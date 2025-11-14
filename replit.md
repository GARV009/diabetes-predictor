# Diabetes Predictor & Health Planner

## Overview
A comprehensive machine learning web application that predicts diabetes risk, generates personalized diet plans, and provides detailed health checkup recommendations based on medical features including glucose level, insulin, BMI, age, and blood pressure. Built with Flask and scikit-learn.

## Features

### 1. Diabetes Prediction
- ML-powered prediction using Support Vector Classifier (SVC)
- Analyzes glucose, insulin, BMI, and age

### 2. Personalized Diet Plans
- Daily calorie targets based on BMI, age, and glucose levels
- Custom macronutrient breakdown adjusted for glucose and insulin levels
- Meal suggestions for breakfast, lunch, dinner, and snacks
- Diabetic-friendly foods categorized by type
- Foods to avoid list
- 7-day weekly meal schedule
- Personalized health tips based on individual metrics

### 3. Health Checkup Recommendations
- **Blood Pressure Analysis**: Evaluates both systolic and diastolic readings
- **Recommended Blood Tests**: Categorized by priority (Essential, Recommended, Optional)
  - HbA1c, FBG, Lipid Panel, Kidney Function, Thyroid, etc.
  - Personalized based on age, diabetes status, BP, and family history
- **Test Frequency Guidance**: Specific scheduling for each recommended test
- **Doctor Visit Frequency**: Customized based on health status
- **Lifestyle Recommendations**: Personalized tips for sleep, exercise, hydration, stress management
- **Family History Consideration**: Enhanced monitoring for genetic risk factors

## Input Parameters
- Glucose Level (mg/dL)
- Insulin Level (μU/mL)
- BMI (Body Mass Index)
- Age (years)
- Blood Pressure (Systolic/Diastolic)
- Family History of Diabetes (Yes/No)

## Project Structure
- `flask/` - Main application directory
  - `app.py` - Flask web application with prediction, diet plan, and health checkup routes
  - `diet_planner.py` - Diet plan generation logic
  - `health_checkup.py` - Health checkup recommendation logic
  - `model.py` - Original ML model training script
  - `model.pkl` - Pre-trained SVC model
  - `diabetes.csv` - Dataset
  - `templates/` - HTML templates
    - `index.html` - Main web interface with comprehensive health analysis display
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
- ✅ Implemented Health Checkup Recommendation Tool
- ✅ Added blood pressure monitoring and analysis
- ✅ Created comprehensive blood test recommendation system
- ✅ Added lifestyle recommendations based on health metrics
- ✅ Fixed critical blood pressure logic to properly evaluate both systolic and diastolic readings
- ✅ Enhanced form with blood pressure and family history inputs
