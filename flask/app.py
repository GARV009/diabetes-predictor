import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
from diet_planner import generate_diet_plan

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
    float_features = [float(x) for x in request.form.values()]
    glucose = float_features[0]
    insulin = float_features[1]
    bmi = float_features[2]
    age = float_features[3]
    
    final_features = [np.array(float_features)]
    prediction = model.predict( sc.transform(final_features) )
    
    pred_value = int(prediction[0])
    
    if pred_value == 1:
        pred = "You have Diabetes, please consult a Doctor."
    else:
        pred = "You don't have Diabetes."
    output = pred
    
    diet_plan = generate_diet_plan(glucose, insulin, bmi, age, pred_value)

    return render_template('index.html', prediction_text='{}'.format(output), diet_plan=diet_plan)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
