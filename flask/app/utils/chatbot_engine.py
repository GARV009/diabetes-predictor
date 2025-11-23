import os
from openai import OpenAI

# Store conversation histories per user (in production, use database)
conversation_histories = {}
# Lazy-loaded OpenAI client
_openai_client = None

def get_openai_client():
    """Lazily initialize and return OpenAI client"""
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

class HealthChatbot:
    def __init__(self):
        self.system_prompt = """You are a knowledgeable and empathetic health assistant specializing in diabetes management and preventive health. You provide evidence-based health advice while always encouraging users to consult with their healthcare providers for medical concerns.

Your expertise includes:
- Diabetes prevention and management
- Personalized diet planning and nutrition advice
- Exercise and fitness recommendations
- Blood sugar management strategies
- Stress management and mental wellness
- Sleep optimization
- Medication adherence support
- Preventive health measures
- Health metrics interpretation (glucose, BMI, blood pressure)

Key principles:
1. Always be empathetic and supportive
2. Provide actionable, practical advice
3. Never diagnose or treat medical conditions
4. Always recommend consulting healthcare providers for serious concerns
5. Use the user's health context when available
6. Encourage healthy habits and positive behavior change
7. Celebrate user progress and achievements
8. Provide evidence-based information
9. Personalize recommendations based on user profile

Conversation style:
- Be conversational and friendly
- Use simple, understandable language
- Break complex information into digestible pieces
- Ask clarifying questions when needed
- Provide specific, measurable recommendations
- Acknowledge user concerns and validate feelings"""
    
    def get_response(self, user_message, user_id=None, user_context=None):
        """Get AI-powered response from OpenAI with conversation history"""
        try:
            # Get lazily-initialized client
            client = get_openai_client()
            
            # Initialize conversation history for user if not exists
            if user_id and user_id not in conversation_histories:
                conversation_histories[user_id] = []
            
            # Build user context string for better personalization
            context_info = ""
            if user_context:
                context_info = f"\n\nUser Health Context:\n"
                if user_context.get('glucose'):
                    context_info += f"- Recent glucose: {user_context['glucose']} mg/dL\n"
                if user_context.get('bmi'):
                    context_info += f"- BMI: {user_context['bmi']}\n"
                if user_context.get('risk_level'):
                    context_info += f"- Diabetes risk: {user_context['risk_level']}\n"
                if user_context.get('age'):
                    context_info += f"- Age: {user_context['age']}\n"
                if user_context.get('recent_activities'):
                    context_info += f"- Recent activities: {', '.join(user_context['recent_activities'])}\n"
            
            # Prepare messages for API
            messages = []
            
            # Add conversation history if exists
            if user_id and user_id in conversation_histories:
                messages.extend(conversation_histories[user_id])
            
            # Add current user message with context
            full_message = user_message + context_info if context_info else user_message
            messages.append({
                "role": "user",
                "content": full_message
            })
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    }
                ] + messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
            )
            
            # Extract response text
            assistant_message = response.choices[0].message.content
            
            # Store conversation history for continuity (keep last 10 exchanges)
            if user_id:
                conversation_histories[user_id].append({
                    "role": "user",
                    "content": user_message
                })
                conversation_histories[user_id].append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # Keep only last 10 exchanges (20 messages) for context
                if len(conversation_histories[user_id]) > 20:
                    conversation_histories[user_id] = conversation_histories[user_id][-20:]
            
            return assistant_message
        
        except Exception as e:
            error_msg = str(e)
            import traceback
            traceback.print_exc()
            if "API key" in error_msg or "authentication" in error_msg.lower() or "OPENAI_API_KEY" in error_msg:
                return "⚠️ Health Assistant is temporarily unavailable. Please check API configuration."
            return f"I apologize, I encountered an issue. Please try again: {error_msg[:100]}"

chatbot = HealthChatbot()

def get_chatbot_response(message, user_id=None, user_context=None):
    """Wrapper function for backward compatibility"""
    return chatbot.get_response(message, user_id, user_context)

def clear_conversation_history(user_id):
    """Clear conversation history for a user"""
    if user_id in conversation_histories:
        del conversation_histories[user_id]
