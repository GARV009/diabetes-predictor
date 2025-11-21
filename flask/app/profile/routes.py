from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.profile import profile_bp
from app.models import db, User, HealthRecord, Gamification
from werkzeug.security import check_password_hash
from app.utils.report_generator import create_health_report_pdf
from datetime import datetime

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_email':
            new_email = request.form.get('email')
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Email already in use', 'error')
                else:
                    current_user.email = new_email
                    db.session.commit()
                    flash('Email updated successfully', 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect', 'error')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters', 'error')
            elif new_password != confirm_password:
                flash('Passwords do not match', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('profile.settings'))
    
    return render_template('profile/settings.html')

@profile_bp.route('/health-stats', methods=['GET'])
@login_required
def health_stats():
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at.asc()).all()
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    
    avg_glucose = None
    avg_bmi = None
    avg_insulin = None
    avg_bp_systolic = None
    avg_bp_diastolic = None
    high_risk_count = 0
    low_risk_count = 0
    
    min_glucose = None
    max_glucose = None
    min_bmi = None
    max_bmi = None
    
    if records:
        glucoses = [r.glucose for r in records]
        bmis = [r.bmi for r in records]
        insulins = [r.insulin for r in records]
        bp_systolics = [r.bp_systolic for r in records]
        bp_diastolics = [r.bp_diastolic for r in records]
        
        avg_glucose = sum(glucoses) / len(glucoses)
        avg_bmi = sum(bmis) / len(bmis)
        avg_insulin = sum(insulins) / len(insulins)
        avg_bp_systolic = sum(bp_systolics) / len(bp_systolics)
        avg_bp_diastolic = sum(bp_diastolics) / len(bp_diastolics)
        
        min_glucose = min(glucoses)
        max_glucose = max(glucoses)
        min_bmi = min(bmis)
        max_bmi = max(bmis)
        
        high_risk_count = sum(1 for r in records if r.risk_level == 'High')
        low_risk_count = sum(1 for r in records if r.risk_level == 'Low')
    
    # Prepare chart data
    chart_labels = [r.created_at.strftime('%b %d') for r in records]
    glucose_data = [r.glucose for r in records]
    bmi_data = [r.bmi for r in records]
    insulin_data = [r.insulin for r in records]
    bp_systolic_data = [r.bp_systolic for r in records]
    bp_diastolic_data = [r.bp_diastolic for r in records]
    
    risk_distribution = {
        'High': high_risk_count,
        'Low': low_risk_count
    }
    
    return render_template('profile/health_stats.html',
                         records=records,
                         gamification=gamification,
                         avg_glucose=avg_glucose,
                         avg_bmi=avg_bmi,
                         avg_insulin=avg_insulin,
                         avg_bp_systolic=avg_bp_systolic,
                         avg_bp_diastolic=avg_bp_diastolic,
                         min_glucose=min_glucose,
                         max_glucose=max_glucose,
                         min_bmi=min_bmi,
                         max_bmi=max_bmi,
                         high_risk_count=high_risk_count,
                         low_risk_count=low_risk_count,
                         chart_labels=chart_labels,
                         glucose_data=glucose_data,
                         bmi_data=bmi_data,
                         insulin_data=insulin_data,
                         bp_systolic_data=bp_systolic_data,
                         bp_diastolic_data=bp_diastolic_data,
                         risk_distribution=risk_distribution)

@profile_bp.route('/download-report', methods=['GET'])
@login_required
def download_report():
    """Generate and download PDF health report"""
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at.desc()).all()
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    
    if not records:
        flash('No health records to generate report', 'error')
        return redirect(url_for('profile.health_stats'))
    
    # Generate PDF
    pdf_buffer = create_health_report_pdf(current_user, records, gamification)
    
    # Create filename with timestamp
    filename = f"Health_Report_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
