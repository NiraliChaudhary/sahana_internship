import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_curve, auc, roc_auc_score
import seaborn as sns

#===========binary============

# 🏥 Create synthetic diabetes dataset
# (Similar to real Pima Indians Diabetes dataset)

np.random.seed(42)

n_patients = 300

# Medical features
data = {
    'Age': np.random.randint(21, 81, n_patients),
    'BMI': np.random.uniform(18, 45, n_patients),
    'BloodGlucose': np.random.uniform(70, 200, n_patients),
    'BloodPressure': np.random.uniform(70, 140, n_patients),
    'Insulin': np.random.uniform(0, 846, n_patients),
}

df = pd.DataFrame(data)

# 🎯 Target: Patient has diabetes (1) or not (0)
# Simple rule-based for demo (real data is complex!)
df['HasDiabetes'] = (
    (df['BloodGlucose'] > 125) &
    (df['BMI'] > 25) &
    (df['Age'] > 45)
).astype(int)

# Add some noise for realism
noise_idx = np.random.choice(df.index, size=30, replace=False)
df.loc[noise_idx, 'HasDiabetes'] = 1 - df.loc[noise_idx, 'HasDiabetes']

print("📋 Medical Dataset Preview:")
print(df.head(10))
print(f"\n✅ Diseased patients: {df['HasDiabetes'].sum()} ({df['HasDiabetes'].mean()*100:.1f}%)")
print(f"❌ Healthy patients: {(1-df['HasDiabetes']).sum()} ({(1-df['HasDiabetes']).mean()*100:.1f}%)")

#======================C (low C parameter =more relaxed..preventing overfitting to noise)=======================

# Prepare data
X = df[['Age', 'BMI', 'BloodGlucose', 'BloodPressure', 'Insulin']]
y = df['HasDiabetes']

# Split: 70% training, 30% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y  # ← stratify preserves class balance
)

print(f"🏥 Training set: {len(X_train)} patients")
print(f"🔬 Test set: {len(X_test)} patients")

# 🎯 Create & train model with C=1.0 (default)
model = LogisticRegression(C=1.0, random_state=42, max_iter=1000)
model.fit(X_train, y_train)

print("\n✅ Model trained!")
print(f"Coefficients (feature importance):")
for feature, coef in zip(X.columns, model.coef_[0]):
    print(f"  {feature:15s}: {coef:7.3f}")


#===making predictions and confidence score====
# Test on a few patients
patient_1 = pd.DataFrame({
    'Age': [35], 'BMI': [22], 'BloodGlucose': [110],
    'BloodPressure': [80], 'Insulin': [50]
})

patient_2 = pd.DataFrame({
    'Age': [65], 'BMI': [32], 'BloodGlucose': [160],
    'BloodPressure': [130], 'Insulin': [200]
})

# 🔮 Predict class (0 or 1)
pred_1 = model.predict(patient_1)[0]
pred_2 = model.predict(patient_2)[0]

# 📊 Predict probability
prob_1 = model.predict_proba(patient_1)[0]
prob_2 = model.predict_proba(patient_2)[0]

print("👨 Patient 1 (young, healthy BMI):")
print(f"   Prediction: {'🔴 HAS DIABETES' if pred_1 else '🟢 NO DIABETES'}")
print(f"   Confidence: {prob_1[0]*100:.1f}% healthy, {prob_1[1]*100:.1f}% diseased")

print("\n👴 Patient 2 (older, high glucose):")
print(f"   Prediction: {'🔴 HAS DIABETES' if pred_2 else '🟢 NO DIABETES'}")
print(f"   Confidence: {prob_2[0]*100:.1f}% healthy, {prob_2[1]*100:.1f}% diseased")


#=====confusion matrix=====
# Make predictions on test set
y_pred = model.predict(X_test)

# Create confusion matrix
cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:")
print(cm)
print(f"\nBreakdown:")
print(f"  True Negatives (TN):  {cm[0,0]}  ✅ Correctly identified healthy")
print(f"  False Positives (FP): {cm[0,1]}  ⚠️  Healthy but predicted diseased")
print(f"  False Negatives (FN): {cm[1,0]}  🚨 DISEASED but predicted healthy (WORST!)")
print(f"  True Positives (TP):  {cm[1,1]}  ✅ Correctly identified diseased")

# Calculate key metrics
sensitivity = cm[1,1] / (cm[1,1] + cm[1,0])  # TPR: "Did we catch disease?"
specificity = cm[0,0] / (cm[0,0] + cm[0,1])  # TNR: "Did we avoid false alarms?"

