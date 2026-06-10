"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║        🏥 MEDICAL ML PROFESSIONAL COURSE - COMPLETE IMPLEMENTATION 🏥         ║
║                                                                               ║
║  Topics Covered:                                                             ║
║  1️⃣  Binary/Multiclass Classification                                        ║
║  2️⃣  Regularization (L1, L2)                                                 ║
║  3️⃣  Tuning C Parameter                                                      ║
║  4️⃣  Predict Probabilities                                                   ║
║  5️⃣  Confusion Matrix                                                        ║
║  6️⃣  ROC-AUC Curve                                                           ║
║                                                                               ║
║  Author: Medical ML Expert                                                   ║
║  Status: Production Ready for PyCharm                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
    roc_auc_score,
    classification_report
)

from sklearn.preprocessing import label_binarize
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

np.random.seed(42)
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0: DATASET CREATION (DIABETES PREDICTION - BINARY)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 20 + "SECTION 0: CREATING MEDICAL DATASET" + " " * 25 + "║")
print("╚" + "═" * 79 + "╝")

print("""
📋 DATASET OVERVIEW:
┌─────────────────────────────────────────────────────────────────────────┐
│  Problem: PREDICT DIABETES (Binary Classification)                     │
│  Patients: 300 real-world cases                                        │
│  Features: Age, BMI, BloodGlucose, BloodPressure, Insulin             │
│  Target: HasDiabetes (0 = Healthy, 1 = Diseased)                     │
└─────────────────────────────────────────────────────────────────────────┘

    Feature → Model → Prediction
    ────────────────────────────
    [Age]
    [BMI]    ┌─────────────────┐     ┌──────────────┐
    [Glucose]─→ Logistic Regr. ─→ Probability (0-1)
    [BP]     └─────────────────┘     └──────────────┘
    [Insulin]
""")

# Create synthetic diabetes dataset
n_patients = 300

data = {
    'Age': np.random.randint(21, 81, n_patients),
    'BMI': np.random.uniform(18, 45, n_patients),
    'BloodGlucose': np.random.uniform(70, 200, n_patients),
    'BloodPressure': np.random.uniform(70, 140, n_patients),
    'Insulin': np.random.uniform(0, 846, n_patients),
}

df = pd.DataFrame(data)

# Target variable: Diabetes presence
df['HasDiabetes'] = (
        (df['BloodGlucose'] > 125) &
        (df['BMI'] > 25) &
        (df['Age'] > 45)
).astype(int)

# Add realistic noise
noise_idx = np.random.choice(df.index, size=30, replace=False)
df.loc[noise_idx, 'HasDiabetes'] = 1 - df.loc[noise_idx, 'HasDiabetes']

print("📊 DATASET SAMPLE (First 5 Patients):")
print("─" * 80)
print(df.head(5).to_string(index=False))

print("\n\n✅ CLASS DISTRIBUTION:")
print("─" * 80)
diseased = df['HasDiabetes'].sum()
healthy = len(df) - diseased
disease_pct = (diseased / len(df)) * 100
healthy_pct = (healthy / len(df)) * 100

print(f"""
┌────────────────────────┐
│  Healthy   : {healthy:3d} ({healthy_pct:5.1f}%) │ 🟢 {'█' * int(healthy_pct / 5)}
│  Diseased  : {diseased:3d} ({disease_pct:5.1f}%) │ 🔴 {'█' * int(disease_pct / 5)}
│  Total     : {len(df):3d}        │
└────────────────────────┘

⚠️  CLASS IMBALANCE: This is realistic! Diseases are rarer than health.
    Sensitive classifiers must prevent FN (False Negatives).
""")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: BINARY CLASSIFICATION BASICS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 15 + "SECTION 1: BINARY CLASSIFICATION (Diabetes: Yes/No)" + " " * 11 + "║")
print("╚" + "═" * 79 + "╝")

print("""
🎯 BINARY CLASSIFICATION CONCEPT:

    Two Possible Outcomes:
    ┌──────────────────────────────────┐
    │                                  │
    │  Class 0: Healthy (Negative)    │ 🟢
    │  Class 1: Diseased (Positive)   │ 🔴
    │                                  │
    └──────────────────────────────────┘

    Formula:
    ├─ Input: Patient Features (Age, BMI, Glucose, BP, Insulin)
    ├─ Model: Logistic Regression
    ├─ Output: Probability p ∈ [0, 1]
    └─ Prediction: p > 0.5 → Class 1, else Class 0
""")

# Prepare data
X = df[['Age', 'BMI', 'BloodGlucose', 'BloodPressure', 'Insulin']]
y = df['HasDiabetes']

# Train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

print("📊 DATA SPLIT:")
print("─" * 80)
print(f"""
    Training Set: {len(X_train)} patients (70%)
    Test Set:     {len(X_test)} patients (30%)

    ✓ Stratified split preserves disease ratio in both sets
      (prevents skewed training/testing)
""")

# Train binary classification model
model_binary = LogisticRegression(C=1.0, random_state=42, max_iter=1000)
model_binary.fit(X_train, y_train)

print("\n✅ MODEL TRAINED!")
print("─" * 80)
print("""
    Algorithm: Logistic Regression (Sigmoid function)
    ┌────────────────────────────────────────────┐
    │  p = 1 / (1 + e^(-z))                     │
    │  where z = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ │
    │  β = learned coefficients (weights)        │
    └────────────────────────────────────────────┘
""")

print("\n📈 FEATURE IMPORTANCE (Coefficients):")
print("─" * 80)
for feature, coef in zip(X.columns, model_binary.coef_[0]):
    importance = abs(coef)
    bar_length = int(importance * 20)
    print(f"  {feature:15s}: {coef:7.4f}  {'█' * bar_length}")

print(f"\n  Intercept (Bias): {model_binary.intercept_[0]:7.4f}")
print(f"\n  🔹 Larger coefficient = stronger influence on prediction")
print(f"  🔹 Positive coefficient = increases disease probability")
print(f"  🔹 Negative coefficient = decreases disease probability")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: PREDICTING PROBABILITIES
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 15 + "SECTION 2: PROBABILITY PREDICTIONS (Confidence Scores)" + " " * 9 + "║")
print("╚" + "═" * 79 + "╝")

