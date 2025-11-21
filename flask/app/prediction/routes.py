from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.prediction import prediction_bp
from app.models import db, HealthRecord, Gamification
import numpy as np
import joblib
from app.utils.diet_planner import generate_diet_plan
from app.utils.health_checkup import generate_health_checkup_plan
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import os

model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'model.pkl')
dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'diabetes.csv')

model = joblib.load(model_path)
dataset = pd.read_csv(dataset_path)
dataset_X = dataset.iloc[:,[1, 2, 5, 7]].values
sc = MinMaxScaler(feature_range = (0,1))
dataset_scaled = sc.fit_transform(dataset_X)

@prediction_bp.route('/', methods=['GET'])
@login_required
def prediction_form():
    return render_template('prediction/form.html')

@prediction_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    glucose = float(request.form.get('glucose'))
    insulin = float(request.form.get('insulin'))
    bmi = float(request.form.get('bmi'))
    age = float(request.form.get('age'))
    bp_systolic = float(request.form.get('bp_systolic'))
    bp_diastolic = float(request.form.get('bp_diastolic'))
    family_history = request.form.get('family_history') == 'yes'
    
    float_features = [glucose, insulin, bmi, age]
    final_features = [np.array(float_features)]
    prediction = model.predict(sc.transform(final_features))
    
    pred_value = int(prediction[0])
    
    if pred_value == 1:
        prediction_text = "You have Diabetes, please consult a Doctor."
        risk_level = "High"
    else:
        prediction_text = "You don't have Diabetes."
        risk_level = "Low"
    
    health_record = HealthRecord(
        user_id=current_user.id,
        glucose=glucose,
        insulin=insulin,
        bmi=bmi,
        age=age,
        bp_systolic=bp_systolic,
        bp_diastolic=bp_diastolic,
        family_history=family_history,
        prediction_result=pred_value,
        risk_level=risk_level
    )
    db.session.add(health_record)
    
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    if gamification:
        gamification.predictions_count += 1
        gamification.update_streak()
        gamification.add_points(20)
        gamification.check_and_award_badges()
    
    db.session.commit()
    
    diet_plan = generate_diet_plan(glucose, insulin, bmi, age, pred_value)
    checkup_plan = generate_health_checkup_plan(
        age, bmi, glucose, bp_systolic, bp_diastolic, 
        pred_value, family_history
    )
    
    # Calculate health metrics analysis
    bmi_category = "Underweight" if bmi < 18.5 else "Normal Weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    bmi_status = "✅ Healthy" if bmi < 25 else "⚠️ Needs Attention" if bmi < 30 else "🔴 At Risk"
    
    glucose_category = "Normal" if glucose < 100 else "Prediabetes" if glucose < 126 else "Diabetes"
    glucose_status = "✅ Normal" if glucose < 100 else "⚠️ Prediabetes" if glucose < 126 else "🔴 High"
    
    insulin_status = "✅ Normal" if insulin < 12 else "⚠️ Elevated" if insulin < 20 else "🔴 High"
    
    bp_category = "Normal" if bp_systolic < 120 and bp_diastolic < 80 else "Elevated" if bp_systolic < 130 and bp_diastolic < 80 else "High Stage 1" if bp_systolic < 140 or bp_diastolic < 90 else "High Stage 2"
    bp_status = "✅ Normal" if bp_systolic < 120 else "⚠️ Elevated" if bp_systolic < 140 else "🔴 High"
    
    health_score = 0
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
                         health_score=health_score)

@prediction_bp.route('/chart-data/<int:record_id>', methods=['GET'])
@login_required
def get_chart_data(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    
    if record.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
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
            'value': record.prediction_result * 100,
            'level': record.risk_level
        }
    }
    
    return jsonify(chart_data)
