from flask import jsonify
from flask_login import login_required, current_user
from app.gamification import gamification_bp
from app.models import Gamification

@gamification_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    
    if not gamification:
        return jsonify({'error': 'Gamification data not found'}), 404
    
    badges = []
    if gamification.badge_first_prediction:
        badges.append({'name': 'First Prediction', 'icon': '🎯', 'description': 'Made your first health prediction'})
    if gamification.badge_week_streak:
        badges.append({'name': '7-Day Streak', 'icon': '🔥', 'description': 'Logged in 7 days in a row'})
    if gamification.badge_health_champion:
        badges.append({'name': 'Health Champion', 'icon': '🏆', 'description': 'Completed 10 health checks'})
    if gamification.badge_diet_master:
        badges.append({'name': 'Diet Master', 'icon': '🥗', 'description': 'Viewed 5 diet plans'})
    if gamification.badge_consistency_king:
        badges.append({'name': 'Consistency King', 'icon': '👑', 'description': 'Maintained 30-day streak'})
    
    stats = {
        'total_points': gamification.total_points,
        'current_streak': gamification.current_streak,
        'longest_streak': gamification.longest_streak,
        'predictions_count': gamification.predictions_count,
        'badges': badges,
        'badges_earned': len(badges),
        'total_badges': 5
    }
    
    return jsonify(stats)