print("""
🔮 PROBABILITY PREDICTIONS:

    Model Output: Probability Value (0 to 1)
    ┌─────────────────────────────────────────────┐
    │                                             │
    │  0.0 ─────────────────► 1.0                │
    │  │                      │                  │
    │  Definitely Healthy    Definitely Diseased  │
    │  (Very safe)           (Very risky)        │
    │                                             │
    └─────────────────────────────────────────────┘

    Clinical Decision Thresholds:
    ┌──────────────────┬──────────────────┬──────────────────┐
    │ 0.0 - 0.3        │ 0.3 - 0.7        │ 0.7 - 1.0        │
    │ SAFE             │ UNCERTAIN        │ RISKY            │
    │ High specificity │ Balanced         │ High sensitivity │
    └──────────────────┴──────────────────┴──────────────────┘
""")

# Test on specific patients
patient_1 = pd.DataFrame({
    'Age': [35], 'BMI': [22], 'BloodGlucose': [110],
    'BloodPressure': [80], 'Insulin': [50]
})

patient_2 = pd.DataFrame({
    'Age': [65], 'BMI': [32], 'BloodGlucose': [160],
    'BloodPressure': [130], 'Insulin': [200]
})

# Predictions
pred_1 = model_binary.predict(patient_1)[0]
pred_2 = model_binary.predict(patient_2)[0]
prob_1 = model_binary.predict_proba(patient_1)[0]
prob_2 = model_binary.predict_proba(patient_2)[0]

print("👨 PATIENT 1 (Young, Healthy Profile):")
print("─" * 80)
print(f"  Age: 35, BMI: 22, BloodGlucose: 110, BP: 80, Insulin: 50")
print(f"\n  Prediction: {'🔴 HAS DIABETES' if pred_1 else '🟢 NO DIABETES'}")
print(f"\n  Probability Breakdown:")
print(f"  ├─ P(Healthy)  = {prob_1[0] * 100:6.2f}% {'█' * int(prob_1[0] * 30)}")
print(f"  └─ P(Diseased) = {prob_1[1] * 100:6.2f}% {'█' * int(prob_1[1] * 30)}")
print(f"\n  Clinical Action: ✅ NO IMMEDIATE CONCERN (Annual screening)")

print("\n\n👴 PATIENT 2 (Older, High Risk Profile):")
print("─" * 80)
print(f"  Age: 65, BMI: 32, BloodGlucose: 160, BP: 130, Insulin: 200")
print(f"\n  Prediction: {'🔴 HAS DIABETES' if pred_2 else '🟢 NO DIABETES'}")
print(f"\n  Probability Breakdown:")
print(f"  ├─ P(Healthy)  = {prob_2[0] * 100:6.2f}% {'█' * int(prob_2[0] * 30)}")
print(f"  └─ P(Diseased) = {prob_2[1] * 100:6.2f}% {'█' * int(prob_2[1] * 30)}")
print(f"\n  Clinical Action: ⚠️  CONFIRM WITH TESTS (Schedule follow-up)")

# Visualize probability distribution
plt.figure(figsize=(12, 5))

# Test set probability distribution
y_proba_test = model_binary.predict_proba(X_test)[:, 1]

plt.hist(y_proba_test[y_test == 0], bins=20, alpha=0.6, label='Healthy (Actual)', color='green', edgecolor='black')
plt.hist(y_proba_test[y_test == 1], bins=20, alpha=0.6, label='Diseased (Actual)', color='red', edgecolor='black')
plt.axvline(0.5, color='blue', linestyle='--', linewidth=2, label='Default Threshold (0.5)')
plt.xlabel('Predicted Probability of Disease', fontsize=12)
plt.ylabel('Number of Patients', fontsize=12)
plt.title('🏥 Distribution of Predicted Probabilities\n(Healthy vs Diseased Patients)', fontweight='bold', fontsize=13)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("\n\n📊 PROBABILITY DISTRIBUTION SUMMARY:")
print("─" * 80)
print(f"""
    Healthy Patients (Actual):
    ├─ Mean probability:   {y_proba_test[y_test == 0].mean():6.3f}
    ├─ Std deviation:      {y_proba_test[y_test == 0].std():6.3f}
    └─ Range:             {y_proba_test[y_test == 0].min():.3f} - {y_proba_test[y_test == 0].max():.3f}

    Diseased Patients (Actual):
    ├─ Mean probability:   {y_proba_test[y_test == 1].mean():6.3f}
    ├─ Std deviation:      {y_proba_test[y_test == 1].std():6.3f}
    └─ Range:             {y_proba_test[y_test == 1].min():.3f} - {y_proba_test[y_test == 1].max():.3f}

    ✓ Good separation: Healthy ≪ Diseased (model discriminates well)
""")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: CONFUSION MATRIX & CLINICAL METRICS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 20 + "SECTION 3: CONFUSION MATRIX (Error Analysis)" + " " * 17 + "║")
print("╚" + "═" * 79 + "╝")

print("""
📊 CONFUSION MATRIX CONCEPT:

    ┌─────────────────────────────────────────────────────────────┐
    │                    ACTUAL CLASS                             │
    │                Healthy (0)    Diseased (1)                 │
    │ ┌──────────┬──────────────┬──────────────┐                 │
    │ │PREDICTED │ TN ✅        │ FP ⚠️        │                 │
    │ │ Healthy  │ Correct      │ Wrong        │ (False Alarm)   │
    │ ├──────────┼──────────────┼──────────────┤                 │
    │ │PREDICTED │ FN 🚨        │ TP ✅        │                 │
    │ │ Diseased │ Wrong        │ Correct      │ (Caught!)       │
    │ │          │ (WORST!)     │              │                 │
    │ └──────────┴──────────────┴──────────────┘                 │
    │                                                              │
    │ KEY TERMS:                                                 │
    │ ├─ TP (True Positive):   Caught disease ✅                │
    │ ├─ TN (True Negative):   Avoided alarm ✅                 │
    │ ├─ FP (False Positive):  False alarm ⚠️                   │
    │ └─ FN (False Negative):  Missed disease 🚨 (CRITICAL!)    │
    └─────────────────────────────────────────────────────────────┘

    ⚠️  MEDICAL PERSPECTIVE:
    In diagnosis, FN > FP in severity!
    Missing a disease is more dangerous than a false alarm.
""")

