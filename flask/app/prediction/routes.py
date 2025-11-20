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
    
    return render_template('prediction/results.html',
                         prediction_text=prediction_text,
                         diet_plan=diet_plan,
                         checkup_plan=checkup_plan,
                         health_record=health_record)

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