print(f"\n🩺 Clinical Metrics:")
print(f"  Sensitivity (Recall):  {sensitivity*100:.1f}%  ← catch disease")
print(f"  Specificity:           {specificity*100:.1f}%  ← avoid false alarms")


#=====heatmap====
# Beautiful heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='RdYlGn',
            xticklabels=['Healthy', 'Diseased'],
            yticklabels=['Healthy', 'Diseased'],
            cbar_kws={'label': 'Count'})
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('🏥 Medical Diagnosis Confusion Matrix')
plt.tight_layout()
plt.show()


#===== Get probability predictions on test set
y_proba = model.predict_proba(X_test)[:, 1]  # Probability of disease

print("📊 Sample predictions (first 10 patients):")
print("Patient | Probability | Default (0.5) | Aggressive (0.3)")
print("-" * 55)
for i in range(10):
    pred_default = "Diseased" if y_proba[i] > 0.5 else "Healthy"
    pred_aggressive = "Diseased" if y_proba[i] > 0.3 else "Healthy"
    print(f"  {i+1:2d}    |   {y_proba[i]:5.1%}    |    {pred_default:8s}   |    {pred_aggressive:8s}")

# 🔴 Notice: Different threshold = different predictions!

#================= Calculate ROC(Receiver Operating Characteristic) curve======================
fpr, tpr, thresholds = roc_curve(y_test, y_proba)

# Calculate AUC (Area Under Curve)
roc_auc = auc(fpr, tpr)
# OR: roc_auc = roc_auc_score(y_test, y_proba)

print(f"🎯 ROC-AUC Score: {roc_auc:.3f}")
print(f"\n📊 Interpretation:")
print(f"  0.90-1.00: 🟢 Excellent (FDA loves this!)")
print(f"  0.80-0.90: 🟢 Good")
print(f"  0.70-0.80: 🟡 Fair (acceptable for medical)")
print(f"  0.60-0.70: 🔴 Poor")
print(f"  0.50-0.60: 🔴 Very Poor (barely better than random)")
print(f"  0.50:      ⚪ Random guess")

#==================visualization of ROC-AUC==================
plt.figure(figsize=(10, 8))

# Plot ROC curve
plt.plot(fpr, tpr, color='#1f77b4', lw=3,
         label=f'ROC Curve (AUC = {roc_auc:.3f})')

# Plot random classifier (baseline)
plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--',
         label='Random Classifier (AUC = 0.500)')

# Highlight the good zone
plt.fill_between(fpr, tpr, alpha=0.2, color='#1f77b4')

plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12)
plt.title('🏥 ROC Curve: Diabetes Detection Model', fontsize=14, fontweight='bold')
plt.legend(loc="lower right", fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 📍 Mark key threshold points
print("\n🔑 Key Operating Points on ROC Curve:")
print("Threshold | Sensitivity | Specificity | Use Case")
print("-" * 55)
for idx in [0, len(thresholds) // 4, len(thresholds) // 2, 3 * len(thresholds) // 4, -1]:
    threshold = thresholds[idx]
    sensitivity = tpr[idx]
    specificity = 1 - fpr[idx]

    if threshold >= 0 and threshold <= 1:
        print(f"   {threshold:.2f}   |    {sensitivity:5.1%}    |    {specificity:5.1%}    |", end="")
        if threshold < 0.3:
            print(" Aggressive (catch all)")
        elif threshold < 0.5:
            print(" Balanced")
        else:
            print(" Conservative (high confidence)")


#==================clinical decision making with ROC==================
# In real medical practice, doctors choose threshold based on needs:

print("🩺 CLINICAL SCENARIOS:")
print("\n1️⃣ SCREENING (catch all possible cases)")
print("   Goal: Minimize false negatives (missed diagnoses)")
print("   Use threshold: 0.30 (low bar, catch everything)")
print("   Result: Sensitivity ~96%, Specificity ~92%")
print("   Trade-off: More false alarms, but catches diseases")

print("\n2️⃣ CONFIRMATION TEST (high confidence needed)")
print("   Goal: Avoid unnecessary treatment")
print("   Use threshold: 0.70 (high bar)")
print("   Result: Sensitivity ~60%, Specificity ~99%")
print("   Trade-off: Miss some cases, but very accurate when positive")

print("\n3️⃣ ROUTINE CHECK-UP (balanced)")
print("   Goal: Balance sensitivity and specificity")
print("   Use threshold: 0.50 (default)")
print("   Result: Sensitivity ~87%, Specificity ~97%")
print("   Trade-off: Good balance for general screening")

#============================visualization =========================


# Train multiple models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Logistic (L2 Reg)': LogisticRegression(C=0.1, random_state=42, max_iter=1000),
    'Logistic (Strong Reg)': LogisticRegression(C=0.01, random_state=42, max_iter=1000),
}

plt.figure(figsize=(10, 8))

# Plot ROC for each model
for name, model in models.items():
    model.fit(X_train, y_train)
    y_proba = model.predict_proba(X_test)[:, 1]

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)

    plt.plot(fpr, tpr, lw=2.5, label=f'{name} (AUC = {roc_auc:.3f})')

