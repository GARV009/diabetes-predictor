from flask import render_template
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import HealthRecord, Gamification
from sqlalchemy import desc

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    recent_records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(desc(HealthRecord.created_at)).limit(5).all()
    
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    
    latest_record = HealthRecord.query.filter_by(user_id=current_user.id).order_by(desc(HealthRecord.created_at)).first()
    
    return render_template('dashboard.html', 
                         recent_records=recent_records,
                         gamification=gamification,
                         latest_record=latest_record)
