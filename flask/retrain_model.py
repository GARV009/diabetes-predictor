import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

# Load dataset
dataset = pd.read_csv('diabetes.csv')

# Extract features and target
dataset_X = dataset.iloc[:, [1, 2, 5, 7]].values
dataset_Y = dataset.iloc[:, 8].values

# Scale the features
sc = MinMaxScaler(feature_range=(0, 1))
dataset_scaled = sc.fit_transform(dataset_X)

# Split the data
X_train, X_test, Y_train, Y_test = train_test_split(dataset_scaled, dataset_Y, test_size=0.20, random_state=42)

# Train SVC model
svc = SVC(kernel='linear', random_state=42)
svc.fit(X_train, Y_train)

# Calculate accuracy
accuracy = svc.score(X_test, Y_test)
print(f"Model trained successfully!")
print(f"Model accuracy: {accuracy:.4f}")

# Save the model
pickle.dump(svc, open('model.pkl', 'wb'))
print("Model saved as model.pkl")
