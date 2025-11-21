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
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at.desc()).all()
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    
    avg_glucose = None
    avg_bmi = None
    high_risk_count = 0
    
    if records:
        avg_glucose = sum(r.glucose for r in records) / len(records)
        avg_bmi = sum(r.bmi for r in records) / len(records)
        high_risk_count = sum(1 for r in records if r.risk_level == 'High')
    
    return render_template('profile/health_stats.html',
                         records=records,
                         gamification=gamification,
                         avg_glucose=avg_glucose,
                         avg_bmi=avg_bmi,
                         high_risk_count=high_risk_count)

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
