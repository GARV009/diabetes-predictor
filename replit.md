# Diabetes Predictor

## Overview
A machine learning web application that predicts whether a patient has diabetes based on medical features like glucose level, insulin, age, and BMI. Built with Flask and scikit-learn.

## Project Structure
- `flask/` - Main application directory
  - `app.py` - Flask web application
  - `model.py` - ML model training script
  - `model.pkl` - Pre-trained SVC model
  - `diabetes.csv` - Dataset
  - `templates/` - HTML templates
  - `static/` - CSS and static files

## Technologies
- Python 3.11
- Flask 2.3.0
- scikit-learn 1.2.0
- pandas 2.0.0
- numpy 1.24.0

## Setup
The application runs on port 5000 and uses a pre-trained Support Vector Classifier (SVC) model with MinMax scaling.

## Recent Changes (Nov 14, 2025)
- Updated dependencies to be compatible with Python 3.11
- Configured Flask to run on 0.0.0.0:5000 for Replit environment
- Added .gitignore for Python projects
