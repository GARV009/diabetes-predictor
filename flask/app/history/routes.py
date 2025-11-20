from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.history import history_bp
from app.models import HealthRecord
from sqlalchemy import desc

@history_bp.route('/')
@login_required
def view_history():
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(desc(HealthRecord.created_at)).limit(10).all()
    return render_template('history/view.html', records=records)

@history_bp.route('/api/trend-data', methods=['GET'])
@login_required
def get_trend_data():
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at).limit(30).all()
    
    dates = [record.created_at.strftime('%Y-%m-%d') for record in records]
    glucose_values = [record.glucose for record in records]
    bmi_values = [record.bmi for record in records]
    
    trend_data = {
        'dates': dates,
        'glucose': glucose_values,
        'bmi': bmi_values
    }
    
    return jsonify(trend_data)
