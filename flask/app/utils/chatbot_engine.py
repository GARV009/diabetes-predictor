import random

class HealthChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your health assistant. How can I help you today?",
                "Hi there! I'm here to help with your health questions.",
                "Welcome! Ask me anything about diabetes, diet, or healthy living."
            ],
            'diet': {
                'keywords': ['diet', 'food', 'eat', 'meal', 'nutrition', 'calorie'],
                'responses': [
                    "A balanced diet is key to managing diabetes. Focus on:\n• Complex carbohydrates (whole grains, vegetables)\n• Lean proteins (fish, chicken, legumes)\n• Healthy fats (nuts, avocado, olive oil)\n• Limit sugary foods and refined carbs",
                    "For diabetes management, consider:\n• Eating at regular intervals\n• Portion control\n• High-fiber foods\n• Avoiding sugary drinks\n• Choosing foods with low glycemic index",
                    "Meal planning tips:\n• Include vegetables in every meal\n• Choose whole grains over refined\n• Have protein with each meal\n• Snack on nuts, not chips\n• Stay hydrated with water"
                ]
            },
            'glucose': {
                'keywords': ['glucose', 'blood sugar', 'sugar level', 'a1c', 'glycemic'],
                'responses': [
                    "Blood sugar management is crucial. Here's what helps:\n• Regular monitoring\n• Consistent meal timing\n• Physical activity\n• Medication as prescribed\n• Stress management\n\nTarget fasting glucose: 80-130 mg/dL",
                    "To maintain healthy blood sugar:\n• Avoid skipping meals\n• Choose low glycemic index foods\n• Exercise regularly (30 min/day)\n• Get adequate sleep (7-8 hours)\n• Monitor levels as recommended by your doctor",
                    "High blood sugar can be managed by:\n• Drinking water\n• Light physical activity\n• Avoiding simple carbs\n• Taking prescribed medication\n• Consulting your doctor if persistently high"
                ]
            },
            'exercise': {
                'keywords': ['exercise', 'workout', 'physical activity', 'fitness', 'gym', 'walk'],
                'responses': [
                    "Exercise is great for diabetes management!\n• Aim for 150 minutes/week of moderate activity\n• Mix cardio and strength training\n• Start slowly if you're new\n• Check blood sugar before/after exercise\n• Stay hydrated",
                    "Best exercises for diabetes:\n• Brisk walking\n• Swimming\n• Cycling\n• Yoga\n• Strength training\n\nRemember: Even 10 minutes counts!",
                    "Exercise tips for diabetics:\n• Exercise at the same time daily\n• Carry a quick sugar source\n• Wear proper footwear\n• Monitor for hypoglycemia\n• Stay consistent"
                ]
            },
            'stress': {
                'keywords': ['stress', 'anxiety', 'worry', 'tension', 'relax'],
                'responses': [
                    "Stress can affect blood sugar. Try these:\n• Deep breathing exercises\n• Meditation (10 min/day)\n• Regular sleep schedule\n• Connect with friends/family\n• Engage in hobbies\n• Consider professional support if needed",
                    "Managing stress helps diabetes control:\n• Practice mindfulness\n• Do gentle yoga\n• Take short breaks during work\n• Avoid caffeine overload\n• Spend time in nature",
                    "Stress reduction techniques:\n• Progressive muscle relaxation\n• Guided imagery\n• Journaling\n• Listening to calming music\n• Regular exercise\n• Adequate sleep"
                ]
            },
            'sleep': {
                'keywords': ['sleep', 'rest', 'tired', 'fatigue', 'insomnia'],
                'responses': [
                    "Quality sleep is essential for diabetes management:\n• Aim for 7-9 hours nightly\n• Keep a consistent sleep schedule\n• Avoid screens 1 hour before bed\n• Keep bedroom cool and dark\n• Avoid large meals before bedtime",
                    "Better sleep improves blood sugar control:\n• Establish a bedtime routine\n• Limit caffeine after 2 PM\n• Avoid alcohol before bed\n• Exercise during the day\n• Manage stress\n• Check with doctor if you have sleep apnea",
                    "Sleep hygiene tips:\n• Same bedtime every night\n• Comfortable mattress/pillow\n• No TV in bedroom\n• Light reading before sleep\n• Avoid daytime naps if possible\n• Relaxation techniques before bed"
                ]
            },
            'medication': {
                'keywords': ['medication', 'medicine', 'insulin', 'drug', 'pill', 'prescription'],
                'responses': [
                    "Medication management tips:\n• Take medications as prescribed\n• Don't skip doses\n• Store insulin properly (if applicable)\n• Set reminders if needed\n• Discuss side effects with your doctor\n• Never adjust dosage without medical advice",
                    "Important medication reminders:\n• Take at the same time daily\n• Know your medications' names and purposes\n• Keep a medication list\n• Refill before running out\n• Inform all healthcare providers\n• Report any adverse reactions",
                    "For insulin users:\n• Rotate injection sites\n• Check expiration dates\n• Store at proper temperature\n• Know signs of hypoglycemia\n• Carry glucose tablets\n• Wear medical ID"
                ]
            },
            'symptoms': {
                'keywords': ['symptom', 'feel', 'sick', 'pain', 'dizzy', 'thirsty'],
                'responses': [
                    "Common diabetes symptoms to watch:\n• Increased thirst\n• Frequent urination\n• Fatigue\n• Blurred vision\n• Slow healing wounds\n\n⚠️ If symptoms worsen, contact your doctor immediately.",
                    "Warning signs requiring medical attention:\n• Very high/low blood sugar\n• Persistent nausea/vomiting\n• Difficulty breathing\n• Confusion or disorientation\n• Chest pain\n\nDon't wait - seek medical help!",
                    "Track your symptoms:\n• Keep a health journal\n• Monitor blood sugar regularly\n• Note patterns\n• Share with your doctor\n• Don't ignore warning signs"
                ]
            },
            'general': {
                'keywords': ['help', 'info', 'tell me', 'what', 'how'],
                'responses': [
                    "I can help you with:\n• Diet and nutrition advice\n• Exercise recommendations\n• Blood sugar management\n• Stress reduction\n• Sleep tips\n• Medication reminders\n\nWhat would you like to know more about?",
                    "Managing diabetes involves:\n• Healthy eating\n• Regular physical activity\n• Monitoring blood sugar\n• Taking medications as prescribed\n• Managing stress\n• Regular checkups\n\nWhich area interests you?",
                    "Living well with diabetes:\n• Stay informed\n• Follow your treatment plan\n• Build healthy habits\n• Stay connected with healthcare team\n• Don't hesitate to ask questions\n\nHow can I help you today?"
                ]
            }
        }
    
    def get_response(self, user_message):
        message_lower = user_message.lower()
        
        greetings = ['hi', 'hello', 'hey', 'greetings']
        if any(word in message_lower.split() for word in greetings):
            return random.choice(self.responses['greeting'])
        
        for category, data in self.responses.items():
            if category == 'greeting':
                continue
            
            if isinstance(data, dict) and 'keywords' in data:
                if any(keyword in message_lower for keyword in data['keywords']):
                    return random.choice(data['responses'])
        
        return random.choice(self.responses['general']['responses'])

chatbot = HealthChatbot()

def get_chatbot_response(message):
    return chatbot.get_response(message)
