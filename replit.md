# Diabetes Predictor & Diet Planner

## Overview
A comprehensive machine learning web application that predicts diabetes risk and generates personalized diet plans based on medical features including glucose level, insulin, BMI, and age. Built with Flask and scikit-learn.

## Features
- **Diabetes Prediction**: ML-powered prediction using Support Vector Classifier (SVC)
- **Personalized Diet Plans**: Automatically generated diet plans based on health metrics
- **Health Metrics Tracking**: Displays user's glucose, insulin, BMI, and age
- **Customized Recommendations**: Diet plans adapt based on:
  - Glucose levels (adjusts carbohydrate intake)
  - Insulin levels (identifies insulin resistance)
  - BMI (calorie targets)
  - Age (metabolic adjustments)

## Diet Plan Components
1. **Daily Calorie Target**: Personalized based on BMI, age, and glucose levels
2. **Macronutrient Breakdown**: Carbs, protein, fats, and fiber recommendations
3. **Meal Suggestions**: Breakfast, lunch, dinner, and snack options with calorie counts
4. **Diabetic-Friendly Foods**: Categorized by vegetables, proteins, grains, fruits, dairy, and healthy fats
5. **Foods to Avoid**: High sugar, refined carbs, unhealthy fats, and high sodium foods
6. **Weekly Diet Schedule**: 7-day meal plan with specific meals for each day
7. **Personalized Tips**: Health advice tailored to individual glucose and insulin levels

## Project Structure
- `flask/` - Main application directory
  - `app.py` - Flask web application with prediction and diet plan routes
  - `diet_planner.py` - Diet plan generation logic
  - `model.py` - Original ML model training script
  - `retrain_model.py` - Helper script for model retraining
  - `model.pkl` - Pre-trained SVC model
  - `diabetes.csv` - Dataset
  - `templates/` - HTML templates
    - `index.html` - Main web interface with prediction form and diet plan display
  - `static/` - CSS and static files
    - `css/style.css` - Styling for the application

## Technologies
- Python 3.11
- Flask 2.3.0
- scikit-learn 1.2.0
- pandas 2.0.0
- numpy 1.24.0

## Setup
The application runs on port 5000 and uses a pre-trained Support Vector Classifier (SVC) model with MinMax scaling.

## Recent Changes (Nov 14, 2025)
- ✅ Updated dependencies to be compatible with Python 3.11
- ✅ Configured Flask to run on 0.0.0.0:5000 for Replit environment
- ✅ Added .gitignore for Python projects
- ✅ Implemented comprehensive Diet Plan Generator feature
- ✅ Created personalized diet planning module with glucose/insulin integration
- ✅ Updated frontend with modern, responsive design for diet plan display
- ✅ Enhanced CSS styling with categorized sections and visual indicators
- ✅ Fixed NumPy array comparison bug in prediction route
- ✅ Integrated health metrics display in diet plan output
