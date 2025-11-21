from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    health_records = db.relationship('HealthRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    gamification = db.relationship('Gamification', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor_notes_written = db.relationship('DoctorNote', backref='doctor', lazy=True, foreign_keys='DoctorNote.doctor_id')
    appointments_as_doctor = db.relationship('Appointment', backref='doctor', lazy=True, foreign_keys='Appointment.doctor_id')
    appointments_as_patient = db.relationship('Appointment', backref='patient', lazy=True, foreign_keys='Appointment.patient_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    glucose = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bp_systolic = db.Column(db.Integer, nullable=False)
    bp_diastolic = db.Column(db.Integer, nullable=False)
    family_history = db.Column(db.Boolean, default=False)
    
    prediction_result = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HealthRecord {self.id} - User {self.user_id}>'


class Gamification(db.Model):
    __tablename__ = 'gamification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    total_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    predictions_count = db.Column(db.Integer, default=0)
    checkups_completed = db.Column(db.Integer, default=0)
    diet_plans_viewed = db.Column(db.Integer, default=0)
    chatbot_interactions = db.Column(db.Integer, default=0)
    
    badge_first_prediction = db.Column(db.Boolean, default=False)
    badge_week_streak = db.Column(db.Boolean, default=False)
    badge_health_champion = db.Column(db.Boolean, default=False)
    badge_diet_master = db.Column(db.Boolean, default=False)
    badge_consistency_king = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def add_points(self, points):
        self.total_points += points
    
    def update_streak(self):
        from datetime import date
        today = date.today()
        
        if self.last_activity_date is None:
            self.current_streak = 1
            self.last_activity_date = today
        else:
            days_diff = (today - self.last_activity_date).days
            
            if days_diff == 0:
                pass
            elif days_diff == 1:
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                self.last_activity_date = today
            else:
                self.current_streak = 1
                self.last_activity_date = today
        
        if self.current_streak >= 7 and not self.badge_week_streak:
            self.badge_week_streak = True
        
        if self.current_streak >= 30 and not self.badge_consistency_king:
            self.badge_consistency_king = True
    
    def check_and_award_badges(self):
        if self.predictions_count >= 1 and not self.badge_first_prediction:
            self.badge_first_prediction = True
        
        if self.predictions_count >= 10 and not self.badge_health_champion:
            self.badge_health_champion = True
        
        if self.diet_plans_viewed >= 5 and not self.badge_diet_master:
            self.badge_diet_master = True
    
    def __repr__(self):
        return f'<Gamification User {self.user_id} - {self.total_points} points>'


class DoctorNote(db.Model):
    __tablename__ = 'doctor_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DoctorNote {self.id} - Patient {self.patient_id}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    appointment_type = db.Column(db.String(50), default='telemedicine')
    status = db.Column(db.String(20), default='scheduled')
    
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id}>'
