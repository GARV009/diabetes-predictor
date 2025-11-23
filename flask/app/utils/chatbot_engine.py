import random

conversation_histories = {}

class HealthChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your health assistant. How can I help you today?",
                "Hi there! I'm here to help with your health questions.",
                "Welcome! Ask me anything about diabetes, diet, exercise, or healthy living.",
                "Good to see you! What health topic can I help you with?"
            ],
            'diet': {
                'keywords': ['diet', 'food', 'eat', 'meal', 'nutrition', 'calorie', 'recipe', 'breakfast', 'lunch', 'dinner', 'snack'],
                'responses': [
                    "A balanced diet is key to managing diabetes. Focus on:\n• Complex carbohydrates (whole grains, vegetables)\n• Lean proteins (fish, chicken, legumes)\n• Healthy fats (nuts, avocado, olive oil)\n• Limit sugary foods and refined carbs",
                    "For diabetes management, consider:\n• Eating at regular intervals (3 meals + 2 snacks)\n• Portion control using the plate method\n• High-fiber foods (aim for 25-30g daily)\n• Avoiding sugary drinks and processed foods\n• Choosing foods with low glycemic index",
                    "Meal planning tips:\n• Include vegetables in every meal (half your plate)\n• Choose whole grains over refined carbs\n• Have protein with each meal for satiety\n• Snack on nuts, seeds, or Greek yogurt\n• Stay hydrated with water\n• Prep meals ahead for consistency",
                    "Best foods for diabetes:\n✓ Leafy greens (spinach, kale, lettuce)\n✓ Non-starchy vegetables (broccoli, peppers, cauliflower)\n✓ Legumes (beans, lentils, chickpeas)\n✓ Whole grains (oats, brown rice, quinoa)\n✓ Fish (salmon, mackerel - omega-3 rich)\n✓ Nuts and seeds",
                    "Foods to limit:\n✗ Sugary beverages (soda, juice)\n✗ Refined carbs (white bread, pasta)\n✗ Fried foods\n✗ Processed snacks\n✗ Added sugars and desserts\n✗ High-sodium foods"
                ]
            },
            'glucose': {
                'keywords': ['glucose', 'blood sugar', 'sugar level', 'a1c', 'glycemic', 'hyperglycemia', 'hypoglycemia'],
                'responses': [
                    "Blood sugar management is crucial:\n• Regular monitoring (fasting: 80-130 mg/dL)\n• Consistent meal timing (every 4-5 hours)\n• Physical activity (30 min/day)\n• Medication as prescribed\n• Stress management\n• Quality sleep (7-9 hours)",
                    "To maintain healthy blood sugar:\n• Never skip meals\n• Combine carbs with protein/fat for slower absorption\n• Exercise regularly (cardio + strength)\n• Get adequate sleep and manage stress\n• Monitor levels as recommended by your doctor\n• Keep a food journal to track patterns",
                    "Managing high blood sugar:\n• Drink water to help flush excess sugar\n• Light physical activity (walk for 15 min)\n• Avoid simple carbs and sugary foods\n• Take medications as prescribed\n• Check for illness or stress triggers\n• Contact doctor if levels stay high",
                    "Understanding A1C:\n• Measures average blood sugar over 3 months\n• Target: Below 7% for most diabetics\n• Every 1% reduction = 18% lower risk of complications\n• Tested every 3 months for diabetes management"
                ]
            },
            'exercise': {
                'keywords': ['exercise', 'workout', 'physical activity', 'fitness', 'gym', 'walk', 'run', 'sport', 'activity'],
                'responses': [
                    "Exercise is great for diabetes management!\n• Aim for 150 minutes/week of moderate activity\n• Mix cardio (walking, cycling) and strength training\n• Start slowly if you're new to exercise\n• Check blood sugar before/after exercise\n• Stay hydrated and carry a snack",
                    "Best exercises for diabetes:\n• Brisk walking (30 min, 5x/week)\n• Swimming (low-impact, full-body)\n• Cycling or stationary bike\n• Yoga or tai chi (improves flexibility & stress)\n• Strength training (2-3x/week)\n\nRemember: Even 10 minutes of activity helps!",
                    "Exercise safety tips:\n• Exercise at the same time daily for consistency\n• Warm up for 5-10 minutes\n• Carry quick sugar source (glucose tablets)\n• Wear proper, comfortable footwear\n• Monitor for hypoglycemia (shakiness, dizziness)\n• Cool down for 5-10 minutes\n• Stay consistent - 3+ times per week",
                    "Exercise benefits for diabetes:\n✓ Improves insulin sensitivity\n✓ Lowers blood sugar levels\n✓ Reduces weight and BMI\n✓ Improves heart health\n✓ Reduces stress and anxiety\n✓ Improves sleep quality\n✓ Increases energy levels"
                ]
            },
            'weight': {
                'keywords': ['weight', 'bmi', 'overweight', 'obese', 'lose weight', 'weight loss', 'slim'],
                'responses': [
                    "Weight management for diabetes:\n• BMI under 25 is ideal; 25-29 is overweight\n• Even 5-10% weight loss improves blood sugar\n• Combine diet + exercise for best results\n• Aim for gradual loss (1-2 lbs/week)\n• Focus on sustainable habits, not quick fixes",
                    "Healthy weight loss strategies:\n• Create calorie deficit through diet & exercise\n• Eat more protein (keeps you full longer)\n• Increase fiber intake (fruits, vegetables, grains)\n• Reduce portion sizes gradually\n• Drink water before meals\n• Keep a food journal\n• Get 7-9 hours of sleep\n• Manage stress effectively",
                    "BMI breakdown:\n• Under 18.5: Underweight\n• 18.5-24.9: Healthy weight\n• 25-29.9: Overweight\n• 30+: Obese\n\nConsult your doctor for personalized targets."
                ]
            },
            'blood pressure': {
                'keywords': ['blood pressure', 'bp', 'hypertension', 'systolic', 'diastolic', 'pressure'],
                'responses': [
                    "Blood pressure management for diabetics:\n• Healthy BP: Less than 120/80 mm Hg\n• Elevated: 120-129/<80 (monitor closely)\n• High BP: 130/80 or higher\n• Diabetics need stricter control (target <130/80)",
                    "Ways to lower blood pressure:\n• Reduce sodium intake (aim for <2,300mg/day)\n• Increase potassium (bananas, leafy greens)\n• Regular aerobic exercise (30 min, 5x/week)\n• Maintain healthy weight\n• Limit alcohol consumption\n• Manage stress through meditation/yoga\n• Take medications as prescribed\n• Monitor at home regularly",
                    "Blood pressure monitoring:\n• Check regularly (morning and evening)\n• Same arm, same position each time\n• Sit calmly for 5 minutes before measuring\n• Keep a log to track patterns\n• Share readings with your doctor\n• Elevated readings + symptoms = call doctor"
                ]
            },
            'stress': {
                'keywords': ['stress', 'anxiety', 'worry', 'tension', 'relax', 'depressed', 'mental health'],
                'responses': [
                    "Stress management for diabetes:\n• Stress raises blood sugar levels\n• Use: Deep breathing, meditation, yoga\n• Practice: 10-15 min daily\n• Connect: With friends, family, support groups\n• Engage: In hobbies and activities\n• Sleep: 7-9 hours nightly\n• Consider professional help if overwhelmed",
                    "Stress reduction techniques:\n• Deep breathing (4-count in, 6-count out)\n• Progressive muscle relaxation (tense & release)\n• Mindfulness meditation (10-20 min/day)\n• Gentle yoga (improves flexibility & calm)\n• Journaling (emotional release)\n• Listening to calming music\n• Spending time in nature\n• Regular exercise",
                    "Quick stress relief:\n• 5-min breathing break\n• 10-min walk\n• Stretch or gentle yoga\n• Listen to music\n• Call a friend\n• Practice gratitude\n• Take a warm bath\n• Limit caffeine and alcohol"
                ]
            },
            'sleep': {
                'keywords': ['sleep', 'rest', 'tired', 'fatigue', 'insomnia', 'sleepy', 'exhausted'],
                'responses': [
                    "Quality sleep is essential for diabetes:\n• Aim for 7-9 hours nightly\n• Poor sleep worsens blood sugar control\n• Establish consistent sleep schedule\n• Keep bedroom cool, dark, quiet\n• Avoid screens 1 hour before bed",
                    "Sleep improvement tips:\n• Go to bed/wake up at same time daily\n• Avoid caffeine after 2 PM\n• No heavy meals 2-3 hours before bed\n• Exercise during day (not near bedtime)\n• Practice relaxation techniques\n• Avoid alcohol (disrupts sleep quality)\n• Limit daytime naps to 20-30 min",
                    "Sleep environment:\n• Temperature: 65-68°F is ideal\n• Darkness: Use blackout curtains\n• Sound: White noise can help\n• Comfort: Good mattress and pillow\n• Bedding: Clean, breathable sheets\n• No TV/phones in bedroom"
                ]
            },
            'medication': {
                'keywords': ['medication', 'medicine', 'insulin', 'drug', 'pill', 'prescription', 'metformin', 'dose'],
                'responses': [
                    "Medication management tips:\n• Take exactly as prescribed\n• Same time daily for consistency\n• Set phone reminders if needed\n• Never skip doses\n• Don't adjust dosage without doctor\n• Keep medication list updated\n• Inform all doctors about medications\n• Store properly (temperature, light)",
                    "Insulin management:\n• Rotate injection sites to prevent lipohypertrophy\n• Check expiration dates before use\n• Store unopened vials/pens in refrigerator\n• Keep in-use insulin at room temperature\n• Use new needle for each injection\n• Know your insulin type and timing\n• Always carry backup insulin\n• Dispose of needles safely",
                    "Medication side effects:\n• Report unusual symptoms to doctor\n• Common: Nausea, fatigue, headache\n• Don't stop medication without consulting\n• Some side effects improve with time\n• Alternative medications may be available\n• Keep detailed symptom journal"
                ]
            },
            'symptoms': {
                'keywords': ['symptom', 'feel', 'sick', 'pain', 'dizzy', 'thirsty', 'tired', 'numb', 'tingle'],
                'responses': [
                    "Diabetes warning signs:\n• Increased thirst\n• Frequent urination (especially at night)\n• Fatigue or weakness\n• Blurred vision\n• Slow-healing cuts/sores\n• Numbness or tingling (neuropathy)\n• Unexplained weight loss\n\n⚠️ Call doctor if symptoms persist or worsen",
                    "Emergency symptoms - Seek help immediately:\n• Blood sugar <70 mg/dL (shakiness, confusion)\n• Blood sugar >300 mg/dL (nausea, fruity breath)\n• Chest pain or shortness of breath\n• Severe headache or dizziness\n• Loss of consciousness\n• Difficulty speaking or vision changes\n\nDon't delay - call 911 if severe",
                    "Hypoglycemia (low blood sugar):\n• Symptoms: Trembling, sweating, confusion, anxiety\n• Causes: Too much insulin, missed meals, exercise\n• Treatment: 15g quick carbs (juice, glucose tablets)\n• Check after 15 min, repeat if needed\n• Eat snack with protein/fat when stable\n• Always carry emergency glucose"
                ]
            },
            'prevention': {
                'keywords': ['prevent', 'prevention', 'preventive', 'checkup', 'screening', 'doctor', 'appointment'],
                'responses': [
                    "Preventive care for diabetics:\n• Annual eye exams (retinopathy screening)\n• Annual foot checks (neuropathy detection)\n• Annual kidney tests (microalbumin)\n• Regular blood pressure monitoring\n• Cholesterol screening (every 5 years)\n• Dental checkups (2x/year)\n• Annual comprehensive health assessment",
                    "Preventive measures to track:\n• Exercise routine (150 min/week)\n• Healthy eating (balanced meals)\n• Stress management techniques\n• Quality sleep (7-9 hours)\n• Medication adherence\n• Regular monitoring\n• Health checkups\n\nUse the Prevention dashboard to log these!",
                    "What to discuss with doctor:\n• Current blood sugar control\n• Medication side effects\n• Any new symptoms\n• Lifestyle changes\n• Preventive screening needs\n• Mental health concerns\n• Exercise limitations\n• Questions about diabetes"
                ]
            },
            'hydration': {
                'keywords': ['water', 'hydration', 'drink', 'thirst', 'dehydrated'],
                'responses': [
                    "Hydration for diabetes:\n• Drink 8-10 glasses of water daily (64-80 oz)\n• More if you exercise or live in warm climate\n• Water helps flush excess glucose\n• Avoid sugary drinks and sodas\n• Limit caffeine (causes dehydration)\n• Alcohol can affect blood sugar",
                    "Hydration tips:\n• Drink water with meals\n• Start day with glass of water\n• Keep water bottle with you\n• Herbal tea counts toward hydration\n• Unsweetened beverages are best\n• Listen to thirst cues\n• Monitor urine color (pale = well hydrated)"
                ]
            },
            'features': {
                'keywords': ['feature', 'how to use', 'dashboard', 'predict', 'history', 'report', 'gamification', 'badge', 'prevention'],
                'responses': [
                    "Platform features available:\n📊 Diabetes Prediction: Get personalized risk assessment\n📈 Health History: Track trends over time\n📋 Diet Planner: Personalized meal recommendations\n🎯 Prevention: Track interventions and effectiveness\n📄 PDF Reports: Download comprehensive health reports\n🎮 Gamification: Earn badges and points\n💬 Health Chat: Ask health questions anytime",
                    "Getting started:\n1. Create account and login\n2. Take health check (enter your metrics)\n3. View personalized recommendations\n4. Track your health history\n5. Start preventive measures\n6. Download PDF reports\n7. Earn gamification badges\n\nVisit each section to learn more!",
                    "Maximizing your experience:\n✓ Do health checks monthly for trends\n✓ Track preventive measures to see effectiveness\n✓ Review PDF reports quarterly\n✓ Complete daily activities for gamification\n✓ Ask health questions in chat\n✓ Share progress with your doctor"
                ]
            },
            'general': {
                'keywords': ['help', 'info', 'tell me', 'what', 'how', 'can you', 'question'],
                'responses': [
                    "I can help you with:\n• Diet and nutrition planning\n• Exercise recommendations\n• Blood sugar management\n• Weight and BMI information\n• Blood pressure control\n• Stress reduction techniques\n• Sleep improvement\n• Medication reminders\n• Symptom information\n• Preventive health measures\n\nWhat topic interests you?",
                    "Living well with diabetes requires:\n• Healthy eating habits\n• Regular physical activity (150 min/week)\n• Consistent blood sugar monitoring\n• Taking medications as prescribed\n• Managing stress effectively\n• Getting quality sleep\n• Regular health checkups\n• Positive mindset\n\nI'm here to support you in all areas!",
                    "Remember:\n✓ Consult your doctor for medical decisions\n✓ Individual needs vary - what works for others may differ\n✓ Small changes lead to big results\n✓ Consistency matters more than perfection\n✓ You're not alone - seek support when needed\n✓ Celebrate your progress!\n\nAsk me anything!"
                ]
            }
        }
    
    def get_response(self, user_message, user_id=None, user_context=None):
        """Get response from enhanced rule-based health chatbot"""
        message_lower = user_message.lower()
        
        # Check for greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'sup', 'thanks', 'thank you']
        if any(word in message_lower.split() for word in greetings):
            return random.choice(self.responses['greeting'])
        
        # Check for category keywords (in order of priority)
        priority_categories = ['emergency', 'prevention', 'features', 'medication', 'glucose', 'exercise', 'diet']
        
        for category in self.responses.keys():
            if category in ['greeting', 'general']:
                continue
            
            data = self.responses[category]
            if isinstance(data, dict) and 'keywords' in data:
                if any(keyword in message_lower for keyword in data['keywords']):
                    return random.choice(data['responses'])
        
        # Default response
        return random.choice(self.responses['general']['responses'])

chatbot = HealthChatbot()

def get_chatbot_response(message, user_id=None, user_context=None):
    """Get chatbot response"""
    return chatbot.get_response(message, user_id, user_context)

def clear_conversation_history(user_id):
    """Clear conversation history for a user"""
    if user_id in conversation_histories:
        del conversation_histories[user_id]
