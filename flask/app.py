import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
from diet_planner import generate_diet_plan
from health_checkup import generate_health_checkup_plan

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

dataset = pd.read_csv('diabetes.csv')

dataset_X = dataset.iloc[:,[1, 2, 5, 7]].values

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0,1))
dataset_scaled = sc.fit_transform(dataset_X)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    # Extract form values
    glucose = float(request.form.get('Glucose Level'))
    insulin = float(request.form.get('Insulin'))
    bmi = float(request.form.get('BMI'))
    age = float(request.form.get('Age'))
    bp_systolic = float(request.form.get('Blood Pressure Systolic'))
    bp_diastolic = float(request.form.get('Blood Pressure Diastolic'))
    family_history = request.form.get('Family History') == 'yes'
    
    # Prepare features for ML model (original 4 features)
    float_features = [glucose, insulin, bmi, age]
    final_features = [np.array(float_features)]
    prediction = model.predict( sc.transform(final_features) )
    
    pred_value = int(prediction[0])
    
    if pred_value == 1:
        pred = "You have Diabetes, please consult a Doctor."
    else:
        pred = "You don't have Diabetes."
    output = pred
    
    # Generate diet plan
    diet_plan = generate_diet_plan(glucose, insulin, bmi, age, pred_value)
    
    # Generate health checkup plan
    checkup_plan = generate_health_checkup_plan(
        age, bmi, glucose, bp_systolic, bp_diastolic, 
        pred_value, family_history
    )

    return render_template('index.html', 
                         prediction_text='{}'.format(output), 
                         diet_plan=diet_plan,
                         checkup_plan=checkup_plan)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
