"""
Reinforcement Learning Feedback System for Diabetes Prediction
Learns from user health outcomes to improve future predictions
"""

import joblib
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path

class RLFeedbackSystem:
    """
    Simple RL system that tracks prediction accuracy and adjusts confidence scores
    based on actual health outcomes reported by users
    """
    
    def __init__(self, feedback_file='rl_feedback_data.pkl'):
        self.feedback_file = feedback_file
        self.feedback_history = self._load_feedback()
        self.confidence_adjustment = 0.0
        
    def _load_feedback(self):
        """Load existing feedback history"""
        if os.path.exists(self.feedback_file):
            try:
                return joblib.load(self.feedback_file)
            except:
                return {
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'predictions_by_risk_level': {},
                    'user_feedback': [],
                    'accuracy_history': []
                }
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'predictions_by_risk_level': {},
            'user_feedback': [],
            'accuracy_history': []
        }
    
    def save_feedback(self):
        """Save feedback history to disk"""
        joblib.dump(self.feedback_history, self.feedback_file)
    
    def record_prediction(self, user_id, prediction_prob, predicted_label, actual_features):
        """Record a prediction for later feedback"""
        return {
            'user_id': user_id,
            'prediction_prob': float(prediction_prob),
            'predicted_label': int(predicted_label),
            'timestamp': datetime.now().isoformat(),
            'features': {k: float(v) for k, v in actual_features.items()}
        }
    
    def record_feedback(self, prediction_data, actual_outcome):
        """
        Record user feedback on whether prediction was correct
        actual_outcome: 1 if user confirmed diabetes, 0 if not
        """
        self.feedback_history['total_predictions'] += 1
        self.feedback_history['user_feedback'].append({
            'prediction_data': prediction_data,
            'actual_outcome': int(actual_outcome),
            'feedback_timestamp': datetime.now().isoformat()
        })
        
        # Check if prediction was correct
        if prediction_data['predicted_label'] == actual_outcome:
            self.feedback_history['correct_predictions'] += 1
        
        # Track accuracy
        if self.feedback_history['total_predictions'] % 5 == 0:  # Every 5 predictions
            accuracy = self.feedback_history['correct_predictions'] / self.feedback_history['total_predictions']
            self.feedback_history['accuracy_history'].append({
                'timestamp': datetime.now().isoformat(),
                'accuracy': accuracy,
                'total_predictions': self.feedback_history['total_predictions']
            })
        
        self.save_feedback()
    
    def get_confidence_adjustment(self):
        """
        Calculate confidence adjustment based on historical accuracy
        Returns: adjustment factor between 0.8 and 1.2
        """
        if self.feedback_history['total_predictions'] == 0:
            return 1.0
        
        accuracy = self.feedback_history['correct_predictions'] / self.feedback_history['total_predictions']
        
        # If accuracy is high, increase confidence in predictions
        # If accuracy is low, decrease confidence
        # Scale from 0.8x to 1.2x based on accuracy
        adjustment = 0.8 + (accuracy * 0.4)
        return adjustment
    
    def adjust_risk_score(self, risk_score):
        """Apply RL-based adjustment to risk score"""
        adjustment = self.get_confidence_adjustment()
        
        # Apply adjustment but keep score within 0-100 range
        adjusted_score = risk_score * adjustment
        return min(100, max(0, adjusted_score))
    
    def get_feedback_stats(self):
        """Get statistics about the feedback system"""
        total = self.feedback_history['total_predictions']
        correct = self.feedback_history['correct_predictions']
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0,
            'confidence_adjustment': self.get_confidence_adjustment(),
            'recent_accuracy_history': self.feedback_history['accuracy_history'][-5:] if self.feedback_history['accuracy_history'] else []
        }

# Initialize RL system when module loads
rl_system = RLFeedbackSystem()