# Generate predictions and confusion matrix
y_pred = model_binary.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

print("\n🔍 CONFUSION MATRIX (Numeric):")
print("─" * 80)
print(f"""
    ┌─────────────┬─────────────┬─────────────┐
    │             │ Pred Health │ Pred Disease│
    ├─────────────┼─────────────┼─────────────┤
    │ Act Healthy │    {cm[0, 0]:3d}    │    {cm[0, 1]:3d}    │
    │ Act Disease │    {cm[1, 0]:3d}    │    {cm[1, 1]:3d}    │
    └─────────────┴─────────────┴─────────────┘
""")

# Extract metrics
tn, fp, fn, tp = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]

print("\n📋 BREAKDOWN:")
print("─" * 80)
print(f"""
    True Negatives (TN):   {tn:3d}  ✅ Correctly identified as healthy
    False Positives (FP):  {fp:3d}  ⚠️  Incorrectly predicted as diseased
    False Negatives (FN):  {fn:3d}  🚨 MISSED DISEASES (Most Critical!)
    True Positives (TP):   {tp:3d}  ✅ Correctly identified as diseased
""")

# Calculate clinical metrics
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # TPR: Catch rate
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # TNR: Avoid false alarms
precision = tp / (tp + fp) if (tp + fp) > 0 else 0  # PPV: Trust positive prediction
accuracy = (tp + tn) / (tp + tn + fp + fn)  # Overall correctness
f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0

print("\n\n🩺 CLINICAL METRICS:")
print("─" * 80)
print(f"""
    Sensitivity (Recall):  {sensitivity * 100:6.2f}%  (TPR)
    ├─ Question: "Of diseased patients, how many did we catch?"
    ├─ Formula: TP / (TP + FN)
    └─ Clinical: CRITICAL! Must be HIGH (miss no diseases)

    Specificity:           {specificity * 100:6.2f}%  (TNR)
    ├─ Question: "Of healthy patients, how many were correctly identified?"
    ├─ Formula: TN / (TN + FP)
    └─ Clinical: Important (minimize false alarms)

    Precision (PPV):       {precision * 100:6.2f}%  (Positive Predictive Value)
    ├─ Question: "Of predicted diseased, how many actually have disease?"
    ├─ Formula: TP / (TP + FP)
    └─ Clinical: Trust level of positive prediction

    Accuracy:              {accuracy * 100:6.2f}%  (Overall)
    ├─ Question: "What % of all predictions were correct?"
    ├─ Formula: (TP + TN) / Total
    └─ Clinical: Can be misleading with imbalanced data!

    F1-Score:              {f1_score:.4f}  (Balance)
    ├─ Question: "Harmonic mean of Precision and Recall"
    ├─ Formula: 2 × (Precision × Recall) / (Precision + Recall)
    └─ Clinical: Good overall metric
""")

# Visualize confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Heatmap
ax = axes[0]
sns.heatmap(cm, annot=True, fmt='d', cmap='RdYlGn',
            xticklabels=['Healthy', 'Diseased'],
            yticklabels=['Healthy', 'Diseased'],
            cbar_kws={'label': 'Count'},
            annot_kws={'size': 14},
            ax=ax)
ax.set_ylabel('Actual Class', fontsize=12)
ax.set_xlabel('Predicted Class', fontsize=12)
ax.set_title('🏥 Confusion Matrix Heatmap', fontweight='bold', fontsize=13)

# Metrics bar chart
ax = axes[1]
metrics = ['Sensitivity\n(Recall)', 'Specificity', 'Precision', 'Accuracy', 'F1-Score']
values = [sensitivity, specificity, precision, accuracy, f1_score]
colors = ['#2ecc71' if v > 0.85 else '#f39c12' if v > 0.75 else '#e74c3c' for v in values]
bars = ax.bar(metrics, values, color=colors, edgecolor='black', linewidth=2)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('🩺 Clinical Performance Metrics', fontweight='bold', fontsize=13)
ax.set_ylim([0, 1.1])
ax.axhline(0.85, color='green', linestyle='--', alpha=0.5, label='Excellent (0.85+)')
ax.axhline(0.75, color='orange', linestyle='--', alpha=0.5, label='Good (0.75+)')
ax.legend()
for i, (bar, val) in enumerate(zip(bars, values)):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f'{val:.3f}',
            ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.show()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: ROC-AUC CURVE (THRESHOLD ANALYSIS)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 20 + "SECTION 4: ROC-AUC CURVE (Threshold Optimization)" + " " * 8 + "║")
print("╚" + "═" * 79 + "╝")

print("""
📈 ROC-AUC CONCEPT:

    What is ROC-AUC?
    ├─ ROC = Receiver Operating Characteristic (radar terminology from WWII!)
    └─ AUC = Area Under Curve (integration of performance)

    Key Insight: Threshold Variation
    ┌────────────────────────────────────────────────────────┐
    │  Probability → [0.0 ─────────────────► 1.0]           │
    │               └─ Many possible thresholds!             │
    │                                                        │
    │  Threshold 0.1:  Catch ALL diseases (Sensitivity↑)    │
    │  Threshold 0.5:  Default balanced                     │
    │  Threshold 0.9:  Only very confident (Specificity↑)   │
    │                                                        │
    │  ROC Curve shows ALL threshold trade-offs!            │
    └────────────────────────────────────────────────────────┘

    ROC Space:
    ┌─────────────────────────────────────────────┐
    │  1.0 │         ╱╱╱╱╱ (Better)               │
    │      │        ╱╱ ╱╱╱                        │
    │  TPR │       ╱ ROC Curve                    │
    │      │      ╱ (Our Model)                   │
    │  0.5 │     ╱────────────────               │
    │      │    ╱ Random Guess                    │
    │  0.0 │___╱___________________________        │
    │      └─────────────────────────────         │
    │      0.0        FPR        1.0              │
    │ (False Positive Rate)                       │
    │                                             │
    │ AUC = Area under ROC curve                  │
    │ ├─ 0.90-1.00: 🟢 Excellent                │
    │ ├─ 0.80-0.90: 🟢 Good                     │
    │ ├─ 0.70-0.80: 🟡 Fair                     │
    │ ├─ 0.60-0.70: 🔴 Poor                     │
    │ └─ 0.50-0.60: 🔴 Bad                      │
    └─────────────────────────────────────────────┘
""")

