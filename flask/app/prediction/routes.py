from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.prediction import prediction_bp
from app.models import db, HealthRecord, Gamification
import numpy as np
import joblib
from app.utils.diet_planner import generate_diet_plan
from app.utils.health_checkup import generate_health_checkup_plan
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
from rl_feedback_system import rl_system

# Load new merged model and scaler
base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(base_path, 'model_merged.pkl')
scaler_path = os.path.join(base_path, 'scaler_merged.pkl')

try:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("✓ Loaded merged model and scaler for probability-based predictions")
except Exception as e:
    print(f"⚠ Could not load merged model: {e}. Falling back to old model.")
    model = joblib.load(os.path.join(base_path, 'model.pkl'))
    scaler = StandardScaler()

@prediction_bp.route('/', methods=['GET'])
@login_required
def prediction_form():
    return render_template('prediction/form.html')

@prediction_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    pregnancies = float(request.form.get('pregnancies', 0))
    glucose = float(request.form.get('glucose'))
    bp_systolic = float(request.form.get('bp_systolic'))
    skin_thickness = float(request.form.get('skin_thickness', 0))
    insulin = float(request.form.get('insulin'))
    bmi = float(request.form.get('bmi'))
    dpf = float(request.form.get('dpf', 0.5))
    age = float(request.form.get('age'))
    bp_diastolic = float(request.form.get('bp_diastolic'))
    family_history = request.form.get('family_history') == 'yes'
    
    # Prepare features for model (all 8 features in correct order)
    # Order: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    float_features = [pregnancies, glucose, bp_systolic, skin_thickness, insulin, bmi, dpf, age]
    final_features = [np.array(float_features)]
    
    # Scale features
    scaled_features = scaler.transform(final_features)
    
    # Get probability-based prediction (0-100%)
    try:
        prediction_proba = model.predict_proba(scaled_features)[0]
        diabetes_probability = float(prediction_proba[1]) * 100  # Convert to Python float, probability of diabetes class
        
        # Apply RL-based adjustment to risk score
        risk_score = float(rl_system.adjust_risk_score(diabetes_probability))
        
        # Convert probability to binary prediction for classification
        pred_value = 1 if risk_score >= 50 else 0
    except Exception as e:
        print(f"Probability prediction error: {e}")
        # Fallback to binary prediction
        prediction = model.predict(scaled_features)
        pred_value = int(prediction[0])
        risk_score = 100.0 if pred_value == 1 else 0.0
    
    # Determine prediction text and risk level
    if pred_value == 1:
        prediction_text = "You have Diabetes, please consult a Doctor."
        risk_level = "High"
    else:
        prediction_text = "You don't have Diabetes."
        risk_level = "Low"
    
    # Create health record with probability-based risk score
    # Convert all values to Python native types (not numpy types)
    health_record = HealthRecord(
        user_id=int(current_user.id),
        glucose=float(glucose),
        insulin=float(insulin),
        bmi=float(bmi),
        age=int(age),
        bp_systolic=float(bp_systolic),
        bp_diastolic=float(bp_diastolic),
        family_history=bool(family_history),
        prediction_result=float(risk_score / 100),  # Store as decimal (0-1)
        risk_level=str(risk_level)
    )
    db.session.add(health_record)
    
    # Record prediction for RL feedback system
    # Convert all values to Python native types for RL system
    prediction_data = rl_system.record_prediction(
        user_id=int(current_user.id),
        prediction_prob=float(risk_score / 100),
        predicted_label=int(pred_value),
        actual_features={
            'glucose': float(glucose),
            'insulin': float(insulin),
            'bmi': float(bmi),
            'age': float(age),
            'bp_systolic': float(bp_systolic),
            'bp_diastolic': float(bp_diastolic)
        }
    )
    
    # Update gamification
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    if gamification:
        gamification.predictions_count += 1
        gamification.update_streak()
        gamification.add_points(20)
        gamification.check_and_award_badges()
    
    db.session.commit()
    
    # Generate personalized plans
    diet_plan = generate_diet_plan(glucose, insulin, bmi, age, pred_value)
    checkup_plan = generate_health_checkup_plan(
        age, bmi, glucose, bp_systolic, bp_diastolic, 
        pred_value, family_history
    )
    
    # Calculate detailed health metrics analysis
    bmi_category = "Underweight" if bmi < 18.5 else "Normal Weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    bmi_status = "✅ Healthy" if bmi < 25 else "⚠️ Needs Attention" if bmi < 30 else "🔴 At Risk"
    
    glucose_category = "Normal" if glucose < 100 else "Prediabetes" if glucose < 126 else "Diabetes"
    glucose_status = "✅ Normal" if glucose < 100 else "⚠️ Prediabetes" if glucose < 126 else "🔴 High"
    
    insulin_status = "✅ Normal" if insulin < 12 else "⚠️ Elevated" if insulin < 20 else "🔴 High"
    
    bp_category = "Normal" if bp_systolic < 120 and bp_diastolic < 80 else "Elevated" if bp_systolic < 130 and bp_diastolic < 80 else "High Stage 1" if bp_systolic < 140 or bp_diastolic < 90 else "High Stage 2"
    bp_status = "✅ Normal" if bp_systolic < 120 else "⚠️ Elevated" if bp_systolic < 140 else "🔴 High"
    
    # Calculate health score (0-100)
    health_score = 0
    glucose = float(glucose)
    bmi = float(bmi)
    insulin = float(insulin)
    bp_systolic = float(bp_systolic)
    if bmi < 25:
        health_score += 25
    elif bmi < 30:
        health_score += 15
    else:
        health_score += 5
    
    if glucose < 100:
        health_score += 25
    elif glucose < 126:
        health_score += 15
    else:
        health_score += 5
    
    if insulin < 12:
        health_score += 20
    elif insulin < 20:
        health_score += 10
    else:
        health_score += 3
    
    if bp_systolic < 120:
        health_score += 30
    elif bp_systolic < 140:
        health_score += 15
    else:
        health_score += 5
    
    health_metrics = {
        'bmi': {
            'value': bmi,
            'category': bmi_category,
            'status': bmi_status,
            'min_healthy': 18.5,
            'max_healthy': 24.9,
            'description': 'Body Mass Index - measures your weight relative to height',
            'recommendation': 'Aim for BMI between 18.5-24.9' if bmi >= 25 else 'Keep up the good work!'
        },
        'glucose': {
            'value': glucose,
            'category': glucose_category,
            'status': glucose_status,
            'normal_range': '70-100',
            'description': 'Blood glucose level - key indicator of diabetes risk',
            'recommendation': 'Values below 100 mg/dL are ideal' if glucose >= 100 else 'Your glucose level is healthy!'
        },
        'insulin': {
            'value': insulin,
            'status': insulin_status,
            'normal_range': '2-12',
            'description': 'Insulin level - hormone that regulates blood sugar',
            'recommendation': 'Normal fasting insulin is below 12 μU/mL' if insulin >= 12 else 'Insulin level is optimal!'
        },
        'blood_pressure': {
            'systolic': bp_systolic,
            'diastolic': bp_diastolic,
            'category': bp_category,
            'status': bp_status,
            'normal_range': '<120/<80',
            'description': 'Blood pressure - force of blood against artery walls',
            'recommendation': 'Maintain below 120/80 mmHg' if bp_systolic >= 120 else 'Your BP is in excellent range!'
        }
    }
    
    return render_template('prediction/results.html',
                         prediction_text=prediction_text,
                         diet_plan=diet_plan,
                         checkup_plan=checkup_plan,
                         health_record=health_record,
                         health_metrics=health_metrics,
                         health_score=health_score,
                         risk_score=risk_score,
                         prediction_data=prediction_data)

