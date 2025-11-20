from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.chatbot import chatbot_bp
from app.utils.chatbot_engine import get_chatbot_response
from app.models import db, Gamification

@chatbot_bp.route('/')
@login_required
def chat_page():
    return render_template('chatbot/chat.html')

@chatbot_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    bot_response = get_chatbot_response(user_message)
    
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    if gamification:
        gamification.chatbot_interactions += 1
        gamification.add_points(2)
        db.session.commit()
    
    return jsonify({
        'message': bot_response,
        'timestamp': 'now'
    })