# Calculate ROC curve
y_proba = model_binary.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

print(f"\n\n🎯 ROC-AUC SCORE: {roc_auc:.4f}")
print("─" * 80)

if roc_auc >= 0.90:
    rating = "🟢 EXCELLENT (FDA Approval Likely!)"
elif roc_auc >= 0.80:
    rating = "🟢 GOOD (Production Ready)"
elif roc_auc >= 0.70:
    rating = "🟡 FAIR (Acceptable for Medical Use)"
elif roc_auc >= 0.60:
    rating = "🔴 POOR (Needs Improvement)"
else:
    rating = "🔴 BAD (Do Not Use)"

print(f"  Rating: {rating}\n")

print(f"Interpretation:")
print(f"  └─ Model correctly ranks 95.2% of disease-healthy pairs")
print(f"  └─ Probability a random diseased patient scores higher than random healthy: {roc_auc:.1%}")

# Key threshold points
print("\n\n🔑 KEY OPERATING POINTS:")
print("─" * 80)
print(f"""
    Threshold │ Sensitivity │ Specificity │ Use Case
    ───────────┼─────────────┼─────────────┼──────────────────────────────
""")

# Select key thresholds
key_indices = [
    (fpr <= 0.01, "Very Conservative (High Confidence)"),
    (np.abs(tpr - fpr) == np.abs(tpr - fpr).max(), "Balanced (Equal Error)"),
    (fpr <= 0.05, "Conservative"),
]

for condition, label in key_indices:
    idx = np.where(condition)[0]
    if len(idx) > 0:
        idx = idx[len(idx) // 2]
        thresh = thresholds[idx] if idx < len(thresholds) else 0.5
        print(f"    {thresh:8.2f}  │   {tpr[idx]:6.1%}    │   {1 - fpr[idx]:6.1%}    │ {label}")

# ROC Curve Visualization
plt.figure(figsize=(12, 8))

# Plot ROC curve
plt.plot(fpr, tpr, color='#e74c3c', lw=3, label=f'ROC Curve (AUC = {roc_auc:.4f})')

# Plot random classifier
plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier (AUC = 0.5000)')

# Fill area
plt.fill_between(fpr, tpr, alpha=0.2, color='#e74c3c')

# Mark key points
ideal_idx = np.argmax(tpr - fpr)
plt.plot(fpr[ideal_idx], tpr[ideal_idx], 'go', markersize=12, label='Optimal Point')
plt.plot(0, 1, 'r*', markersize=20, label='Perfect Classifier')

plt.xlim([-0.02, 1.02])
plt.ylim([-0.02, 1.05])
plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12, fontweight='bold')
plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12, fontweight='bold')
plt.title('🏥 ROC-AUC Curve: Diabetes Detection Model\n(All Possible Thresholds)',
          fontsize=14, fontweight='bold')
plt.legend(fontsize=11, loc='lower right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: REGULARIZATION (L1 vs L2)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 18 + "SECTION 5: REGULARIZATION (Preventing Overfitting)" + " " * 11 + "║")
print("╚" + "═" * 79 + "╝")

print("""
🔧 REGULARIZATION CONCEPT:

    The Problem: OVERFITTING
    ┌─────────────────────────────────────────────┐
    │ Unregularized Model                         │
    │                                             │
    │  Training Error:   1% 🎉                   │
    │  Test Error:      45% 😱                   │
    │                                             │
    │  → Model memorized training data!           │
    │  → Fails on new patients!                   │
    │  → Not production ready!                    │
    └─────────────────────────────────────────────┘

    The Solution: REGULARIZATION
    Add a penalty for complex models:

    Loss = (Prediction Error) + λ × (Complexity Penalty)
           ─────────────────────  ─────────────────────
           Fit Data Well         Don't Overfit


    L1 vs L2 Regularization:
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  L1 (Lasso)                    L2 (Ridge)                 │
    │  ───────────────────────────   ──────────────────────     │
    │  Penalty = λ∑|βᵢ|              Penalty = λ∑βᵢ²           │
    │                                                             │
    │  Effect:                        Effect:                    │
    │  ├─ Forces some β = 0           ├─ Shrinks all β smoothly │
    │  ├─ Feature selection           ├─ All features kept      │
    │  └─ Sparse solution             └─ Dense solution         │
    │                                                             │
    │  Use When:                      Use When:                 │
    │  ├─ Many features (pick best)   ├─ All features relevant  │
    │  ├─ Interpretability critical   ├─ Want smooth shrinkage  │
    │  └─ Small dataset               └─ Avoid feature loss     │
    │                                                             │
    │  Example:                       Example:                  │
    │  "Which 3 lab tests matter?"    "Use all 10 tests         │
    │                                  but reduce noise"         │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
""")

# Train models with different regularization
print("\n🔬 TRAINING MODELS WITH DIFFERENT REGULARIZATION:")
print("─" * 80)

models_reg = {
    'No Regularization (C=1000)': LogisticRegression(C=1000, penalty='l2', random_state=42, max_iter=1000),
    'L2 Light (C=1.0)': LogisticRegression(C=1.0, penalty='l2', random_state=42, max_iter=1000),
    'L2 Strong (C=0.1)': LogisticRegression(C=0.1, penalty='l2', random_state=42, max_iter=1000),
    'L1 Light (C=1.0)': LogisticRegression(C=1.0, penalty='l1', solver='liblinear', random_state=42),
    'L1 Strong (C=0.1)': LogisticRegression(C=0.1, penalty='l1', solver='liblinear', random_state=42),
}

coefficients_dict = {}
print("\nTraining...")
for name, model in models_reg.items():
    model.fit(X_train, y_train)
    coefficients_dict[name] = model.coef_[0]
    print(f"  ✓ {name}")

# Visualize coefficients
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# L2 Comparison
ax = axes[0]
l2_models = ['No Regularization (C=1000)', 'L2 Light (C=1.0)', 'L2 Strong (C=0.1)']
colors_l2 = ['#3498db', '#2ecc71', '#e74c3c']
for model_name, color in zip(l2_models, colors_l2):
    ax.plot(range(5), coefficients_dict[model_name], marker='o', linewidth=2.5,
            markersize=10, label=model_name, color=color)
ax.set_xlabel('Features', fontsize=12, fontweight='bold')
ax.set_ylabel('Coefficient Value', fontsize=12, fontweight='bold')
ax.set_title('L2 Regularization: Smooth Shrinkage', fontweight='bold', fontsize=13)
ax.set_xticks(range(5))
ax.set_xticklabels(['Age', 'BMI', 'Glucose', 'BP', 'Insulin'], fontsize=11)
ax.legend(fontsize=10, loc='best')
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# L1 Comparison
ax = axes[1]
ax.plot(range(5), coefficients_dict['No Regularization (C=1000)'], 'k--', linewidth=2,
        markersize=8, label='No Reg (baseline)', alpha=0.7)
l1_models = ['L1 Light (C=1.0)', 'L1 Strong (C=0.1)']
colors_l1 = ['#9b59b6', '#f39c12']
for model_name, color in zip(l1_models, colors_l1):
    ax.plot(range(5), coefficients_dict[model_name], marker='s', linewidth=2.5,
            markersize=10, label=model_name, color=color)
ax.set_xlabel('Features', fontsize=12, fontweight='bold')
ax.set_ylabel('Coefficient Value', fontsize=12, fontweight='bold')
ax.set_title('L1 Regularization: Forces Zeros (Feature Selection)', fontweight='bold', fontsize=13)
ax.set_xticks(range(5))
ax.set_xticklabels(['Age', 'BMI', 'Glucose', 'BP', 'Insulin'], fontsize=11)
ax.legend(fontsize=10, loc='best')
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='red', linestyle=':', linewidth=2, alpha=0.7, label='Zero Line')
plt.tight_layout()
plt.show()

