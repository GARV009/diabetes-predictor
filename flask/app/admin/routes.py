from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import db, User, HealthRecord, Gamification
from sqlalchemy import func

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admin role required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    health_records = HealthRecord.query.all()
    
    avg_glucose = db.session.query(func.avg(HealthRecord.glucose)).scalar() or 0
    avg_bmi = db.session.query(func.avg(HealthRecord.bmi)).scalar() or 0
    
    low_risk = HealthRecord.query.filter_by(risk_level='Low').count()
    high_risk = HealthRecord.query.filter_by(risk_level='High').count()
    
    top_performers = db.session.query(User, Gamification).join(
        Gamification, User.id == Gamification.user_id
    ).filter(User.role == 'user').order_by(
        Gamification.total_points.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_doctors=total_doctors,
                         total_admins=total_admins,
                         total_records=len(health_records),
                         avg_glucose=round(avg_glucose, 2),
                         avg_bmi=round(avg_bmi, 2),
                         low_risk=low_risk,
                         high_risk=high_risk,
                         top_performers=top_performers)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    health_records = HealthRecord.query.all()
    users = User.query.filter_by(role='user').all()
    
    glucose_rows = db.session.query(
        HealthRecord.glucose,
        func.count(HealthRecord.id)
    ).group_by(HealthRecord.glucose).all()
    
    bmi_rows = db.session.query(
        HealthRecord.bmi,
        func.count(HealthRecord.id)
    ).group_by(HealthRecord.bmi).all()
    
    # Convert SQLAlchemy Row objects to JSON-serializable lists
    glucose_data = [[float(row[0]), int(row[1])] for row in glucose_rows]
    bmi_data = [[float(row[0]), int(row[1])] for row in bmi_rows]
    
    return render_template('admin/reports.html',
                         total_records=len(health_records),
                         total_users=len(users),
                         glucose_data=glucose_data,
                         bmi_data=bmi_data)

@admin_bp.route('/rl-model-dashboard')
@login_required
@admin_required
def rl_model_dashboard():
    """Display RL model performance dashboard for admins"""
    return render_template('rl_dashboard.html')
