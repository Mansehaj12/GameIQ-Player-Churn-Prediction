# ============================================================
# GameIQ - Step 4: Machine Learning Model (Churn Prediction)
# ============================================================
# This script:
#   1. Loads and prepares the Cookie Cats dataset
#   2. Engineers features for the ML model
#   3. Trains a RandomForestClassifier
#   4. Evaluates the model (accuracy, classification report)
#   5. Saves the trained model as model.pkl
# ============================================================

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

# ────────────────────────────────────────────────────────────
# 4.1 LOAD DATA
# ────────────────────────────────────────────────────────────

data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cookie_cats.csv')
df = pd.read_csv(data_path)

print("=" * 60)
print("STEP 4: MACHINE LEARNING MODEL")
print("=" * 60)

# ────────────────────────────────────────────────────────────
# 4.2 FEATURE ENGINEERING
# ────────────────────────────────────────────────────────────
# We need to prepare our data for the ML model.
#
# TARGET (what we predict):
#   churn → 1 if the player LEFT (retention_7 == False)
#            0 if the player STAYED
#
# FEATURES (what we use to predict):
#   1. sum_gamerounds → How many rounds the player played (engagement)
#      WHY: Higher engagement = less likely to churn
#
#   2. retention_1    → Did they come back on Day 1? (True/False → 1/0)
#      WHY: Day 1 return is the strongest early signal of retention
#
#   3. version        → gate_30 or gate_40 (categorical → 1/0)
#      WHY: The A/B test group might affect churn behavior

# Create target variable
df['churn'] = (df['retention_7'] == False).astype(int)

# Convert categorical 'version' to numeric
# gate_30 = 0 (control group)
# gate_40 = 1 (test group)
df['version_num'] = (df['version'] == 'gate_40').astype(int)

# Convert boolean retention_1 to integer (True→1, False→0)
df['retention_1_num'] = df['retention_1'].astype(int)

print("\nFeature columns created:")
print(df[['sum_gamerounds', 'retention_1_num', 'version_num', 'churn']].head(10))

# ────────────────────────────────────────────────────────────
# 4.3 PREPARE FEATURES AND TARGET
# ────────────────────────────────────────────────────────────

# Select features (X) and target (y)
features = ['sum_gamerounds', 'retention_1_num', 'version_num']
X = df[features]
y = df['churn']

print(f"\nFeatures shape: {X.shape}")
print(f"Target distribution:")
print(f"  Churned (1):  {(y == 1).sum()} ({(y == 1).mean()*100:.1f}%)")
print(f"  Retained (0): {(y == 0).sum()} ({(y == 0).mean()*100:.1f}%)")

# ────────────────────────────────────────────────────────────
# 4.4 SPLIT INTO TRAIN AND TEST SETS
# ────────────────────────────────────────────────────────────
# WHY SPLIT?
#   We train on 80% of data and test on 20%.
#   This ensures the model is evaluated on data it has NEVER seen,
#   which simulates real-world performance.
#
#   random_state=42 makes the split reproducible (same split every run).

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTrain set: {X_train.shape[0]} samples")
print(f"Test set:  {X_test.shape[0]} samples")

# ────────────────────────────────────────────────────────────
# 4.5 TRAIN THE MODEL
# ────────────────────────────────────────────────────────────
# WHY RANDOM FOREST?
#
#   1. It's an ENSEMBLE method — it creates many decision trees and
#      averages their predictions, which reduces overfitting.
#
#   2. Works well with both numerical and categorical features.
#
#   3. Handles imbalanced data reasonably well.
#
#   4. Provides FEATURE IMPORTANCE — tells us which features matter most.
#
#   5. Doesn't require feature scaling (unlike SVM or Neural Networks).
#
#   6. Easy to interpret and explain to stakeholders.
#
# PARAMETERS:
#   n_estimators=100  → Use 100 decision trees
#   random_state=42   → Reproducible results
#   n_jobs=-1          → Use all CPU cores for speed

print("\nTraining RandomForest model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("Model trained successfully!")

# ────────────────────────────────────────────────────────────
# 4.6 EVALUATE THE MODEL
# ────────────────────────────────────────────────────────────

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=['Retained', 'Churned']))

print("--- Confusion Matrix ---")
cm = confusion_matrix(y_test, y_pred)
print(f"                  Predicted")
print(f"                  Retained  Churned")
print(f"  Actual Retained    {cm[0][0]:>5}    {cm[0][1]:>5}")
print(f"  Actual Churned     {cm[1][0]:>5}    {cm[1][1]:>5}")

# ────────────────────────────────────────────────────────────
# 4.7 FEATURE IMPORTANCE
# ────────────────────────────────────────────────────────────
# This tells us WHICH features the model relies on most to predict churn.

print("\n--- Feature Importance ---")
importances = model.feature_importances_
for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
    bar = "#" * int(imp * 50)
    print(f"  {feat:<20} {imp:.4f}  {bar}")

print("""
INTERPRETATION:
  - 'sum_gamerounds' is likely the most important feature.
    This makes sense: engagement is the #1 predictor of retention.
  - 'retention_1_num' is the second strongest signal.
    If a player returns on Day 1, they're much more likely to stay.
  - 'version_num' has the least importance, meaning the gate placement
    has a small but measurable effect on churn.
""")

# ────────────────────────────────────────────────────────────
# 4.8 SAVE THE MODEL
# ────────────────────────────────────────────────────────────
# We save the model using Python's 'pickle' module.
# This lets us load it later in the Flask API without retraining.

model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"Model saved to: {os.path.abspath(model_path)}")

# ────────────────────────────────────────────────────────────
# 4.9 QUICK TEST: Predict for a sample player
# ────────────────────────────────────────────────────────────

print("\n--- Quick Prediction Test ---")
# Test player: played 10 rounds, returned on Day 1, gate_30 version
test_player = pd.DataFrame({
    'sum_gamerounds': [10],
    'retention_1_num': [1],
    'version_num': [0]
})
prediction = model.predict(test_player)[0]
probability = model.predict_proba(test_player)[0]

print(f"  Player: 10 rounds, returned Day 1, gate_30")
print(f"  Prediction: {'CHURN' if prediction == 1 else 'RETAINED'}")
print(f"  Confidence: {max(probability)*100:.1f}%")
print(f"  (Retain prob: {probability[0]*100:.1f}%, Churn prob: {probability[1]*100:.1f}%)")

# Test player 2: played 200 rounds, returned on Day 1, gate_40 version
test_player2 = pd.DataFrame({
    'sum_gamerounds': [200],
    'retention_1_num': [1],
    'version_num': [1]
})
prediction2 = model.predict(test_player2)[0]
probability2 = model.predict_proba(test_player2)[0]

print(f"\n  Player: 200 rounds, returned Day 1, gate_40")
print(f"  Prediction: {'CHURN' if prediction2 == 1 else 'RETAINED'}")
print(f"  Confidence: {max(probability2)*100:.1f}%")
print(f"  (Retain prob: {probability2[0]*100:.1f}%, Churn prob: {probability2[1]*100:.1f}%)")

print("\n" + "=" * 60)
print("STEP 4 COMPLETE!")
print("=" * 60)