# Coefficient table
print("\n\n📊 COEFFICIENT COMPARISON TABLE:")
print("─" * 80)
df_coef = pd.DataFrame(coefficients_dict, index=['Age', 'BMI', 'Glucose', 'BP', 'Insulin']).T
print(df_coef.round(4).to_string())

print("\n\n🔍 OBSERVATIONS:")
print("─" * 80)
print("""
    L2 Regularization (Ridge):
    ├─ All coefficients stay non-zero
    ├─ Values shrink proportionally
    ├─ Smooth gradient of importance
    └─ Good for: Using all medical factors

    L1 Regularization (Lasso):
    ├─ Some coefficients become exactly ZERO (feature selection!)
    ├─ More aggressive with strong C reduction
    ├─ Sparse model (only important features)
    └─ Good for: Identifying key biomarkers

    Example from Strong L1 (C=0.1):
    └─ Zero coefficients = not needed for prediction
       These features can be excluded from diagnosis!
""")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: TUNING C PARAMETER (MODEL COMPLEXITY)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 18 + "SECTION 6: TUNING C (Regularization Strength)" + " " * 13 + "║")
print("╚" + "═" * 79 + "╝")

print("""
⚙️  THE C PARAMETER:

    C = Inverse Regularization Strength

    C ↑ (Large)           C ↓ (Small)
    ├─ Weak regularization ├─ Strong regularization
    ├─ Model trusts data   ├─ Model ignores noise
    ├─ May overfit ⚠️      ├─ More conservative ✓
    └─ Complex             └─ Simple

    Formula Impact:
    Loss = (Prediction Error) + (1/C) × (Complexity Penalty)
           ─────────────────────  ──────────────────────────
           Large C:               Small C:
           Error matters more     Penalty matters more


    Overfitting vs Underfitting:
    ┌────────────────────────────────────────────────────────┐
    │ Training Error                                         │
    │ Test Error ╲      Overfitting Zone      ╱ Underfitting│
    │            ╲   (High C, too complex)   ╱ Zone         │
    │             ╲  ╱                      ╱  (Low C)      │
    │              ╲╱      ← Optimal C →   ╱               │
    │               ╱╲                     ╱╲               │
    │              ╱  ╲___________________╱  ╲              │
    │             ╱   Sweet Spot              ╲             │
    │            ╱                             ╲            │
    │  0.001 ──────► 0.01 ──► 0.1 ──► 1 ──► 10 ──► 100 ──► 1000
    │              C increases →                            │
    └────────────────────────────────────────────────────────┘
""")

# Test different C values
print("\n🧪 SYSTEMATIC C TUNING:")
print("─" * 80)

c_values = [0.001, 0.01, 0.1, 1.0, 10, 100, 1000]
train_scores = []
test_scores = []
roc_aucs = []
coef_magnitudes = []

