from flask import jsonify, render_template
from flask_login import login_required, current_user
from app.gamification import gamification_bp
from app.models import Gamification, User, db
from sqlalchemy import desc

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

@gamification_bp.route('/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    top_users = db.session.query(User, Gamification).join(
        Gamification, User.id == Gamification.user_id
    ).order_by(
        desc(Gamification.total_points),
        desc(Gamification.current_streak)
    ).limit(10).all()
    
    leaderboard_data = []
    for idx, (user, gamification) in enumerate(top_users, 1):
        badges_count = sum([
            gamification.badge_first_prediction,
            gamification.badge_week_streak,
            gamification.badge_health_champion,
            gamification.badge_diet_master,
            gamification.badge_consistency_king
        ])
        
        is_current_user = user.id == current_user.id
        
        leaderboard_data.append({
            'rank': idx,
            'username': user.username,
            'points': gamification.total_points,
            'streak': gamification.current_streak,
            'longest_streak': gamification.longest_streak,
            'badges': badges_count,
            'total_badges': 5,
            'is_current_user': is_current_user,
            'medal': '🥇' if idx == 1 else '🥈' if idx == 2 else '🥉' if idx == 3 else f'{idx}️⃣'
        })
    
    current_user_rank = None
    all_users = db.session.query(User, Gamification).join(
        Gamification, User.id == Gamification.user_id
    ).order_by(
        desc(Gamification.total_points),
        desc(Gamification.current_streak)
    ).all()
    
    for idx, (user, gamification) in enumerate(all_users, 1):
        if user.id == current_user.id:
            current_user_rank = idx
            break
    
    return render_template('gamification/leaderboard.html', 
                         leaderboard=leaderboard_data,
                         current_user_rank=current_user_rank,
                         total_users=len(all_users))
