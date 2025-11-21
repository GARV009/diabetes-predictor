"""
Train ML models on merged diabetes datasets with improved accuracy.
This script:
1. Merges diabetes.csv and healthcare_diabetes.csv
2. Trains multiple models
3. Selects the best one
4. Saves model and scaler for production use
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔬 TRAINING MERGED DIABETES PREDICTION MODEL")
print("=" * 80)

# Step 1: Load both datasets
print("\n📂 Loading datasets...")
try:
    df1 = pd.read_csv('flask/diabetes_original.csv')
    print(f"✓ Dataset 1 (Diabetes): {df1.shape}")
    print(f"  Columns: {list(df1.columns)}")
except Exception as e:
    print(f"✗ Error loading diabetes_original.csv: {e}")
    df1 = pd.DataFrame()

try:
    df2 = pd.read_csv('flask/healthcare_diabetes.csv')
    print(f"✓ Dataset 2 (Healthcare-Diabetes): {df2.shape}")
    print(f"  Columns: {list(df2.columns)}")
    
    # Remove 'Id' column if present
    if 'Id' in df2.columns:
        df2 = df2.drop('Id', axis=1)
        print(f"  Removed 'Id' column")
except Exception as e:
    print(f"✗ Error loading healthcare_diabetes.csv: {e}")
    df2 = pd.DataFrame()

# Step 2: Merge datasets
print("\n🔀 Merging datasets...")
if not df1.empty and not df2.empty:
    merged_df = pd.concat([df1, df2], axis=0, ignore_index=True)
    print(f"✓ Merged dataset shape: {merged_df.shape}")
else:
    print("⚠ Using single dataset due to loading issues")
    merged_df = df1 if not df1.empty else df2

# Step 3: Handle missing values
print("\n🧹 Handling missing values...")
print(f"Missing values before:\n{merged_df.isna().sum()}")
merged_df = merged_df.fillna(merged_df.mean(numeric_only=True))
print(f"✓ Missing values filled with mean")

# Step 4: Prepare features and target
print("\n📊 Preparing features...")
target_col = 'Outcome'
if target_col not in merged_df.columns:
    print(f"✗ Target column '{target_col}' not found!")
    print(f"Available columns: {list(merged_df.columns)}")
    exit(1)

# Drop non-numeric columns
X = merged_df.drop(target_col, axis=1).select_dtypes(include=[np.number])
y = merged_df[target_col]

print(f"✓ Features shape: {X.shape}")
print(f"✓ Target distribution:\n{y.value_counts()}")
print(f"  Diabetes (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
print(f"  Non-Diabetes (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

# Step 5: Split and scale data
print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train set: {X_train.shape}")
print(f"✓ Test set: {X_test.shape}")

print("\n⚙️  Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print(f"✓ Features scaled using StandardScaler")

# Step 6: Train multiple models
print("\n🤖 Training multiple models...")
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, probability=True),
    'Random Forest': RandomForestClassifier(n_estimators=200, random_state=42, max_depth=15),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, random_state=42, learning_rate=0.1),
    'SVM': SVC(kernel='rbf', probability=True, random_state=42, C=1.0),
}

results = {}
best_model = None
best_accuracy = 0
best_model_name = ""

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    results[name] = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc
    }
    
    print(f"    ✓ Accuracy: {accuracy:.4f}")
    print(f"    ✓ Precision: {precision:.4f}")
    print(f"    ✓ Recall: {recall:.4f}")
    print(f"    ✓ F1-Score: {f1:.4f}")
    print(f"    ✓ ROC-AUC: {auc:.4f}")
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model
        best_model_name = name

# Step 7: Display results summary
print("\n" + "=" * 80)
print("📈 MODEL COMPARISON")
print("=" * 80)
print(f"\n{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'F1-Score':<12} {'ROC-AUC':<12}")
print("-" * 80)
for name, metrics in results.items():
    marker = "⭐ BEST" if name == best_model_name else ""
    print(f"{name:<25} {metrics['accuracy']:<12.4f} {metrics['precision']:<12.4f} {metrics['f1']:<12.4f} {metrics['auc']:<12.4f} {marker}")

print(f"\n✅ BEST MODEL: {best_model_name} (Accuracy: {best_accuracy:.4f})")

# Step 8: Save model and scaler
print("\n💾 Saving model and scaler...")
model_path = 'flask/model_merged.pkl'
scaler_path = 'flask/scaler_merged.pkl'
metadata_path = 'flask/model_metadata.pkl'

joblib.dump(best_model, model_path)
joblib.dump(scaler, scaler_path)

metadata = {
    'model_name': best_model_name,
    'accuracy': best_accuracy,
    'feature_names': list(X.columns),
    'all_results': results,
    'merged_datasets': {
        'dataset1': 'diabetes_original.csv',
        'dataset2': 'healthcare_diabetes.csv'
    }
}
joblib.dump(metadata, metadata_path)

print(f"✓ Model saved: {model_path}")
print(f"✓ Scaler saved: {scaler_path}")
print(f"✓ Metadata saved: {metadata_path}")

print("\n" + "=" * 80)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 80)
print(f"\nBest Model: {best_model_name}")
print(f"Accuracy: {best_accuracy:.4f}")
print(f"Training Samples: {X_train.shape[0]}")
print(f"Testing Samples: {X_test.shape[0]}")
print(f"Total Features: {X.shape[1]}")
print("\nReady for integration into Flask app!")
print("=" * 80)