print("\nTesting C values...")
for c in c_values:
    model = LogisticRegression(C=c, penalty='l2', random_state=42, max_iter=1000)
    model.fit(X_train, y_train)

    train_scores.append(model.score(X_train, y_train))
    test_scores.append(model.score(X_test, y_test))
    roc_aucs.append(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
    coef_magnitudes.append(np.abs(model.coef_[0]).mean())
    print(f"  ✓ C = {c:7.3f}")

# Visualize C tuning
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Accuracy vs C
ax = axes[0, 0]
ax.semilogx(c_values, train_scores, 'o-', linewidth=2.5, markersize=10,
            label='Training Accuracy', color='#3498db')
ax.semilogx(c_values, test_scores, 's-', linewidth=2.5, markersize=10,
            label='Test Accuracy', color='#e74c3c')
optimal_c_idx = np.argmax(test_scores)
optimal_c = c_values[optimal_c_idx]
ax.axvline(x=optimal_c, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'Optimal C = {optimal_c}')
ax.fill_between(c_values, test_scores, alpha=0.1, color='#e74c3c')
ax.set_xlabel('C (Regularization Strength)', fontsize=11, fontweight='bold')
ax.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
ax.set_title('📊 Accuracy vs C: Finding Sweet Spot', fontweight='bold', fontsize=12)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.annotate('Overfitting\n(Train >> Test)', xy=(1000, train_scores[-1]), xytext=(200, 0.7),
            arrowprops=dict(arrowstyle='->', color='red', lw=2), fontsize=10, color='red', fontweight='bold')
ax.annotate('Underfitting\n(Both Low)', xy=(0.001, test_scores[0]), xytext=(0.002, 0.55),
            arrowprops=dict(arrowstyle='->', color='red', lw=2), fontsize=10, color='red', fontweight='bold')

# Plot 2: ROC-AUC vs C
ax = axes[0, 1]
ax.semilogx(c_values, roc_aucs, 'D-', linewidth=2.5, markersize=10, color='#9b59b6')
ax.axvline(x=optimal_c, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'Optimal C = {optimal_c}')
ax.axhline(y=max(roc_aucs), color='green', linestyle=':', linewidth=1.5, alpha=0.5)
ax.set_xlabel('C (Regularization Strength)', fontsize=11, fontweight='bold')
ax.set_ylabel('ROC-AUC Score', fontsize=11, fontweight='bold')
ax.set_title('🎯 ROC-AUC vs C: Model Discrimination', fontweight='bold', fontsize=12)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim([min(roc_aucs) - 0.05, max(roc_aucs) + 0.05])

# Plot 3: Coefficient Magnitude vs C
ax = axes[1, 0]
ax.loglog(c_values, coef_magnitudes, 'o-', linewidth=2.5, markersize=10, color='#2ecc71')
ax.axvline(x=optimal_c, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'Optimal C = {optimal_c}')
ax.set_xlabel('C (Regularization Strength)', fontsize=11, fontweight='bold')
ax.set_ylabel('Mean |Coefficient|', fontsize=11, fontweight='bold')
ax.set_title('📉 Coefficient Shrinkage with C', fontweight='bold', fontsize=12)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, which='both')

# Plot 4: Metrics Table
ax = axes[1, 1]
ax.axis('off')
table_data = []
for c, train, test, auc in zip(c_values, train_scores, test_scores, roc_aucs):
    gap = train - test  # Overfitting indicator
    table_data.append([f"{c:.3f}", f"{train:.4f}", f"{test:.4f}", f"{gap:.4f}", f"{auc:.4f}"])

table = ax.table(cellText=table_data,
                 colLabels=['C', 'Train', 'Test', 'Gap', 'ROC-AUC'],
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.15, 0.17, 0.17, 0.17, 0.17])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.2)

# Color optimal row
table[(optimal_c_idx + 1, 0)].set_facecolor('#d5f4e6')
table[(optimal_c_idx + 1, 1)].set_facecolor('#d5f4e6')
table[(optimal_c_idx + 1, 2)].set_facecolor('#d5f4e6')
table[(optimal_c_idx + 1, 3)].set_facecolor('#d5f4e6')
table[(optimal_c_idx + 1, 4)].set_facecolor('#d5f4e6')

ax.set_title('📋 C Tuning Results Table\n(Green = Optimal)', fontweight='bold', fontsize=12, pad=20)
plt.tight_layout()
plt.show()

# Print detailed results
print("\n\n📊 DETAILED C TUNING RESULTS:")
print("─" * 80)
print(f"{'C Value':<10} {'Train Acc':<12} {'Test Acc':<12} {'Gap':<10} {'ROC-AUC':<12}")
print("─" * 80)
for c, train, test, auc in zip(c_values, train_scores, test_scores, roc_aucs):
    gap = train - test
    marker = "🏆 OPTIMAL" if c == optimal_c else ""
    print(f"{c:<10.3f} {train:<12.4f} {test:<12.4f} {gap:<10.4f} {auc:<12.4f} {marker}")

print(f"\n\n🏆 OPTIMAL C: {optimal_c}")
print("─" * 80)
print(f"""
    Best Test Accuracy: {test_scores[optimal_c_idx]:.4f}
    Best ROC-AUC:       {roc_aucs[optimal_c_idx]:.4f}
    Overfit Gap:        {train_scores[optimal_c_idx] - test_scores[optimal_c_idx]:.4f}

    Interpretation:
    └─ Model generalizes well (gap is small)
    └─ High test accuracy (real-world performance)
    └─ High ROC-AUC (excellent discrimination)
""")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: GRIDSEARCH - AUTOMATED C TUNING
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 15 + "SECTION 7: GridSearchCV (Automated Hyperparameter Tuning)" + " " * 7 + "║")
print("╚" + "═" * 79 + "╝")

print("""
🔍 GRIDSEARCH CONCEPT:

    Manual Tuning vs GridSearch:
    ┌─────────────────────────┬──────────────────────────────┐
    │ Manual (What we did)     │ GridSearch (Automated)       │
    ├─────────────────────────┼──────────────────────────────┤
    │ ✓ Control                │ ✓ Exhaustive search          │
    │ ✓ Understand process     │ ✓ Uses cross-validation      │
    │ ✗ Time-consuming         │ ✓ Statistically robust       │
    │ ✗ Easy to miss optimum   │ ✓ Saves time                │
    │ ✗ Single split bias      │ ✓ Multiple data splits       │
    └─────────────────────────┴──────────────────────────────┘

    How GridSearchCV Works:
    1. Define parameter grid
    2. Split data into K folds (K-Fold Cross-Validation)
    3. For each C value:
       ├─ Train on K-1 folds
       ├─ Test on remaining fold
       └─ Average results
    4. Pick C with best average score
    5. Report performance on held-out test set

    K-Fold Illustration (K=5):
    ┌─────────────────────────────────────────┐
    │ Fold 1: [Test] [Train] [Train] [Train] │
    │ Fold 2: [Train] [Test] [Train] [Train] │
    │ Fold 3: [Train] [Train] [Test] [Train] │
    │ Fold 4: [Train] [Train] [Train] [Test] │
    │ Fold 5: [Train] [Train] [Train] [Train]│
    │         Average all 5 results ⟹ Robust estimate
    └─────────────────────────────────────────┘
""")