@prediction_bp.route('/feedback/<int:record_id>', methods=['POST'])
@login_required
def submit_feedback(record_id):
    """
    Submit feedback on whether prediction was accurate
    Users can report if they got diagnosed or if prediction was wrong
    """
    record = HealthRecord.query.get_or_404(record_id)
    
    if record.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    actual_outcome = request.json.get('actual_outcome')  # 0 or 1
    
    if actual_outcome not in [0, 1]:
        return jsonify({'error': 'Invalid outcome'}), 400
    
    # Get stored prediction data
    prediction_data = {
        'user_id': record.user_id,
        'prediction_prob': float(record.prediction_result),
        'predicted_label': 1 if record.risk_level == 'High' else 0,
        'timestamp': record.created_at.isoformat(),
        'features': {
            'glucose': float(record.glucose),
            'insulin': float(record.insulin),
            'bmi': float(record.bmi),
            'age': float(record.age),
            'bp_systolic': float(record.bp_systolic),
            'bp_diastolic': float(record.bp_diastolic)
        }
    }
    
    # Record feedback in RL system
    rl_system.record_feedback(prediction_data, actual_outcome)
    
    # Get updated stats
    stats = rl_system.get_feedback_stats()
    
    return jsonify({
        'success': True,
        'message': 'Feedback recorded successfully',
        'rl_stats': stats
    })

@prediction_bp.route('/rl-stats', methods=['GET'])
@login_required
def get_rl_stats():
    """Get RL feedback system statistics"""
    stats = rl_system.get_feedback_stats()
    return jsonify(stats)

@prediction_bp.route('/rl-dashboard', methods=['GET'])
@login_required
def rl_dashboard():
    """Display RL model performance dashboard"""
    return render_template('rl_dashboard.html')

@prediction_bp.route('/chart-data/<int:record_id>', methods=['GET'])
@login_required
def get_chart_data(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    
    if record.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Use probability-based risk score (0-100)
    risk_value = record.prediction_result * 100
    
    chart_data = {
        'bmi': {
            'value': record.bmi,
            'category': 'Underweight' if record.bmi < 18.5 else 'Normal' if record.bmi < 25 else 'Overweight' if record.bmi < 30 else 'Obese'
        },
        'glucose': {
            'value': record.glucose,
            'category': 'Normal' if record.glucose < 100 else 'Prediabetes' if record.glucose < 126 else 'Diabetes'
        },
        'risk': {
            'value': risk_value,
            'level': record.risk_level
        }
    }
    
    return jsonify(chart_data)