# Baseline
plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random (AUC = 0.500)')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('🏥 ROC-AUC: Comparing Different Model Configurations', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 🎯 Winner
print("🏆 Model Comparison:")
for name, model in models.items():
    model.fit(X_train, y_train)
    y_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"  {name:25s}: AUC = {roc_auc:.3f}")

#===========L1 Vs L2=================


# Train models with different regularization
models_regularization = {
    'No Regularization (C=1000)': LogisticRegression(C=1000, penalty='l2', random_state=42, max_iter=1000),
    'L2 Light (C=1.0)': LogisticRegression(C=1.0, penalty='l2', random_state=42, max_iter=1000),
    'L2 Strong (C=0.1)': LogisticRegression(C=0.1, penalty='l2', random_state=42, max_iter=1000),
    'L1 Light (C=1.0)': LogisticRegression(C=1.0, penalty='l1', solver='liblinear', random_state=42),
    'L1 Strong (C=0.1)': LogisticRegression(C=0.1, penalty='l1', solver='liblinear', random_state=42),
}

# Get coefficients
coefficients = {}
for name, model in models_regularization.items():
    model.fit(X_train, y_train)
    coefficients[name] = model.coef_[0]

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# L2 regularization
ax = axes[0]
names_l2 = ['No Regularization (C=1000)', 'L2 Light (C=1.0)', 'L2 Strong (C=0.1)']
for idx, name in enumerate(names_l2):
    ax.plot(range(5), coefficients[name], marker='o', linewidth=2, markersize=8, label=name)
ax.set_xlabel('Features')
ax.set_ylabel('Coefficient Value')
ax.set_title('L2 Regularization: Smooth Shrinkage', fontweight='bold')
ax.set_xticks(range(5))
ax.set_xticklabels(['Age', 'BMI', 'Glucose', 'BP', 'Insulin'], rotation=45)
ax.legend()
ax.grid(True, alpha=0.3)

# L1 regularization
ax = axes[1]
names_l1 = ['L1 Light (C=1.0)', 'L1 Strong (C=0.1)']
for idx, name in enumerate(names_l1):
    ax.plot(range(5), coefficients[name], marker='s', linewidth=2, markersize=8, label=name)
ax.plot(range(5), coefficients['No Regularization (C=1000)'], 'k--', alpha=0.5, label='No Reg (baseline)')
ax.set_xlabel('Features')
ax.set_ylabel('Coefficient Value')
ax.set_title('L1 Regularization: Forces Zeros', fontweight='bold')
ax.set_xticks(range(5))
ax.set_xticklabels(['Age', 'BMI', 'Glucose', 'BP', 'Insulin'], rotation=45)
ax.legend()
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='red', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# Print coefficients table
print("\n📊 Coefficient Values by Model:\n")
df_coef = pd.DataFrame(coefficients, index=['Age', 'BMI', 'Glucose', 'BP', 'Insulin']).T
print(df_coef.round(4))

#===============C tuning=============
# Train models with different C values
c_values = [0.001, 0.01, 0.1, 1.0, 10, 100, 1000]

train_scores = []
test_scores = []
coefficients_by_c = {}