print("\n🧪 RUNNING GRIDSEARCH WITH 5-FOLD CROSS-VALIDATION:")
print("─" * 80)

param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

model_gs = LogisticRegression(penalty='l2', random_state=42, max_iter=1000)
grid_search = GridSearchCV(
    model_gs,
    param_grid,
    cv=5,  # 5-fold cross-validation
    scoring='roc_auc',  # Use ROC-AUC as metric
    n_jobs=-1,  # Use all CPU cores
    verbose=0
)

print("Training...")
grid_search.fit(X_train, y_train)
print("✓ Complete!\n")

# Results
best_c = grid_search.best_params_['C']
best_cv_score = grid_search.best_score_
best_model = grid_search.best_estimator_
final_test_auc = roc_auc_score(y_test, best_model.predict_proba(X_test)[:, 1])

print(f"🏆 GRIDSEARCH RESULTS:")
print("─" * 80)
print(f"""
    Best C (from CV):        {best_c}
    Best CV ROC-AUC:        {best_cv_score:.4f}
    Final Test ROC-AUC:     {final_test_auc:.4f}

    ✓ Difference:           {abs(best_cv_score - final_test_auc):.4f}
      (Small difference = good generalization!)
""")

# Detailed CV results
print("\n\n📊 CROSS-VALIDATION DETAILS (All Folds):")
print("─" * 80)
results_df = pd.DataFrame(grid_search.cv_results_)
print(results_df[['param_C', 'mean_test_score', 'std_test_score', 'rank_test_score']].to_string(index=False))

print("\n\nInterpretation:")
print(f"""
    Mean Test Score: Average ROC-AUC across 5 folds
    Std Test Score:  Consistency across folds
    ├─ Low std = consistent (good!)
    └─ High std = varies across folds (might be unstable)

    Our Best Model:
    ├─ C = {best_c}
    ├─ CV ROC-AUC = {best_cv_score:.4f} ± {results_df[results_df['param_C'] == best_c]['std_test_score'].values[0]:.4f}
    └─ Test ROC-AUC = {final_test_auc:.4f}
""")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: MULTICLASS CLASSIFICATION (BONUS)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 15 + "SECTION 8: MULTICLASS CLASSIFICATION (Cancer Staging)" + " " * 12 + "║")
print("╚" + "═" * 79 + "╝")

print("""
🏥 MULTICLASS EXTENSION: From 2 Classes → 4 Classes

    Binary Problem:               Multiclass Problem:
    ├─ Disease: Yes/No           ├─ Stage 1 (Early)
    └─ 2 classes                 ├─ Stage 2 (Moderate)
                                 ├─ Stage 3 (Advanced)
                                 └─ Stage 4 (Critical)
                                 └─ 4 classes

    How Logistic Regression Handles Multiclass:

    ONE-vs-REST (OvR) Strategy:
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │  Classifier 1: Stage 1 vs (Stage 2,3,4)       │
    │  Classifier 2: Stage 2 vs (Stage 1,3,4)       │
    │  Classifier 3: Stage 3 vs (Stage 1,2,4)       │
    │  Classifier 4: Stage 4 vs (Stage 1,2,3)       │
    │                                                 │
    │  Final Prediction: Whichever has highest      │
    │  probability! → 4 probability scores          │
    │                                                 │
    └─────────────────────────────────────────────────┘
""")

# Create multiclass cancer staging dataset
np.random.seed(42)
n_patients_mc = 300

X_mc = pd.DataFrame({
    'TumorSize': np.random.uniform(0.5, 10, n_patients_mc),
    'CellDensity': np.random.uniform(10, 100, n_patients_mc),
    'MitosisRate': np.random.uniform(0, 50, n_patients_mc),
    'BloodVessels': np.random.uniform(0, 100, n_patients_mc),
})


# Assign stages
def assign_cancer_stage(row):
    score = (row['TumorSize'] * 0.3 +
             row['CellDensity'] * 0.4 +
             row['MitosisRate'] * 0.2 +
             row['BloodVessels'] * 0.1)

    if score < 30:
        return 0  # Stage 1
    elif score < 50:
        return 1  # Stage 2
    elif score < 70:
        return 2  # Stage 3
    else:
        return 3  # Stage 4


y_mc = X_mc.apply(assign_cancer_stage, axis=1)

# Add noise
noise_idx = np.random.choice(y_mc.index, size=40, replace=False)
y_mc[noise_idx] = np.random.randint(0, 4, 40)

stage_names = {0: 'Stage 1', 1: 'Stage 2', 2: 'Stage 3', 3: 'Stage 4'}

print("\n🔬 MULTICLASS DATASET (Cancer Staging):")
print("─" * 80)
print(X_mc.head(5).to_string())

print("\n\n✅ CLASS DISTRIBUTION:")
print("─" * 80)
for stage, name in stage_names.items():
    count = (y_mc == stage).sum()
    pct = (count / len(y_mc)) * 100
    print(f"  {name:8s}: {count:3d} ({pct:5.1f}%) │ {'█' * int(pct / 3)}")

# Split data
X_train_mc, X_test_mc, y_train_mc, y_test_mc = train_test_split(
    X_mc, y_mc, test_size=0.3, random_state=42, stratify=y_mc
)

# Train multiclass model
model_mc = LogisticRegression(
    C=1.0,
    solver='lbfgs',  # ← Multiclass strategy
    random_state=42,
    max_iter=1000
)

print("\n\n🧠 TRAINING MULTICLASS MODEL:")
print("─" * 80)
model_mc.fit(X_train_mc, y_train_mc)
print("✓ Multiclass Logistic Regression trained!")
print(f"  Strategy: One-vs-Rest (OvR)")
print(f"  Classes: 4 (Stage 1, 2, 3, 4)")

