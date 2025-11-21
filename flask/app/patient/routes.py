from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.patient import patient_bp
from app.models import db, User, Appointment
from datetime import datetime

@patient_bp.route('/book-appointment')
@login_required
def book_appointment():
    if current_user.role != 'user':
        flash('Only patients can book appointments', 'error')
        return redirect(url_for('main.dashboard'))
    
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('patient/book_appointment.html', doctors=doctors)

@patient_bp.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment_submit():
    if current_user.role != 'user':
        flash('Only patients can book appointments', 'error')
        return redirect(url_for('main.dashboard'))
    
    doctor_id = request.form.get('doctor_id')
    appointment_date = request.form.get('appointment_date')
    appointment_type = request.form.get('appointment_type', 'telemedicine')
    reason = request.form.get('reason')
    
    try:
        appt_datetime = datetime.fromisoformat(appointment_date)
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=int(doctor_id),
            appointment_date=appt_datetime,
            appointment_type=appointment_type,
            reason=reason
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully! Awaiting doctor confirmation.', 'success')
    except Exception as e:
        flash('Error booking appointment. Please try again.', 'error')
    
    return redirect(url_for('patient.my_appointments'))

@patient_bp.route('/appointments')
@login_required
def my_appointments():
    if current_user.role != 'user':
        flash('Only patients can view appointments', 'error')
        return redirect(url_for('main.dashboard'))
    
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('patient/my_appointments.html', appointments=appointments)
