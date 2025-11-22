from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import PreventiveMeasure, HealthRecord
from app.prevention import prevention_bp
from rl_feedback_system import rl_system
from datetime import datetime, timedelta

@prevention_bp.route('/')
@login_required
def prevention_dashboard():
    """View user's preventive measures and RL recommendations"""
    # Get user's active preventive measures
    active_measures = PreventiveMeasure.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).order_by(PreventiveMeasure.start_date.desc()).all()
    
    # Get completed measures
    completed_measures = PreventiveMeasure.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(PreventiveMeasure.updated_at.desc()).limit(10).all()
    
    # Get user's latest health record
    latest_record = HealthRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthRecord.created_at.desc()).first()
    
    # Get RL-based intervention recommendations
    recommendations = []
    if latest_record:
        recommendations = rl_system.get_recommended_interventions(
            latest_record.glucose,
            latest_record.bmi,
            latest_record.risk_level
        )
    
    # Get intervention statistics from RL system
    intervention_stats = rl_system.get_intervention_stats()
    
    return render_template('prevention/dashboard.html',
                         active_measures=active_measures,
                         completed_measures=completed_measures,
                         latest_record=latest_record,
                         recommendations=recommendations,
                         intervention_stats=intervention_stats)

@prevention_bp.route('/start', methods=['POST'])
@login_required
def start_measure():
    """Start a new preventive measure"""
    data = request.get_json()
    measure_type = data.get('measure_type')
    description = data.get('description')
    
    if not measure_type or not description:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get latest health metrics as baseline
    latest_record = HealthRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthRecord.created_at.desc()).first()
    
    measure = PreventiveMeasure(
        user_id=current_user.id,
        measure_type=measure_type,
        measure_description=description,
        baseline_glucose=latest_record.glucose if latest_record else None,
        baseline_bmi=latest_record.bmi if latest_record else None,
        baseline_bp_systolic=latest_record.bp_systolic if latest_record else None,
        status='active'
    )
    
    db.session.add(measure)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Started: {description}',
        'measure_id': measure.id
    })

@prevention_bp.route('/update/<int:measure_id>', methods=['POST'])
@login_required
def update_measure(measure_id):
    """Update measure with outcome metrics"""
    measure = PreventiveMeasure.query.get(measure_id)
    
    if not measure or measure.user_id != current_user.id:
        return jsonify({'error': 'Measure not found'}), 404
    
    data = request.get_json()
    status = data.get('status')
    rating = data.get('rating')  # 1-5 user feedback
    
    if status:
        measure.status = status
    
    if rating:
        measure.user_rating = rating
    
    # Get latest health record for outcome metrics
    latest_record = HealthRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthRecord.created_at.desc()).first()
    
    if latest_record:
        measure.outcome_glucose = latest_record.glucose
        measure.outcome_bmi = latest_record.bmi
        measure.outcome_bp_systolic = latest_record.bp_systolic
        
        # Calculate effectiveness
        if measure.baseline_glucose and latest_record.glucose:
            glucose_improvement = max(0, measure.baseline_glucose - latest_record.glucose)
            # Effectiveness: 0-1 scale (0% improvement = 0.0, 10+ mg/dL improvement = 1.0)
            effectiveness = min(glucose_improvement / 20, 1.0)
            measure.effectiveness_score = effectiveness
            
            # Record to RL system for learning
            rl_system.record_intervention(
                user_id=current_user.id,
                measure_type=measure.measure_type,
                baseline_glucose=measure.baseline_glucose,
                outcome_glucose=latest_record.glucose,
                effectiveness_score=effectiveness
            )
    
    if status == 'completed':
        measure.end_date = datetime.utcnow()
    
    measure.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Measure updated',
        'effectiveness_score': measure.effectiveness_score
    })

@prevention_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get RL-based intervention recommendations"""
    latest_record = HealthRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthRecord.created_at.desc()).first()
    
    if not latest_record:
        return jsonify({'error': 'No health records found'}), 404
    
    recommendations = rl_system.get_recommended_interventions(
        latest_record.glucose,
        latest_record.bmi,
        latest_record.risk_level
    )
    
    # Format for display
    formatted = []
    for rec in recommendations:
        formatted.append({
            'type': rec['type'],
            'effectiveness': f"{rec['effectiveness_rate']*100:.0f}%",
            'avg_glucose_reduction': f"{rec['avg_glucose_reduction']:.0f} mg/dL",
            'users_tried': rec['total_users_tried'],
            'successful': rec['success_count'],
            'score': rec['score']
        })
    
    return jsonify(formatted)

@prevention_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user's preventive measure statistics"""
    measures = PreventiveMeasure.query.filter_by(user_id=current_user.id).all()
    
    stats = {
        'total_measures': len(measures),
        'active': len([m for m in measures if m.status == 'active']),
        'completed': len([m for m in measures if m.status == 'completed']),
        'avg_effectiveness': 0
    }
    
    completed = [m for m in measures if m.status == 'completed' and m.effectiveness_score]
    if completed:
        stats['avg_effectiveness'] = sum(m.effectiveness_score for m in completed) / len(completed)
    
    return jsonify(stats)