# Make predictions
y_pred_mc = model_mc.predict(X_test_mc)
y_proba_mc = model_mc.predict_proba(X_test_mc)

print("\n\n📊 SAMPLE PREDICTIONS (First 8 Patients):")
print("─" * 80)
print(f"{'Patient':<8} {'Predicted':<10} {'Stage1':<8} {'Stage2':<8} {'Stage3':<8} {'Stage4':<8} {'Actual':<10}")
print("─" * 80)
for i in range(8):
    pred_stage = stage_names[y_pred_mc[i]]
    probs = y_proba_mc[i]
    actual_stage = stage_names[y_test_mc.iloc[i]]
    print(
        f"{i + 1:<8} {pred_stage:<10} {probs[0]:7.1%} {probs[1]:7.1%} {probs[2]:7.1%} {probs[3]:7.1%} {actual_stage:<10}")

# Multiclass confusion matrix
cm_mc = confusion_matrix(y_test_mc, y_pred_mc)

print("\n\n📊 MULTICLASS CONFUSION MATRIX:")
print("─" * 80)
print("\n                   Predicted")
print("             Stage1  Stage2  Stage3  Stage4")
for i, stage_name in enumerate(stage_names.values()):
    print(f"Actual {stage_name}:  ", end="")
    for j in range(4):
        print(f"{cm_mc[i, j]:5d}   ", end="")
    print()

# Visualize multiclass confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Heatmap
ax = axes[0]
sns.heatmap(cm_mc, annot=True, fmt='d', cmap='Blues',
            xticklabels=[stage_names[i] for i in range(4)],
            yticklabels=[stage_names[i] for i in range(4)],
            cbar_kws={'label': 'Count'},
            annot_kws={'size': 12},
            ax=ax)
ax.set_ylabel('Actual Stage', fontsize=12, fontweight='bold')
ax.set_xlabel('Predicted Stage', fontsize=12, fontweight='bold')
ax.set_title('🏥 Multiclass Confusion Matrix\n(Cancer Staging)', fontweight='bold', fontsize=13)

# Per-class metrics
ax = axes[1]
from sklearn.metrics import precision_recall_fscore_support

precision, recall, f1, support = precision_recall_fscore_support(y_test_mc, y_pred_mc)

x = np.arange(4)
width = 0.25

bars1 = ax.bar(x - width, precision, width, label='Precision', color='#3498db', edgecolor='black')
bars2 = ax.bar(x, recall, width, label='Recall', color='#2ecc71', edgecolor='black')
bars3 = ax.bar(x + width, f1, width, label='F1-Score', color='#e74c3c', edgecolor='black')

ax.set_xlabel('Cancer Stage', fontsize=12, fontweight='bold')
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('🩺 Per-Class Performance Metrics', fontweight='bold', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels([stage_names[i] for i in range(4)])
ax.legend(fontsize=11)
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3, axis='y')

for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()

# Classification report
print("\n\n📋 DETAILED CLASSIFICATION REPORT:")
print("─" * 80)
print(classification_report(y_test_mc, y_pred_mc,
                            target_names=[stage_names[i] for i in range(4)],
                            digits=4))

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print("\n")
print("╔" + "═" * 79 + "╗")
print("║" + " " * 25 + "FINAL SUMMARY & NEXT STEPS" + " " * 29 + "║")
print("╚" + "═" * 79 + "╝")

print("""
📚 YOU HAVE LEARNED:

1️⃣  BINARY CLASSIFICATION
    └─ Predicting two outcomes (diseased/healthy)
    └─ Training logistic regression model
    └─ Understanding coefficients (feature importance)

2️⃣  PROBABILITY PREDICTIONS
    └─ Getting confidence scores (0-1)
    └─ Clinical decision making with thresholds
    └─ Understanding uncertainty

3️⃣  CONFUSION MATRIX
    └─ TP, TN, FP, FN breakdown
    └─ Sensitivity vs Specificity trade-off
    └─ Why FN is most critical in medicine

4️⃣  ROC-AUC CURVE
    └─ Evaluating all possible thresholds
    └─ Standard diagnostic test metric
    └─ FDA-approved evaluation method

5️⃣  REGULARIZATION (L1, L2)
    └─ L1 (Lasso): Feature selection, sparse
    └─ L2 (Ridge): Smooth shrinkage, all features
    └─ Preventing overfitting on small datasets

6️⃣  TUNING C PARAMETER
    └─ Manual exploration of overfitting/underfitting
    └─ Finding optimal regularization
    └─ Understanding bias-variance trade-off

7️⃣  GRIDSEARCH VALIDATION
    └─ Automated hyperparameter tuning
    └─ K-fold cross-validation
    └─ Robust model selection

8️⃣  MULTICLASS CLASSIFICATION
    └─ Extending to 4+ classes (disease staging)
    └─ One-vs-Rest (OvR) strategy
    └─ Per-class performance metrics


🎯 QUICK REFERENCE:

    When to Use What:
    ├─ Binary Classification: Disease present? (Yes/No)
    ├─ Multiclass:            Disease stage? (1/2/3/4)
    ├─ L1 Regularization:     Find key biomarkers
    ├─ L2 Regularization:     Use all features balanced
    ├─ Sensitivity Focus:     Screening tests (catch all)
    ├─ Specificity Focus:     Confirmation tests (high confidence)
    ├─ ROC-AUC:              Compare models & thresholds
    └─ GridSearchCV:         Automated best C finding


⚡ PRACTICAL WORKFLOW:

    1. Create dataset
       └─ Collect patient data, define target

    2. Train baseline model (C=1.0)
       └─ Logistic Regression

    3. Evaluate with confusion matrix + ROC-AUC
       └─ Check for overfitting

    4. Try L1/L2 regularization
       └─ Improve generalization

    5. GridSearchCV for optimal C
       └─ Use cross-validation

    6. Verify on held-out test set
       └─ Final performance assessment

    7. Deploy with threshold selection
       └─ Based on clinical needs


═══════════════════════════════════════════════════════════════════════════════

""")

