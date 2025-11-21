from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.doctor import doctor_bp
from app.models import db, User, DoctorNote, Appointment, HealthRecord
from datetime import datetime, timedelta

def doctor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'doctor':
            flash('Access denied. Doctor role required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    patients = db.session.query(User).filter(User.id.in_(
        db.session.query(Appointment.patient_id).filter(Appointment.doctor_id == current_user.id)
    )).all()
    
    upcoming_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='scheduled'
    ).filter(Appointment.appointment_date >= datetime.utcnow()).order_by(
        Appointment.appointment_date
    ).limit(5).all()
    
    total_appointments = Appointment.query.filter_by(doctor_id=current_user.id).count()
    
    return render_template('doctor/dashboard.html', 
                         patients=patients,
                         upcoming_appointments=upcoming_appointments,
                         total_appointments=total_appointments)

@doctor_bp.route('/patients')
@login_required
@doctor_required
def patients():
    patients = db.session.query(User).filter(User.id.in_(
        db.session.query(Appointment.patient_id).filter(Appointment.doctor_id == current_user.id)
    )).all()
    
    return render_template('doctor/patients.html', patients=patients)

@doctor_bp.route('/patient/<int:patient_id>')
@login_required
@doctor_required
def patient_details(patient_id):
    patient = User.query.get_or_404(patient_id)
    
    health_records = HealthRecord.query.filter_by(user_id=patient_id).order_by(
        HealthRecord.created_at.desc()
    ).all()
    
    doctor_notes = DoctorNote.query.filter_by(
        patient_id=patient_id, 
        doctor_id=current_user.id
    ).order_by(DoctorNote.created_at.desc()).all()
    
    return render_template('doctor/patient_details.html',
                         patient=patient,
                         health_records=health_records,
                         doctor_notes=doctor_notes)

@doctor_bp.route('/patient/<int:patient_id>/add-note', methods=['POST'])
@login_required
@doctor_required
def add_note(patient_id):
    patient = User.query.get_or_404(patient_id)
    
    title = request.form.get('title')
    content = request.form.get('content')
    recommendations = request.form.get('recommendations')
    
    note = DoctorNote(
        patient_id=patient_id,
        doctor_id=current_user.id,
        title=title,
        content=content,
        recommendations=recommendations
    )
    
    db.session.add(note)
    db.session.commit()
    
    flash('Note added successfully!', 'success')
    return redirect(url_for('doctor.patient_details', patient_id=patient_id))

@doctor_bp.route('/appointments')
@login_required
@doctor_required
def appointments():
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('doctor/appointments.html', appointments=appointments)

@doctor_bp.route('/appointment/<int:appointment_id>/confirm', methods=['POST'])
@login_required
@doctor_required
def confirm_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    flash('Appointment confirmed!', 'success')
    return redirect(url_for('doctor.appointments'))

@doctor_bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@doctor_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('doctor.appointments'))