for c in c_values:
    model = LogisticRegression(C=c, penalty='l2', random_state=42, max_iter=1000)
    model.fit(X_train, y_train)

    train_scores.append(model.score(X_train, y_train))
    test_scores.append(model.score(X_test, y_test))
    coefficients_by_c[c] = np.abs(model.coef_[0]).mean()  # Mean absolute coefficient

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Training vs Test Accuracy
ax = axes[0]
ax.semilogx(c_values, train_scores, 'o-', linewidth=2, markersize=8, label='Training Accuracy', color='#1f77b4')
ax.semilogx(c_values, test_scores, 's-', linewidth=2, markersize=8, label='Test Accuracy', color='#ff7f0e')
ax.set_xlabel('C (Regularization Strength)', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('🎯 Overfitting vs Underfitting: Finding Sweet Spot', fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.axvline(x=1.0, color='green', linestyle='--', alpha=0.7, label='Optimal C')

# Annotate
ax.annotate('Overfitting\n(High C)', xy=(1000, train_scores[-1]), xytext=(100, 0.70),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')
ax.annotate('Underfitting\n(Low C)', xy=(0.001, test_scores[0]), xytext=(0.01, 0.65),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')

# Plot 2: Coefficient Magnitude
ax = axes[1]
ax.loglog(c_values, list(coefficients_by_c.values()), 'o-', linewidth=2.5, markersize=10, color='#2ca02c')
ax.set_xlabel('C (Regularization Strength)', fontsize=12)
ax.set_ylabel('Mean |Coefficient|', fontsize=12)
ax.set_title('📉 Coefficient Shrinkage with C', fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
ax.axvline(x=1.0, color='green', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

print("\n📊 C Tuning Results:\n")
print(f"{'C Value':<10} {'Train Acc':<12} {'Test Acc':<12} {'Mean |Coef|':<12}")
print("-" * 50)
for c, train, test in zip(c_values, train_scores, test_scores):
    print(f"{c:<10.3f} {train:<12.4f} {test:<12.4f} {coefficients_by_c[c]:<12.4f}")

# Find optimal C
optimal_idx = np.argmax(test_scores)
optimal_c = c_values[optimal_idx]
print(f"\n🏆 Best C = {optimal_c} (Test Accuracy = {test_scores[optimal_idx]:.4f})")

print("🩺 WHAT DIFFERENT C VALUES MEAN IN MEDICINE:\n")

scenarios = {
    'C = 0.001 (Strong Regularization)': {
        'Behavior': 'Very conservative, ignores patient details',
        'Sensitivity': '~65%  (Misses some diseases)',
        'Specificity': '~95%  (Few false alarms)',
        'Use Case': 'Expensive/invasive follow-up tests',
        'Example': 'Heart surgery screening (only certain cases)',
    },

    'C = 0.1 (Moderate Regularization)': {
        'Behavior': 'Balanced approach, reduces noise',
        'Sensitivity': '~80%  (Catches most diseases)',
        'Specificity': '~92%  (Manageable false alarms)',
        'Use Case': 'Routine screening',
        'Example': 'Annual diabetes risk screening',
    },

    'C = 1.0 (Light Regularization) [RECOMMENDED]': {
        'Behavior': 'Uses patient details but still careful',
        'Sensitivity': '~87%  (Catches diseases)',
        'Specificity': '~97%  (Very few false alarms)',
        'Use Case': 'General diagnostic',
        'Example': 'Diabetes diagnosis in clinic',
    },

    'C = 100 (Weak Regularization)': {
        'Behavior': 'Trusts training data heavily, risky',
        'Sensitivity': '~92%  (Catches almost all)',
        'Specificity': '~90%  (More false alarms)',
        'Use Case': 'When missing disease is critical',
        'Example': 'Cancer screening (can\'t miss it!)',
    },

    'C = 1000 (No Regularization)': {
        'Behavior': 'Overfits to training data',
        'Sensitivity': '~95%  (Overfitting on test data)',
        'Specificity': '~88%  (Many false alarms)',
        'Use Case': 'AVOID in production',
        'Example': 'High risk of model failure',
    }
}

for c_desc, details in scenarios.items():
    print(f"\n{'=' * 60}")
    print(f"⚙️  {c_desc}")
    print(f"{'=' * 60}")
    for key, value in details.items():
        print(f"  {key:20s}: {value}")

#======gridesearch : finding optimal C=====
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score

# Define C values to test
param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

# GridSearchCV tests all combinations and picks best
model = LogisticRegression(penalty='l2', random_state=42, max_iter=1000)
grid_search = GridSearchCV(
    model,
    param_grid,
    cv=5,  # 5-fold cross-validation (test on 5 different splits)
    scoring='roc_auc',  # Use ROC-AUC as metric
    n_jobs=-1  # Use all CPU cores
)

grid_search.fit(X_train, y_train)

print("🔍 GridSearchCV Results:")
print(f"\nBest C: {grid_search.best_params_['C']}")
print(f"Best ROC-AUC: {grid_search.best_score_:.4f}")

# Show all results
results_df = pd.DataFrame(grid_search.cv_results_)
print("\n📊 All Results:")
print(results_df[['param_C', 'mean_test_score', 'std_test_score']])

# Use best model
best_model = grid_search.best_estimator_
final_auc = roc_auc_score(y_test, best_model.predict_proba(X_test)[:, 1])
print(f"\n✅ Final Test AUC with Best C: {final_auc:.4f}")
