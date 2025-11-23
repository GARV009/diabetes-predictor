from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.chatbot import chatbot_bp
from app.utils.chatbot_engine import get_chatbot_response, clear_conversation_history
from app.models import db, Gamification, HealthRecord

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
    
    # Get user's latest health record for context
    latest_record = HealthRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthRecord.created_at.desc()).first()
    
    user_context = {}
    if latest_record:
        user_context = {
            'glucose': latest_record.glucose,
            'bmi': latest_record.bmi,
            'risk_level': latest_record.risk_level,
            'age': current_user.age if hasattr(current_user, 'age') else None,
        }
    
    # Get AI-powered response with health context
    bot_response = get_chatbot_response(
        user_message, 
        user_id=current_user.id,
        user_context=user_context
    )
    
    # Award gamification points for AI interaction
    gamification = Gamification.query.filter_by(user_id=current_user.id).first()
    if gamification:
        gamification.chatbot_interactions += 1
        gamification.add_points(5)  # Increased points for AI interactions
        db.session.commit()
    
    return jsonify({
        'message': bot_response,
        'timestamp': 'now'
    })

@chatbot_bp.route('/api/clear-history', methods=['POST'])
@login_required
def clear_history():
    """Clear conversation history for user"""
    clear_conversation_history(current_user.id)
    return jsonify({'success': True, 'message': 'Conversation history cleared'})
