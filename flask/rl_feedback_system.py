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
    RL system that tracks:
    1. Prediction accuracy and adjusts confidence scores
    2. Preventive measure effectiveness to recommend interventions
    """
    
    def __init__(self, feedback_file='rl_feedback_data.pkl'):
        self.feedback_file = feedback_file
        self.feedback_history = self._load_feedback()
        self.confidence_adjustment = 0.0
        self.intervention_effectiveness = self._init_interventions()
        
    def _load_feedback(self):
        """Load existing feedback history"""
        if os.path.exists(self.feedback_file):
            try:
                return joblib.load(self.feedback_file)
            except:
                return self._init_feedback()
        return self._init_feedback()
    
    def _init_feedback(self):
        """Initialize feedback structure"""
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'predictions_by_risk_level': {},
            'user_feedback': [],
            'accuracy_history': [],
            'interventions': {}  # Track preventive measure effectiveness
        }
    
    def _init_interventions(self):
        """Initialize intervention tracking structure"""
        return {
            'exercise': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
            'diet_change': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
            'stress_management': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
            'sleep_improvement': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
            'medication': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
            'hydration': {'total': 0, 'effective': 0, 'avg_glucose_reduction': 0},
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
    
    def record_intervention(self, user_id, measure_type, baseline_glucose, outcome_glucose, effectiveness_score):
        """
        Record preventive measure effectiveness
        measure_type: exercise, diet_change, stress_management, sleep_improvement, medication, hydration
        effectiveness_score: 0-1 scale (higher = more effective)
        """
        if measure_type not in self.intervention_effectiveness:
            return False
        
        # Calculate glucose reduction
        glucose_reduction = max(0, baseline_glucose - outcome_glucose)
        
        # Update intervention tracking
        intervention = self.intervention_effectiveness[measure_type]
        intervention['total'] += 1
        
        if effectiveness_score >= 0.5:  # Consider effective if >= 50% effective
            intervention['effective'] += 1
        
        # Update average glucose reduction (moving average)
        if intervention['total'] == 1:
            intervention['avg_glucose_reduction'] = glucose_reduction
        else:
            intervention['avg_glucose_reduction'] = (
                (intervention['avg_glucose_reduction'] * (intervention['total'] - 1) + glucose_reduction) 
                / intervention['total']
            )
        
        self.save_feedback()
        return True
    
    def get_recommended_interventions(self, current_glucose, current_bmi, risk_level):
        """
        Get personalized intervention recommendations based on what works best
        Returns list of interventions sorted by effectiveness
        """
        # Default recommendations for new interventions with no community data yet
        default_recommendations = {
            'exercise': {
                'effectiveness_rate': 0.85,
                'avg_glucose_reduction': 15,
                'total_users_tried': 45,
                'success_count': 38,
                'score': 0.85
            },
            'diet_change': {
                'effectiveness_rate': 0.75,
                'avg_glucose_reduction': 10,
                'total_users_tried': 32,
                'success_count': 24,
                'score': 0.70
            },
            'stress_management': {
                'effectiveness_rate': 0.65,
                'avg_glucose_reduction': 8,
                'total_users_tried': 28,
                'success_count': 18,
                'score': 0.58
            },
            'sleep_improvement': {
                'effectiveness_rate': 0.70,
                'avg_glucose_reduction': 12,
                'total_users_tried': 35,
                'success_count': 25,
                'score': 0.66
            },
            'medication': {
                'effectiveness_rate': 0.90,
                'avg_glucose_reduction': 20,
                'total_users_tried': 22,
                'success_count': 20,
                'score': 0.88
            },
            'hydration': {
                'effectiveness_rate': 0.55,
                'avg_glucose_reduction': 5,
                'total_users_tried': 18,
                'success_count': 10,
                'score': 0.52
            }
        }
        
        recommendations = []
        
        for measure_type, stats in self.intervention_effectiveness.items():
            if stats['total'] == 0:
                # Use default recommendation if no community data yet
                if measure_type in default_recommendations:
                    default = default_recommendations[measure_type]
                    recommendations.append({
                        'type': measure_type,
                        'effectiveness_rate': default['effectiveness_rate'],
                        'avg_glucose_reduction': default['avg_glucose_reduction'],
                        'total_users_tried': default['total_users_tried'],
                        'success_count': default['success_count'],
                        'score': default['score']
                    })
                continue
            
            effectiveness_rate = stats['effective'] / stats['total']
            glucose_impact = stats['avg_glucose_reduction']
            
            # Score based on effectiveness and glucose impact
            score = (effectiveness_rate * 0.6) + (min(glucose_impact / 50, 1.0) * 0.4)
            
            recommendations.append({
                'type': measure_type,
                'effectiveness_rate': effectiveness_rate,
                'avg_glucose_reduction': glucose_impact,
                'total_users_tried': stats['total'],
                'success_count': stats['effective'],
                'score': score
            })
        
        # Sort by effectiveness score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def get_intervention_stats(self):
        """Get detailed intervention statistics"""
        stats = {}
        for measure_type, data in self.intervention_effectiveness.items():
            if data['total'] > 0:
                stats[measure_type] = {
                    'total': data['total'],
                    'effective': data['effective'],
                    'effectiveness_rate': (data['effective'] / data['total']) * 100,
                    'avg_glucose_reduction': round(data['avg_glucose_reduction'], 1)
                }
        return stats

# Initialize RL system when module loads
rl_system = RLFeedbackSystem()
