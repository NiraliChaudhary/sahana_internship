"""
================================================================================
SUPPORT VECTOR MACHINE (SVM) FOR MEDICAL DIAGNOSIS
Industrial-Ready Implementation with Educational Outputs
================================================================================

Author: Senior ML Engineer
Domain: Medical Machine Learning
Purpose: Complete SVM pipeline with learning focus and explainability

This program demonstrates SVM for binary classification in healthcare,
focusing on educational understanding and production-ready code quality.
================================================================================
"""

import logging
import time
import warnings
from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc,
    roc_auc_score
)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

RANDOM_STATE: int = 42
TEST_SIZE: float = 0.2
RANDOM_SEED: int = 42
LOGGING_LEVEL: int = logging.INFO
FIGSIZE_DEFAULT: Tuple[int, int] = (12, 6)
FIGSIZE_LARGE: Tuple[int, int] = (14, 8)

# SVM Hyperparameters
C_VALUES: list = [0.1, 1, 10, 100]
GAMMA_VALUES: list = ['scale', 'auto', 0.001, 0.01, 0.1, 1]
KERNELS: list = ['linear', 'rbf', 'poly', 'sigmoid']

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================


def setup_logging() -> logging.Logger:
    """
    Configure logging system for the entire application.

    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=LOGGING_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('svm_medical_diagnosis.log')
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def print_section(title: str) -> None:
    """
    Print formatted section separator with title.

    Args:
        title (str): Section title to display
    """
    separator = "=" * 80
    print(f"\n{separator}")
    print(f"  {title.upper()}")
    print(f"{separator}\n")


def print_subsection(title: str) -> None:
    """
    Print formatted subsection separator.

    Args:
        title (str): Subsection title to display
    """
    separator = "-" * 80
    print(f"\n{separator}")
    print(f"  {title}")
    print(f"{separator}\n")


def log_execution_time(func):
    """
    Decorator to measure and log function execution time.

    Args:
        func: Function to measure

    Returns:
        wrapper: Wrapped function with timing
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting execution of {func.__name__}")
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Completed {func.__name__} in {execution_time:.4f} seconds")
        print(f"⏱️  Execution time for {func.__name__}: {execution_time:.4f} seconds\n")
        return result
    return wrapper


# ============================================================================
# DATA LOADING & EXPLORATION
# ============================================================================


@log_execution_time
def load_medical_dataset() -> Tuple[pd.DataFrame, pd.Series, Dict[str, str]]:
    """
    Load the Breast Cancer Wisconsin dataset - a real medical dataset.

    The Breast Cancer Wisconsin dataset contains:
    - 569 samples
    - 30 features computed from digitized images of fine needle aspirates
    - Binary target: Malignant (0) vs Benign (1)

    Features represent measurements of cell nuclei including:
    - radius, texture, perimeter, area, smoothness
    - compactness, concavity, concave points, symmetry, fractal dimension
    - (10 measurements, 3 statistics each: mean, se, worst)

    Why use this dataset?
    ✓ Real medical data
    ✓ Binary classification (suitable for SVM)
    ✓ Clear medical relevance
    ✓ Well-documented features
    ✓ No synthetic/biased data

    Returns:
        Tuple[pd.DataFrame, pd.Series, Dict]: Features, Target, Feature descriptions
    """
    print_section("STEP 1: DATA LOADING")

    try:
        # Load dataset
        data = load_breast_cancer()
        X = pd.DataFrame(data.data, columns=data.feature_names)
        y = pd.Series(data.target, name='diagnosis')

        # Create feature descriptions
        feature_descriptions = {
            'radius_mean': 'Mean distance from center to perimeter',
            'texture_mean': 'Standard deviation of gray-scale values',
            'perimeter_mean': 'Mean size of core tumor',
            'area_mean': 'Mean area of tumor',
            'smoothness_mean': 'Mean of local variation in radius lengths',
            'compactness_mean': 'Mean of perimeter² / area - 1.0',
            'concavity_mean': 'Mean of severity of concave portions',
            'concave points_mean': 'Mean number of concave portions contour',
            'symmetry_mean': 'Mean symmetry measurement',
            'fractal_dimension_mean': 'Mean fractal dimension (coastline approx.)',
        }

        print("✓ Dataset loaded successfully!")
        print(f"✓ Source: Breast Cancer Wisconsin (Diagnostic)")
        print(f"✓ Real medical dataset from UCI Machine Learning Repository")

        logger.info("Dataset loaded: Breast Cancer Wisconsin")

        return X, y, feature_descriptions

    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


@log_execution_time
def explore_dataset(X: pd.DataFrame, y: pd.Series) -> None:
    """
    Perform comprehensive exploratory data analysis.

    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target variable
    """
    print_section("STEP 2: DATA EXPLORATION & UNDERSTANDING")

    # Dataset shape
    print("📊 DATASET SHAPE")
    print(f"  Number of samples (patients): {X.shape[0]}")
    print(f"  Number of features (measurements): {X.shape[1]}")
    print(f"  Total data points: {X.shape[0] * X.shape[1]:,}")

    # Target distribution
    print("\n🎯 TARGET DISTRIBUTION")
    target_counts = y.value_counts()
    print(f"  Benign (1):      {target_counts[1]} samples ({target_counts[1]/len(y)*100:.2f}%)")
    print(f"  Malignant (0):   {target_counts[0]} samples ({target_counts[0]/len(y)*100:.2f}%)")
    print("\n  ℹ️  Class distribution is reasonably balanced (good for SVM)")

    # Feature statistics
    print("\n📈 FEATURE STATISTICS")
    print("\nFirst 10 features summary:")
    print(X.iloc[:, :10].describe().round(3))

    # Data types
    print("\n🔍 DATA TYPES & MISSING VALUES")
    print(f"  All features are numerical: {X.dtypes.unique()}")
    missing = X.isnull().sum().sum()
    print(f"  Missing values: {missing} ✓ (Clean dataset)")

    logger.info("Dataset exploration completed")

    print("\n💡 WHY THIS DATASET FOR SVM?")
    print("  ✓ Real medical data - not synthetic")
    print("  ✓ Continuous numerical features - suitable for SVM")
    print("  ✓ High-dimensional (30 features) - SVM handles well")
    print("  ✓ Medical relevance - cancer diagnosis classification")
    print("  ✓ No missing values - requires no imputation")


@log_execution_time
def check_feature_correlation(X: pd.DataFrame) -> None:
    """
    Analyze feature correlation to understand relationships.

    Args:
        X (pd.DataFrame): Feature matrix
    """
    print_section("STEP 3: FEATURE CORRELATION ANALYSIS")

    correlation_matrix = X.corr()
    highly_correlated_pairs = []

    # Find highly correlated features
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            if abs(correlation_matrix.iloc[i, j]) > 0.9:
                highly_correlated_pairs.append(
                    (correlation_matrix.columns[i],
                     correlation_matrix.columns[j],
                     correlation_matrix.iloc[i, j])
                )

    if highly_correlated_pairs:
        print("🔗 HIGHLY CORRELATED FEATURES (correlation > 0.9):")
        for feat1, feat2, corr in highly_correlated_pairs[:5]:
            print(f"  {feat1} ↔ {feat2}: {corr:.4f}")
        print(f"\n  ℹ️  {len(highly_correlated_pairs)} highly correlated pairs found")
        print("  ℹ️  SVM can handle correlated features due to feature scaling")
    else:
        print("✓ No highly correlated features found (good for model stability)")

    logger.info("Feature correlation analysis completed")


# ============================================================================
# FEATURE SCALING & DATA PREPROCESSING
# ============================================================================


@log_execution_time
def prepare_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    """
    Prepare data with proper scaling and train-test split.

    Why Feature Scaling is Critical for SVM:
    ===================================
    SVM is DISTANCE-BASED algorithm:
    - Uses distance between data points to find optimal hyperplane
    - Features with larger ranges dominate the distance calculation
    - Without scaling: Feature with range [0, 10000] overpowers [0, 1]

    Example WITHOUT scaling:
      Point A = [100 (feature1), 0.5 (feature2)]
      Point B = [0, 0.5]
      Distance = √[(100-0)² + (0.5-0.5)²] = 100 (dominated by feature1)

    Example WITH scaling (to [-1, 1]):
      Point A = [1, -0.5]
      Point B = [0, -0.5]
      Distance = √[(1-0)² + (-0.5-0.5)²] = 1 (balanced)

    StandardScaler:
    - Transforms features to mean=0, std=1
    - Formula: z = (x - mean) / std_dev
    - Ensures all features contribute equally

    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target variable
        test_size (float): Proportion of test set
        random_state (int): Random seed

    Returns:
        Tuple: X_train_scaled, X_test_scaled, y_train, y_test, scaler
    """
    print_section("STEP 4: FEATURE SCALING & DATA SPLITTING")

    print("🔢 FEATURE SCALING IMPORTANCE")
    print("\nWhy scaling matters for SVM:")
    print("  1. SVM is DISTANCE-BASED algorithm")
    print("  2. Without scaling, large-range features dominate")
    print("  3. Scaling ensures fair contribution from all features")
    print("  4. Improves convergence speed of SVM optimization")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    # Reset indices to ensure DataFrames maintain column names
    X_train = X_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    print(f"\n✓ Train-Test Split (80-20 stratified):")
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")

    print("\n📊 BEFORE SCALING:")
    # Get first feature and second feature names from columns
    feature_cols = X_train.columns
    first_feature = feature_cols[0]
    second_feature = feature_cols[1]

    print(f"  Feature '{first_feature}' range: [{X_train[first_feature].min():.2f}, "
          f"{X_train[first_feature].max():.2f}]")
    print(f"  Feature '{second_feature}' range: [{X_train[second_feature].min():.2f}, "
          f"{X_train[second_feature].max():.2f}]")

    # Apply StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Convert to DataFrame for reference
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X_train.columns)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X_test.columns)

    print("\n📊 AFTER SCALING (StandardScaler - mean=0, std=1):")
    print(f"  Feature '{first_feature}' range: [{X_train_scaled_df[first_feature].min():.2f}, "
          f"{X_train_scaled_df[first_feature].max():.2f}]")
    print(f"  Feature '{second_feature}' range: [{X_train_scaled_df[second_feature].min():.2f}, "
          f"{X_train_scaled_df[second_feature].max():.2f}]")
    print("\n  ✓ All features now have similar scales")
    print("  ✓ Each feature contributes fairly to distance calculation")
    print("  ✓ SVM will train more efficiently and accurately")

    logger.info("Data preprocessing completed")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


# ============================================================================
# SVM THEORY & FUNDAMENTALS
# ============================================================================


def explain_svm_fundamentals() -> None:
    """
    Print comprehensive explanation of SVM theory.
    """
    print_section("SVM FUNDAMENTALS & THEORY")

    print("📚 WHAT IS SUPPORT VECTOR MACHINE (SVM)?")
    print("=" * 80)
    print("""
Support Vector Machine (SVM) is a powerful supervised learning algorithm for
binary classification and regression. In medical diagnosis, it excels at
finding decision boundaries between healthy and diseased patients.

🎯 CORE CONCEPT: The Hyperplane
================================
In 2D space: A LINE that separates two classes
In 3D space: A PLANE that separates two classes
In nD space: A HYPERPLANE (n-1 dimensional surface)

Example in Medical Diagnosis:
  Feature 1 (X-axis): Blood Glucose Level
  Feature 2 (Y-axis): BMI
  Classes: Benign (blue dots) vs Malignant (red dots)
  
  The hyperplane is a line that best separates these two classes.

🚀 KEY PRINCIPLE: MAXIMUM MARGIN
==================================
SVM doesn't just find ANY line separating classes. It finds the OPTIMAL line
that maximizes the margin (distance) between classes.

Why is maximum margin important?
  ✓ Provides robustness: More confident predictions
  ✓ Reduces overfitting: Generalizes better to new data
  ✓ Better separation: Clear decision boundary

Illustration:
  
  Poor Hyperplane (close to points):      Good Hyperplane (far from points):
      
      Red ●                                   Red ●
      ███████ ← Hyperplane                    ═══════════ ← Hyperplane
      Blue ●                                  Blue ●
  
      Margin = SMALL (risky)                  Margin = LARGE (safe)

🎪 SUPPORT VECTORS: The Important Points
==========================================
Support vectors are the data points CLOSEST to the hyperplane.
They literally "support" (define) the decision boundary.

Key insight:
  ✓ SVM uses ONLY support vectors for prediction (not all data)
  ✓ Other points don't influence the decision boundary
  ✓ This makes SVM memory-efficient and fast
  
Medical interpretation:
  - Support vectors are the "borderline" cases (hardest to classify)
  - These are the most informative patients for diagnosis
  - Often represent edge cases in medical domain

📐 MATHEMATICAL FORMULATION
=============================
For a linear SVM, the goal is:
  1. Find weights (w) and bias (b) for the hyperplane
  2. Maximize margin = 2/||w|| (distance between classes)
  3. Subject to constraint: All points classified correctly
     (with tolerance parameter C for misclassification)

The decision function is: f(x) = w·x + b
  - If f(x) > 0: Predict class 1
  - If f(x) < 0: Predict class 0
    """)


def explain_kernels() -> None:
    """
    Explain different SVM kernels and their use cases.
    """
    print_subsection("SVM KERNELS: Handling Non-linear Problems")

    print("""
🔧 THE KERNEL TRICK: Transforming Non-linear into Linear
=========================================================

Problem: Real-world data is often NOT linearly separable.

Example: Imagine separating healthy vs diseased patients where the boundary
is circular - no straight line can separate them!

Solution: The Kernel Trick
  ✓ Transform data into higher dimension where it becomes separable
  ✓ Do this implicitly (computationally efficient) without explicit transformation
  ✓ Use kernel function to compute inner products in high-dimensional space

Four Main Kernels in SVM:

1️⃣  LINEAR KERNEL
   ─────────────
   Formula: K(x₁, x₂) = x₁ · x₂
   
   When to use:
   ✓ Data is linearly separable
   ✓ High-dimensional data (many features)
   ✓ Large datasets (fastest to train)
   ✓ Interpretability is important
   
   Pros: Fast, interpretable, fewer parameters
   Cons: Cannot handle complex non-linear patterns
   
   Medical example: Simple threshold-based diagnosis

2️⃣  RBF (Radial Basis Function) KERNEL
   ──────────────────────────────────
   Formula: K(x₁, x₂) = exp(-γ||x₁ - x₂||²)
   
   When to use:
   ✓ Data has non-linear decision boundaries
   ✓ Moderate to large datasets
   ✓ You don't know if data is linearly separable
   ✓ Generally good default choice
   
   Parameters:
   - γ (gamma): Controls influence of each training example
     * Small γ: Each point has far-reaching influence (smooth boundary)
     * Large γ: Each point has local influence (wiggly boundary)
   
   Pros: Versatile, handles complex patterns
   Cons: Slower than linear, more parameters to tune
   
   Medical example: Complex disease patterns with interactions

3️⃣  POLYNOMIAL KERNEL
   ──────────────────
   Formula: K(x₁, x₂) = (γ(x₁ · x₂) + coef)^d
   
   When to use:
   ✓ Polynomial relationships in features
   ✓ When you know the degree of non-linearity
   ✓ Small to medium datasets
   
   Parameters:
   - degree: Polynomial degree (typically 2-5)
   - γ (gamma): Kernel coefficient
   - coef: Independent term
   
   Pros: Good for polynomial relationships
   Cons: Computational cost increases with degree
   
   Medical example: Feature interactions (e.g., age × weight)

4️⃣  SIGMOID KERNEL
   ───────────────
   Formula: K(x₁, x₂) = tanh(γ(x₁ · x₂) + coef)
   
   When to use:
   ✓ Similar to neural networks (uses sigmoid function)
   ✓ Small datasets
   ✓ When you want soft decision boundaries
   
   Pros: Soft boundaries, familiar from neural networks
   Cons: Not always convergent, behaves like RBF in some cases
   
   Medical example: Soft classification boundaries
    """)


def explain_hyperparameters() -> None:
    """
    Explain critical SVM hyperparameters.
    """
    print_subsection("CRITICAL HYPERPARAMETERS: C and Gamma")

    print("""
⚙️  HYPERPARAMETER 1: C (Regularization Parameter)
===================================================

What does C do?
- Controls the trade-off between:
  ✓ Creating a smooth decision boundary (large margin)
  ✓ Correctly classifying all training points (small margin)

Mathematical interpretation:
- C = penalty for misclassifying a point
- Small C: Allow more misclassifications (focus on margin)
- Large C: Punish misclassifications heavily (focus on accuracy)

Impact on model:

Small C (e.g., 0.1):
  Decision boundary: SMOOTH and SIMPLE
  Training accuracy: May be LOWER
  Overfitting risk: LOW (more generalization)
  Margin: LARGE
  
  Medical implication: Accept some diagnosis errors for robust model

Large C (e.g., 100):
  Decision boundary: COMPLEX and WIGGLY
  Training accuracy: May be HIGHER
  Overfitting risk: HIGH (memorizes data)
  Margin: SMALL
  
  Medical implication: Minimize all diagnosis errors (risky in practice)

Typical range: C = [0.1, 1, 10, 100, 1000]


⚙️  HYPERPARAMETER 2: Gamma (Kernel Coefficient)
==================================================

What does Gamma do? (Only relevant for RBF, Poly, Sigmoid kernels)
- Controls the "reach" of each training example
- Defines how far the influence of one example extends

Mathematical interpretation:
- γ affects the shape of the decision boundary
- Controls flexibility of the decision surface

Impact on model:

Small γ (e.g., 0.001):
  Decision boundary: SMOOTH and SIMPLE
  Each point influences: FAR AWAY points
  Overfitting risk: LOW
  Training speed: FAST
  
  Medical implication: Considers broader context for diagnosis

Large γ (e.g., 1):
  Decision boundary: COMPLEX and LOCALIZED
  Each point influences: NEARBY points only
  Overfitting risk: HIGH
  Training speed: SLOW
  
  Medical implication: Makes decisions based on specific neighbors

Typical range: γ = [0.001, 0.01, 0.1, 1, 'scale', 'auto']

🎯 Combined Effect of C and Gamma:

C=0.1, γ=0.001   → Very smooth boundary, maximum generalization
C=100, γ=1       → Very complex boundary, maximum specificity

Finding optimal values requires GridSearchCV (cross-validation).
    """)


# ============================================================================
# SVM MODEL TRAINING
# ============================================================================


@log_execution_time
def train_svm_models(
    X_train_scaled: np.ndarray,
    y_train: np.ndarray
) -> Dict[str, SVC]:
    """
    Train SVM models with different kernels.

    Args:
        X_train_scaled (np.ndarray): Scaled training features
        y_train (np.ndarray): Training target

    Returns:
        Dict[str, SVC]: Dictionary of trained SVM models
    """
    print_section("STEP 5: TRAINING SVM WITH DIFFERENT KERNELS")

    print("🤖 TRAINING MULTIPLE KERNEL VARIANTS\n")

    models = {}

    for kernel in KERNELS:
        print(f"  Training {kernel.upper()} kernel SVM...", end=" ")
        try:
            model = SVC(kernel=kernel, random_state=RANDOM_STATE, probability=True)
            model.fit(X_train_scaled, y_train)
            models[kernel] = model

            # Print basic info
            n_support_vectors = len(model.support_vectors_)
            support_vector_ratio = n_support_vectors / len(X_train_scaled) * 100

            print(f"✓")
            logger.info(f"Trained {kernel} SVM with {n_support_vectors} support vectors")

        except Exception as e:
            logger.error(f"Error training {kernel} kernel: {str(e)}")
            print(f"✗ (Error: {str(e)})")
            continue

    print(f"\n✓ All {len(models)} SVM models trained successfully!")

    return models


@log_execution_time
def train_optimal_svm(
    X_train_scaled: np.ndarray,
    y_train: np.ndarray
) -> Tuple[SVC, Dict[str, Any], GridSearchCV]:
    """
    Train optimal SVM using GridSearchCV for hyperparameter tuning.

    GridSearchCV automatically finds the best hyperparameters through
    exhaustive search combined with cross-validation.

    Why GridSearchCV?
    ✓ Tests all combinations of hyperparameters
    ✓ Uses k-fold cross-validation (default k=5)
    ✓ Prevents overfitting by using validation sets
    ✓ Returns best model automatically
    ✓ Provides detailed performance metrics

    Args:
        X_train_scaled (np.ndarray): Scaled training features
        y_train (np.ndarray): Training target

    Returns:
        Tuple: Best SVM model, Best parameters, GridSearchCV object
    """
    print_section("STEP 6: HYPERPARAMETER TUNING WITH GRIDSEARCHCV")

    print("🔍 GRID SEARCH OVERVIEW")
    print("=" * 80)
    print(f"\nSearching hyperparameter space:")
    print(f"  Kernels to test:  {KERNELS}")
    print(f"  C values to test: {C_VALUES}")
    print(f"  Gamma values to test: {GAMMA_VALUES}")
    total_combinations = len(KERNELS) * len(C_VALUES) * len(GAMMA_VALUES)
    print(f"  Total combinations: {total_combinations}")
    print(f"  With 5-fold CV: {total_combinations * 5} models will be trained")

    print("\nThis is computationally intensive but ensures we find optimal hyperparameters!")
    print("\n⏳ Starting Grid Search (this may take 1-2 minutes)...\n")

    param_grid = {
        'kernel': KERNELS,
        'C': C_VALUES,
        'gamma': GAMMA_VALUES
    }

    grid_search = GridSearchCV(
        SVC(random_state=RANDOM_STATE, probability=True),
        param_grid,
        cv=5,
        n_jobs=-1,
        verbose=0,
        scoring='accuracy'
    )

    grid_search.fit(X_train_scaled, y_train)
    best_model = grid_search.best_estimator_

    print("✓ Grid Search completed!\n")

    # Extract best parameters
    best_params = grid_search.best_params_
    best_cv_score = grid_search.best_score_

    print("🏆 BEST HYPERPARAMETERS FOUND")
    print("=" * 80)
    print(f"  Best Kernel: {best_params['kernel']}")
    print(f"  Best C: {best_params['C']}")
    print(f"  Best Gamma: {best_params['gamma']}")
    print(f"  Best CV Accuracy: {best_cv_score:.4f} ({best_cv_score*100:.2f}%)")

    print("\n💡 INTERPRETATION OF RESULTS")
    print("-" * 80)

    if best_params['kernel'] == 'linear':
        print("  ✓ Linear kernel works best: Data has linear separation")
        print("  ✓ Features are linearly related to diagnosis")
    elif best_params['kernel'] == 'rbf':
        print("  ✓ RBF kernel works best: Complex non-linear relationships exist")
        print(f"  ✓ Gamma={best_params['gamma']}: Controls RBF influence range")
    elif best_params['kernel'] == 'poly':
        print("  ✓ Polynomial kernel works best: Polynomial feature relationships")

    if best_params['C'] < 10:
        print("  ✓ Low C value: Model prioritizes smooth boundaries (regularization)")
        print("  ✓ More generalization, potentially better on new data")
    else:
        print("  ✓ High C value: Model prioritizes training accuracy")
        print("  ⚠️  Risk of overfitting - verify on test set carefully")

    logger.info(f"Best hyperparameters found: {best_params}")

    return best_model, best_params, grid_search


# ============================================================================
# MODEL EVALUATION
# ============================================================================


@log_execution_time
def evaluate_model(
    model: SVC,
    X_test_scaled: np.ndarray,
    y_test: np.ndarray,
    model_name: str = "SVM"
) -> Dict[str, Any]:
    """
    Comprehensive model evaluation with multiple metrics.

    Args:
        model (SVC): Trained SVM model
        X_test_scaled (np.ndarray): Scaled test features
        y_test (np.ndarray): Test target
        model_name (str): Name for logging

    Returns:
        Dict[str, Any]: Dictionary containing all evaluation metrics
    """
    print_section(f"STEP 7: MODEL EVALUATION - {model_name}")

    try:
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=False)

        # ROC curve
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc_auc': roc_auc,
            'confusion_matrix': cm,
            'fpr': fpr,
            'tpr': tpr,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'class_report': class_report
        }

        # Print metrics
        print("📊 PERFORMANCE METRICS")
        print("=" * 80)

        print(f"\n1. ACCURACY: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("   Definition: Percentage of correct predictions (both TP and TN)")
        print("   Formula: (TP + TN) / (TP + TN + FP + FN)")
        print("   In medical diagnosis:")
        print(f"   ✓ {int(accuracy * len(y_test))}/{len(y_test)} predictions are correct")
        if accuracy > 0.95:
            print("   ✓ EXCELLENT: Model is highly reliable")
        elif accuracy > 0.90:
            print("   ✓ GOOD: Model is reliable")
        elif accuracy > 0.80:
            print("   ⚠️  FAIR: Consider improving the model")
        else:
            print("   ✗ POOR: Model needs significant improvements")

        print(f"\n2. PRECISION: {precision:.4f} ({precision*100:.2f}%)")
        print("   Definition: When model predicts 'Malignant', how often is it correct?")
        print("   Formula: TP / (TP + FP)")
        print("   Medical interpretation:")
        if precision > 0.95:
            print(f"   ✓ EXCELLENT: Only {int((1-precision)*100)}% false positives")
            print("   ✓ Safe to use - rare misdiagnosis of healthy as diseased")
        elif precision > 0.90:
            print(f"   ✓ GOOD: {int((1-precision)*100)}% false positive rate")
        else:
            print(f"   ⚠️  CONCERNING: {int((1-precision)*100)}% of 'Malignant' predictions are wrong")
            print("   ⚠️  Risk: Healthy patients treated as diseased (high anxiety)")

        print(f"\n3. RECALL: {recall:.4f} ({recall*100:.2f}%)")
        print("   Definition: Of all actually 'Malignant' cases, how many did we catch?")
        print("   Formula: TP / (TP + FN)")
        print("   Medical interpretation:")
        if recall > 0.95:
            print(f"   ✓ EXCELLENT: Only {int((1-recall)*100)}% of diseased patients missed")
            print("   ✓ Very safe - rarely miss actual cases")
        elif recall > 0.90:
            print(f"   ✓ GOOD: {int((1-recall)*100)}% of cases might be missed")
        else:
            print(f"   ✗ DANGEROUS: {int((1-recall)*100)}% false negatives!")
            print("   ✗ Risk: Diseased patients told they're healthy (life-threatening)")

        print(f"\n4. F1 SCORE: {f1:.4f}")
        print("   Definition: Harmonic mean of precision and recall")
        print("   Formula: 2 × (Precision × Recall) / (Precision + Recall)")
        print("   Why F1?")
        print("   ✓ Balances precision and recall")
        print("   ✓ Better than accuracy when classes are imbalanced")
        print("   ✓ Important in medical diagnosis (both errors matter)")
        if f1 > 0.90:
            print("   ✓ EXCELLENT: Well-balanced performance")
        elif f1 > 0.80:
            print("   ✓ GOOD: Acceptable balance")

        print(f"\n5. ROC-AUC SCORE: {roc_auc:.4f}")
        print("   Definition: Area Under the ROC Curve")
        print("   Range: 0 to 1 (higher is better)")
        print("   What it measures:")
        print("   ✓ Probability that model ranks a random positive higher than negative")
        print("   ✓ Threshold-independent performance evaluation")
        if roc_auc > 0.95:
            print("   ✓ EXCELLENT: Outstanding discrimination between classes")
        elif roc_auc > 0.90:
            print("   ✓ GOOD: Strong discrimination")
        elif roc_auc > 0.80:
            print("   ⚠️  FAIR: Moderate discrimination")

        # Confusion Matrix
        print(f"\n6. CONFUSION MATRIX")
        print("=" * 80)
        tn, fp, fn, tp = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]

        print(f"\n  Predicted:        Negative    Positive")
        print(f"  Actual Negative:  {tn:6d}     {fp:6d}  (TN=True Neg, FP=False Pos)")
        print(f"  Actual Positive:  {fn:6d}     {tp:6d}  (FN=False Neg, TP=True Pos)")

        print("\n  Interpretation:")
        print(f"  ✓ True Negatives (TN):  {tn} - Correctly identified benign")
        print(f"  ✓ True Positives (TP):  {tp} - Correctly identified malignant")
        print(f"  ✗ False Positives (FP): {fp} - Benign wrongly marked as malignant")
        print(f"  ✗ False Negatives (FN): {fn} - Malignant wrongly marked as benign")

        print("\n  Medical Risk Analysis:")
        if fn > 0:
            fn_rate = fn / (fn + tp) * 100
            print(f"  ✗ FALSE NEGATIVE RATE: {fn_rate:.2f}%")
            print(f"    → {fn_rate:.2f}% of actual malignant cases are missed (DANGEROUS)")
        else:
            print(f"  ✓ FALSE NEGATIVE RATE: 0% (No malignant cases missed!)")

        if fp > 0:
            fp_rate = fp / (fp + tn) * 100
            print(f"  ⚠️  FALSE POSITIVE RATE: {fp_rate:.2f}%")
            print(f"    → {fp_rate:.2f}% of benign cases wrongly diagnosed (Causes anxiety)")
        else:
            print(f"  ✓ FALSE POSITIVE RATE: 0% (No unnecessary alarms!)")

        logger.info(f"{model_name} evaluation completed")

        return metrics

    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================


@log_execution_time
def visualize_confusion_matrix(
    cm: np.ndarray,
    model_name: str = "SVM"
) -> None:
    """
    Create confusion matrix heatmap visualization.

    Args:
        cm (np.ndarray): Confusion matrix
        model_name (str): Model name for title
    """
    print_subsection(f"Confusion Matrix Visualization - {model_name}")

    plt.figure(figsize=(12, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['Benign', 'Malignant'],
                yticklabels=['Benign', 'Malignant'])
    plt.title(f'Confusion Matrix - {model_name}\n(Medical Diagnosis Prediction)', fontsize=14, fontweight='bold')
    plt.ylabel('Actual Diagnosis', fontsize=12)
    plt.xlabel('Predicted Diagnosis', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'confusion_matrix_{model_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info(f"Confusion matrix visualization saved")


@log_execution_time
def visualize_roc_curve(
    fpr: np.ndarray,
    tpr: np.ndarray,
    roc_auc: float,
    model_name: str = "SVM"
) -> None:
    """
    Create ROC curve visualization.

    Args:
        fpr (np.ndarray): False positive rate
        tpr (np.ndarray): True positive rate
        roc_auc (float): Area under curve
        model_name (str): Model name
    """
    print_subsection(f"ROC Curve Visualization - {model_name}")

    plt.figure(figsize=(12, 6))

    # Plot ROC curve
    plt.plot(fpr, tpr, color='darkorange', lw=2.5, label=f'ROC curve (AUC = {roc_auc:.3f})')

    # Plot diagonal (random classifier)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier (AUC = 0.500)')

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Sensitivity/Recall)', fontsize=12)
    plt.title(f'ROC Curve - {model_name}\n(Medical Diagnosis Performance)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'roc_curve_{model_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info("ROC curve visualization saved")


@log_execution_time
def visualize_decision_boundary(
    X_train_scaled: np.ndarray,
    y_train: np.ndarray,
    model: SVC,
    feature_idx1: int = 0,
    feature_idx2: int = 1,
    model_name: str = "SVM"
) -> None:
    """
    Visualize 2D decision boundary using two selected features.

    This visualization helps understand how SVM separates classes in 2D space.
    In real high-dimensional space, the decision boundary is much more complex.

    Args:
        X_train_scaled (np.ndarray): Scaled training features
        y_train (np.ndarray): Training target
        model (SVC): Trained SVM model
        feature_idx1 (int): Index of first feature
        feature_idx2 (int): Index of second feature
        model_name (str): Model name
    """
    print_subsection(f"Decision Boundary Visualization - {model_name}")

    # Create mesh
    x_min, x_max = X_train_scaled[:, feature_idx1].min() - 1, X_train_scaled[:, feature_idx1].max() + 1
    y_min, y_max = X_train_scaled[:, feature_idx2].min() - 1, X_train_scaled[:, feature_idx2].max() + 1

    h = 0.02  # step size in mesh

    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # Prepare data for prediction
    test_data = np.c_[xx.ravel(), yy.ravel()]

    # For decision boundary visualization, we need to pad with mean values for other features
    full_test_data = np.zeros((test_data.shape[0], X_train_scaled.shape[1]))
    full_test_data[:, feature_idx1] = test_data[:, 0]
    full_test_data[:, feature_idx2] = test_data[:, 1]

    # Fill other features with training data mean
    for i in range(X_train_scaled.shape[1]):
        if i not in [feature_idx1, feature_idx2]:
            full_test_data[:, i] = X_train_scaled[:, i].mean()

    # Predict on mesh
    Z = model.decision_function(full_test_data)
    Z = Z.reshape(xx.shape)

    # Plot
    plt.figure(figsize=(14, 8))

    # Plot decision boundary
    plt.contourf(xx, yy, Z, levels=20, cmap='RdBu', alpha=0.8)
    plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='black')

    # Plot training points
    plt.scatter(X_train_scaled[y_train == 0, feature_idx1],
                X_train_scaled[y_train == 0, feature_idx2],
                c='blue', label='Benign', s=50, edgecolors='k', alpha=0.7)
    plt.scatter(X_train_scaled[y_train == 1, feature_idx1],
                X_train_scaled[y_train == 1, feature_idx2],
                c='red', label='Malignant', s=50, edgecolors='k', alpha=0.7)

    # Plot support vectors
    support_vectors = model.support_vectors_
    plt.scatter(support_vectors[:, feature_idx1], support_vectors[:, feature_idx2],
                s=200, linewidth=1.5, facecolors='none', edgecolors='green', label='Support Vectors')

    plt.xlabel(f'Feature {feature_idx1} (Scaled)', fontsize=12)
    plt.ylabel(f'Feature {feature_idx2} (Scaled)', fontsize=12)
    plt.title(f'Decision Boundary - {model_name}\n(2D Projection of High-dimensional Space)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.colorbar(label='Decision Function Value')
    plt.tight_layout()
    plt.savefig(f'decision_boundary_{model_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info("Decision boundary visualization saved")


@log_execution_time
def visualize_kernel_comparison(
    models: Dict[str, SVC],
    metrics_dict: Dict[str, Dict[str, Any]]
) -> None:
    """
    Compare accuracy across different kernels.

    Args:
        models (Dict[str, SVC]): Dictionary of trained models
        metrics_dict (Dict[str, Dict]): Dictionary of metrics for each kernel
    """
    print_subsection("Kernel Comparison Visualization")

    kernels = list(metrics_dict.keys())
    accuracies = [metrics_dict[k]['accuracy'] for k in kernels]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(kernels, accuracies, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
                   edgecolor='black', linewidth=1.5, alpha=0.8)

    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.4f}\n({acc*100:.2f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.xlabel('Kernel Type', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
    plt.title('SVM Performance Comparison: Different Kernels\n(Medical Diagnosis Accuracy)', fontsize=14, fontweight='bold')
    plt.ylim([0, 1.1])
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('kernel_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info("Kernel comparison visualization saved")


@log_execution_time
def visualize_c_parameter_effect(
    X_train_scaled: np.ndarray,
    X_test_scaled: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray
) -> None:
    """
    Visualize effect of C parameter on model performance.

    Args:
        X_train_scaled (np.ndarray): Scaled training features
        X_test_scaled (np.ndarray): Scaled test features
        y_train (np.ndarray): Training target
        y_test (np.ndarray): Test target
    """
    print_subsection("C Parameter Effect Analysis")

    c_values = [0.01, 0.1, 1, 10, 100]
    train_accuracies = []
    test_accuracies = []

    print("Testing different C values...")
    for c in c_values:
        model = SVC(kernel='rbf', C=c, random_state=RANDOM_STATE)
        model.fit(X_train_scaled, y_train)

        train_acc = model.score(X_train_scaled, y_train)
        test_acc = model.score(X_test_scaled, y_test)

        train_accuracies.append(train_acc)
        test_accuracies.append(test_acc)
        print(f"  C={c:6.2f} → Train: {train_acc:.4f}, Test: {test_acc:.4f}")

    plt.figure(figsize=(12, 6))
    plt.plot(c_values, train_accuracies, marker='o', linewidth=2.5, markersize=8,
            label='Training Accuracy', color='blue')
    plt.plot(c_values, test_accuracies, marker='s', linewidth=2.5, markersize=8,
            label='Testing Accuracy', color='orange')

    plt.xlabel('C Parameter (Regularization)', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
    plt.title('Effect of C Parameter on SVM Performance\n(Lower C = More Regularization)', fontsize=14, fontweight='bold')
    plt.xscale('log')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('c_parameter_effect.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info("C parameter effect visualization saved")


@log_execution_time
def visualize_gamma_parameter_effect(
    X_train_scaled: np.ndarray,
    X_test_scaled: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray
) -> None:
    """
    Visualize effect of gamma parameter on model performance.

    Args:
        X_train_scaled (np.ndarray): Scaled training features
        X_test_scaled (np.ndarray): Scaled test features
        y_train (np.ndarray): Training target
        y_test (np.ndarray): Test target
    """
    print_subsection("Gamma Parameter Effect Analysis")

    gamma_values = [0.001, 0.01, 0.1, 1]
    train_accuracies = []
    test_accuracies = []

    print("Testing different Gamma values...")
    for gamma in gamma_values:
        model = SVC(kernel='rbf', C=1, gamma=gamma, random_state=RANDOM_STATE)
        model.fit(X_train_scaled, y_train)

        train_acc = model.score(X_train_scaled, y_train)
        test_acc = model.score(X_test_scaled, y_test)

        train_accuracies.append(train_acc)
        test_accuracies.append(test_acc)
        print(f"  Gamma={gamma:6.3f} → Train: {train_acc:.4f}, Test: {test_acc:.4f}")

    plt.figure(figsize=(12, 6))
    plt.plot(gamma_values, train_accuracies, marker='o', linewidth=2.5, markersize=8,
            label='Training Accuracy', color='green')
    plt.plot(gamma_values, test_accuracies, marker='s', linewidth=2.5, markersize=8,
            label='Testing Accuracy', color='purple')

    plt.xlabel('Gamma Parameter (RBF Influence)', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
    plt.title('Effect of Gamma Parameter on SVM Performance\n(RBF Kernel, C=1)', fontsize=14, fontweight='bold')
    plt.xscale('log')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('gamma_parameter_effect.png', dpi=300, bbox_inches='tight')
    plt.show()

    logger.info("Gamma parameter effect visualization saved")


# ============================================================================
# EXPLAINABILITY & MEDICAL INSIGHTS
# ============================================================================


def explain_svm_performance(
    model: SVC,
    metrics: Dict[str, Any],
    best_params: Dict[str, Any],
    feature_descriptions: Dict[str, str]
) -> None:
    """
    Provide educational explanations of SVM performance and insights.

    Args:
        model (SVC): Trained SVM model
        metrics (Dict): Performance metrics
        best_params (Dict): Hyperparameters
        feature_descriptions (Dict): Feature descriptions
    """
    print_section("EXPLAINABILITY: WHY SVM WORKS WELL FOR THIS MEDICAL PROBLEM")

    print("🔬 SVM PERFORMANCE ANALYSIS")
    print("=" * 80)

    accuracy = metrics['accuracy']

    print(f"\n1. ACHIEVED ACCURACY: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("-" * 80)

    if accuracy > 0.95:
        print("   ✓ EXCELLENT PERFORMANCE!")
        print("\n   Reasons SVM excels here:")
        print("   ✓ High-dimensional data (30 features)")
        print("     → SVM handles high dimensions better than many algorithms")
        print("   ✓ Clear separation between benign and malignant")
        print("     → SVM can find optimal hyperplane efficiently")
        print("   ✓ Proper feature scaling applied")
        print("     → Ensures all features contribute fairly")
        print("   ✓ Support vectors capture decision boundary effectively")
        print("     → Focus only on critical boundary cases")

    elif accuracy > 0.85:
        print("   ✓ GOOD PERFORMANCE")
        print("   The model is reliable for clinical support")
        print("   But should be combined with other diagnostic methods")

    else:
        print("   ⚠️  MODERATE PERFORMANCE")
        print("   Consider ensemble methods or more data collection")

    print(f"\n2. KERNEL SELECTION: {best_params['kernel'].upper()}")
    print("-" * 80)

    kernel = best_params['kernel']
    if kernel == 'linear':
        print("   Linear kernel selected - indicates:")
        print("   ✓ Data has approximately linear decision boundary")
        print("   ✓ Features are roughly linearly related to diagnosis")
        print("   ✓ Model is interpretable (weights show feature importance)")

    elif kernel == 'rbf':
        print("   RBF kernel selected - indicates:")
        print("   ✓ Data has complex non-linear decision boundary")
        print("   ✓ Feature interactions are important")
        print("   ✓ Local neighborhoods matter for classification")
        print(f"   ✓ Gamma={best_params['gamma']}: Controls smoothness")

    elif kernel == 'poly':
        print("   Polynomial kernel selected - indicates:")
        print("   ✓ Polynomial feature relationships are important")
        print("   ✓ Features have power-law interactions")

    print(f"\n3. REGULARIZATION STRENGTH: C={best_params['C']}")
    print("-" * 80)

    c_param = best_params['C']
    if c_param < 1:
        print(f"   Low C (underfitting risk is lower):")
        print(f"   ✓ Model generalizes well to new, unseen patients")
        print(f"   ✓ Smooth decision boundary (robust)")
        print(f"   ✓ Less sensitive to individual outlier cases")

    else:
        print(f"   High C (overfitting risk is higher):")
        print(f"   ⚠️  Model fits training data very closely")
        print(f"   ⚠️  May not generalize as well to new patients")
        print(f"   ⚠️  Sensitive to outliers and noise")

    print(f"\n4. SUPPORT VECTORS ANALYSIS")
    print("-" * 80)

    n_support = len(model.support_vectors_)
    n_training = len(model.support_vectors_) / (30*0.8)  # Approximate
    sv_ratio = n_support / 456  # Approximate training set size

    print(f"   Number of support vectors: {n_support}")
    print(f"   Support vector ratio: {sv_ratio:.1%}")

    if sv_ratio < 0.1:
        print("   ✓ Very few support vectors needed")
        print("   ✓ Simple decision boundary")
        print("   ✓ Good generalization expected")

    elif sv_ratio < 0.3:
        print("   ✓ Reasonable number of support vectors")
        print("   ✓ Balanced complexity and accuracy")

    else:
        print("   ⚠️  Many support vectors")
        print("   ⚠️  Complex decision boundary")
        print("   ⚠️  Risk of overfitting")

    print(f"\n5. ADVANTAGES OF SVM FOR MEDICAL DIAGNOSIS")
    print("-" * 80)
    print("""
    ✓ HIGH ACCURACY: Excellent at finding optimal decision boundaries
    ✓ MEMORY EFFICIENT: Uses only support vectors (not all data points)
    ✓ HIGH-DIMENSIONAL DATA: Handles 30+ features effectively
    ✓ INTERPRETABLE: Can identify influential features via support vectors
    ✓ ROBUST: Maximum margin principle gives generalization confidence
    ✓ VERSATILE KERNELS: Handles both linear and non-linear patterns
    ✓ WELL-STUDIED: Extensive research in medical domain
    ✓ PROBABILISTIC: Can output confidence scores for decisions
    """)

    print(f"\n6. LIMITATIONS & WHEN SVM MAY FAIL")
    print("-" * 80)
    print("""
    ✗ IMBALANCED DATA: Struggles when classes are very unbalanced
      → Not an issue here (classes are balanced)

    ✗ MANY SAMPLES: Slow training with very large datasets
      → Not an issue here (569 samples is manageable)

    ✗ MISSING VALUES: Cannot handle missing data directly
      → Not an issue here (no missing values)

    ✗ FEATURE SCALING: Sensitive to feature scale
      → ADDRESSED: We applied StandardScaler

    ✗ HYPERPARAMETER TUNING: Requires GridSearchCV optimization
      → ADDRESSED: We performed comprehensive hyperparameter tuning

    ✗ INTERPRETABILITY: Black box for high dimensions
      → Can analyze support vectors for insights
    """)

    print(f"\n7. CLINICAL RECOMMENDATIONS")
    print("-" * 80)
    print(f"""
    Given SVM's {accuracy*100:.2f}% accuracy on this dataset:

    ✓ APPROPRIATE USES:
      • Screening tool to identify high-risk patients
      • Initial decision support for radiologists
      • Feature importance analysis for further investigation

    ⚠️  CAUTIONS:
      • Should NOT replace pathologist examination
      • Use as part of ensemble with other diagnostic methods
      • Always combine with clinical judgment and other tests
      • Document all predictions for audit trail
      • Monitor model performance over time with new data

    🔬 NEXT STEPS:
      • Validate on independent test cohort
      • Compare against other algorithms (Random Forest, Neural Networks)
      • Perform ablation studies on feature importance
      • Collect more data for edge cases
      • Establish confidence intervals for predictions
    """)


def explain_feature_scaling_importance() -> None:
    """
    Explain consequences of skipping feature scaling.
    """
    print_section("CRITICAL CONCEPT: IMPORTANCE OF FEATURE SCALING")

    print("""
🚨 WHAT HAPPENS IF WE SKIP FEATURE SCALING?

Let's analyze the Breast Cancer dataset without scaling:

BEFORE SCALING:
──────────────
Feature: radius_mean  → Range: [6.98, 28.11]    (difference: 21.13)
Feature: texture_mean → Range: [9.71, 39.28]    (difference: 29.57)
Feature: compactness_mean → Range: [0.04, 0.35] (difference: 0.31)

PROBLEM: Feature ranges differ by 100x!

How SVM is affected:
────────────────────
Distance = √[(radius difference)² + (texture difference)² + ... + (compactness)²]

Without scaling:
  = √[(20)² + (30)² + (0.3)²]
  = √[400 + 900 + 0.09]
  = √1300.09 ≈ 36

The large-range features (radius, texture) completely dominate!
Compactness is essentially ignored (difference of 0.3 is lost in the noise).

Impact on SVM:
──────────────
1. Biased Decision Boundary
   → Only considers high-range features
   → Ignores low-range features
   → Suboptimal classification

2. Convergence Problems
   → Optimization algorithm struggles with unbalanced scales
   → Requires more iterations to converge
   → May converge to suboptimal solution

3. Hyperparameter Sensitivity
   → C parameter becomes scale-dependent
   → Gamma becomes unreliable
   → Hard to tune hyperparameters

4. Distance Metrics Fail
   → All distances calculated incorrectly
   → Support vectors selected based on wrong criteria
   → Decision boundary is arbitrary

5. Reduced Generalization
   → Model learns to focus on high-range features
   → Ignores potentially important low-range features
   → Poor performance on new data

AFTER SCALING (StandardScaler):
────────────────────────────
All features → Mean=0, Std=1
All features → Approximately same range [-3, 3]

Benefits:
─────────
✓ Balanced contribution from all features
✓ Distance metric works correctly
✓ Optimization converges faster
✓ Hyperparameters become more meaningful
✓ Model generalizes better
✓ Results are reproducible

CONCLUSION:
───────────
Feature scaling is NOT optional for SVM - it's MANDATORY!
The algorithm assumes all features are on similar scales.

Without scaling: Model accuracy could drop by 5-15%
With scaling: Optimal performance achieved
    """)


def explain_svm_vs_other_algorithms() -> None:
    """
    Explain SVM advantages compared to other algorithms in medical domain.
    """
    print_section("SVM VS OTHER ALGORITHMS FOR MEDICAL DIAGNOSIS")

    print("""
ALGORITHM COMPARISON TABLE:
═══════════════════════════════════════════════════════════════════════════════

                    SVM         Logistic Reg    Random Forest    Neural Network
─────────────────────────────────────────────────────────────────────────────
High Dimensions    ✓ Excellent ✓ Good          ⚠ Moderate       ⚠ Moderate
Non-linear         ✓ Excellent ✗ Poor         ✓ Excellent      ✓ Excellent
Interpretability   ⚠ Moderate ✓ Excellent      ⚠ Moderate       ✗ Black box
Data Size          ⚠ < 100K   ✓ Any size      ✗ Needs 100K+    ✗ Needs 100K+
Training Speed     ✓ Fast      ✓ Very fast     ✗ Slow           ✗ Very slow
Mem Usage          ✓ Low       ✓ Low           ✗ High           ✗ Very high
Hyperparameter     ⚠ Complex   ✓ Simple        ✓ Simple          ✗ Very complex
Tuning
Outlier Robust     ⚠ Moderate ✓ Good          ✓ Excellent      ✗ Poor
Class Imbalance    ⚠ Moderate ✓ Good          ✓ Excellent      ⚠ Moderate
Medical Domain     ✓ Excellent ✓ Common       ✓ Growing        ✗ Regulatory issues
Validation         ✓ Proven    ✓ Proven       ✓ Growing        ⚠ Concerns

WHY SVM FOR MEDICAL DIAGNOSIS:
═══════════════════════════════

1. PERFECT FOR OUR DATASET:
   ✓ 30 high-dimensional features - SVM excels here
   ✓ ~600 samples - SVM trains fast with this size
   ✓ Binary classification - SVM's original use case
   ✓ Well-documented features - Support vectors are interpretable

2. MEDICAL REGULATORY COMPLIANCE:
   ✓ SVM has FDA approval in some medical applications
   ✓ Well-understood algorithm - easier to explain to doctors
   ✓ Deterministic predictions - no randomness in inference
   ✓ Reproducible results - critical in healthcare

3. CLINICAL ADVANTAGES:
   ✓ Confidence scores via probability estimation
   ✓ Support vectors identify critical cases
   ✓ Fast inference - good for real-time diagnosis
   ✓ No need for massive training data

4. ROBUSTNESS:
   ✓ Not sensitive to outliers (unlike some algorithms)
   ✓ Maximum margin principle provides safety margin
   ✓ Well-studied mathematics - predictable behavior
   ✓ Hyperparameter sensitivity is manageable

WHEN TO USE ALTERNATIVES:
═════════════════════════

Logistic Regression:
  → When maximum interpretability is critical
  → When features are known to be linearly separable
  → For quick baseline models

Random Forest:
  → When you have 100K+ samples
  → When features are very heterogeneous
  → When you need feature importance ranking

Neural Networks:
  → When you have 1M+ samples
  → When data is image/text based
  → When non-linearity is extreme
  → When you have sufficient computational resources

Ensemble (SVM + Logistic Reg + Random Forest):
  → For maximum accuracy and robustness
  → For clinical decision support systems
  → When combining different data sources
    """)


# ============================================================================
# HTML DASHBOARD GENERATION
# ============================================================================


def generate_html_dashboard(
    optimal_metrics: Dict[str, Any],
    best_params: Dict[str, Any],
    metrics_dict: Dict[str, Dict[str, Any]],
    grid_search: GridSearchCV
) -> None:
    """
    Generate a beautiful interactive HTML dashboard for insights visualization.

    Args:
        optimal_metrics (Dict): Performance metrics from best model
        best_params (Dict): Best hyperparameters found
        metrics_dict (Dict): Metrics for all kernels
        grid_search (GridSearchCV): GridSearchCV object with CV results
    """
    print_subsection("Generating Interactive HTML Dashboard")

    # Extract key metrics
    accuracy = optimal_metrics['accuracy']
    precision = optimal_metrics['precision']
    recall = optimal_metrics['recall']
    f1 = optimal_metrics['f1']
    roc_auc = optimal_metrics['roc_auc']
    cm = optimal_metrics['confusion_matrix']
    tn, fp, fn, tp = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]

    # Calculate additional metrics
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    sensitivity = recall  # Same as recall
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Negative Rate
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate

    # Get kernel accuracies for comparison
    kernel_names = list(metrics_dict.keys())
    kernel_accuracies = [metrics_dict[k]['accuracy'] for k in kernel_names]

    # Get best CV score
    best_cv_score = grid_search.best_score_

    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVM Medical Diagnosis - Insights Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-color: #2E86AB;
            --secondary-color: #A23B72;
            --success-color: #06A77D;
            --warning-color: #F18F01;
            --danger-color: #C1121F;
            --light-bg: #F8F9FA;
            --dark-text: #1A1A1A;
            --border-color: #E0E0E0;
            --shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--dark-text);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeInDown 0.8s ease;
        }}

        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.95;
        }}

        /* Key Metrics Section */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
            animation: fadeInUp 0.8s ease;
        }}

        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}

        .metric-card .label {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }}

        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 5px;
        }}

        .metric-card .subtext {{
            font-size: 0.9em;
            color: #999;
        }}

        .metric-card.success .value {{
            color: var(--success-color);
        }}

        .metric-card.warning .value {{
            color: var(--warning-color);
        }}

        .metric-card.danger .value {{
            color: var(--danger-color);
        }}

        /* Charts Section */
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.8s ease 0.2s both;
        }}

        .chart-container h3 {{
            margin-bottom: 20px;
            color: var(--primary-color);
            font-size: 1.3em;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 10px;
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin-bottom: 15px;
        }}

        /* Visualizations Section */
        .visualizations-section {{
            margin-bottom: 40px;
        }}

        .visualizations-section h2 {{
            color: white;
            margin-bottom: 20px;
            font-size: 2em;
            animation: fadeInLeft 0.8s ease;
        }}

        .visualization-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
        }}

        .visualization-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.8s ease 0.3s both;
            transition: transform 0.3s ease;
        }}

        .visualization-card:hover {{
            transform: translateY(-5px);
        }}

        .visualization-card img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .visualization-title {{
            padding: 15px 20px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            font-weight: bold;
            font-size: 1em;
        }}

        /* Insights Section */
        .insights-section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.8s ease 0.4s both;
            margin-bottom: 40px;
        }}

        .insights-section h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 10px;
        }}

        .insight-item {{
            margin-bottom: 15px;
            padding: 12px 15px;
            background: var(--light-bg);
            border-left: 4px solid var(--primary-color);
            border-radius: 4px;
            transition: all 0.3s ease;
        }}

        .insight-item:hover {{
            background: #f0f0f0;
            transform: translateX(5px);
        }}

        .insight-item strong {{
            color: var(--primary-color);
        }}

        /* Confusion Matrix Display */
        .confusion-matrix {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
            font-size: 0.95em;
        }}

        .cm-cell {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }}

        .cm-tn {{
            background: #E8F5E9;
            border: 2px solid var(--success-color);
        }}

        .cm-tp {{
            background: #E8F5E9;
            border: 2px solid var(--success-color);
        }}

        .cm-fp {{
            background: #FFF3E0;
            border: 2px solid var(--warning-color);
        }}

        .cm-fn {{
            background: #FFEBEE;
            border: 2px solid var(--danger-color);
        }}

        .cm-cell .label {{
            font-size: 0.85em;
            color: #666;
            display: block;
            margin-bottom: 5px;
        }}

        .cm-cell .value {{
            font-size: 1.8em;
            display: block;
        }}

        /* Hyperparameters Section */
        .hyperparams {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .hyperparams h4 {{
            margin-bottom: 12px;
            font-size: 1.1em;
        }}

        .param-item {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .param-item:last-child {{
            border-bottom: none;
        }}

        .param-item span {{
            font-weight: bold;
        }}

        /* Medical Interpretation */
        .medical-box {{
            background: #E3F2FD;
            border-left: 5px solid var(--primary-color);
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .medical-box h4 {{
            color: var(--primary-color);
            margin-bottom: 10px;
        }}

        .medical-box p {{
            color: #1565C0;
            line-height: 1.6;
        }}

        /* Risk Level Badge */
        .risk-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
            margin: 5px 0;
        }}

        .risk-high {{
            background: #FFEBEE;
            color: var(--danger-color);
        }}

        .risk-medium {{
            background: #FFF3E0;
            color: var(--warning-color);
        }}

        .risk-low {{
            background: #E8F5E9;
            color: var(--success-color);
        }}

        /* Recommendations */
        .recommendations {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.8s ease 0.5s both;
        }}

        .recommendations h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid var(--secondary-color);
            padding-bottom: 10px;
        }}

        .recommendation-list {{
            list-style: none;
        }}

        .recommendation-list li {{
            padding: 15px;
            margin-bottom: 12px;
            background: var(--light-bg);
            border-radius: 8px;
            border-left: 4px solid var(--secondary-color);
            transition: all 0.3s ease;
        }}

        .recommendation-list li:hover {{
            background: #f0f0f0;
            transform: translateX(5px);
        }}

        .recommendation-list li::before {{
            content: "✓ ";
            color: var(--secondary-color);
            font-weight: bold;
            margin-right: 10px;
        }}

        /* Footer */
        footer {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            margin-top: 50px;
            backdrop-filter: blur(10px);
        }}

        footer p {{
            margin: 5px 0;
            font-size: 0.95em;
        }}

        /* Animations */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        /* Responsive Design */
        @media (max-width: 1024px) {{
            .charts-section {{
                grid-template-columns: 1fr;
            }}
            .visualization-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2em;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .visualization-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Print Styles */
        @media print {{
            body {{
                background: white;
            }}
            .metric-card, .chart-container, .visualization-card, .insights-section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🔬 SVM Medical Diagnosis</h1>
            <p>Intelligent Insights & Performance Dashboard</p>
        </header>

        <!-- Key Performance Metrics -->
        <div class="metrics-grid">
            <div class="metric-card success">
                <div class="label">Accuracy</div>
                <div class="value">{accuracy*100:.2f}%</div>
                <div class="subtext">Overall Correctness</div>
            </div>

            <div class="metric-card success">
                <div class="label">Precision</div>
                <div class="value">{precision*100:.2f}%</div>
                <div class="subtext">False Positive Rate</div>
            </div>

            <div class="metric-card success">
                <div class="label">Recall (Sensitivity)</div>
                <div class="value">{recall*100:.2f}%</div>
                <div class="subtext">Disease Detection</div>
            </div>

            <div class="metric-card success">
                <div class="label">F1 Score</div>
                <div class="value">{f1:.4f}</div>
                <div class="subtext">Precision-Recall Balance</div>
            </div>

            <div class="metric-card success">
                <div class="label">ROC-AUC</div>
                <div class="value">{roc_auc:.4f}</div>
                <div class="subtext">Classification Quality</div>
            </div>

            <div class="metric-card success">
                <div class="label">Best CV Score</div>
                <div class="value">{best_cv_score*100:.2f}%</div>
                <div class="subtext">Cross-Validation</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="charts-section">
            <!-- Metrics Comparison Chart -->
            <div class="chart-container">
                <h3>📊 Performance Metrics Comparison</h3>
                <div class="chart-wrapper">
                    <canvas id="metricsChart"></canvas>
                </div>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                    <strong>Interpretation:</strong> All metrics above 90% indicate excellent model performance. 
                    The balance between precision and recall is critical for medical diagnosis.
                </p>
            </div>

            <!-- Kernel Comparison Chart -->
            <div class="chart-container">
                <h3>🎯 Kernel Performance Comparison</h3>
                <div class="chart-wrapper">
                    <canvas id="kernelChart"></canvas>
                </div>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                    <strong>Best Kernel:</strong> {best_params['kernel'].upper()} 
                    <strong>Accuracy:</strong> {metrics_dict[best_params['kernel']]['accuracy']*100:.2f}%
                </p>
            </div>
        </div>

        <!-- Confusion Matrix Section -->
        <div class="chart-container" style="margin-bottom: 40px;">
            <h3>🎪 Confusion Matrix Breakdown</h3>
            <div class="confusion-matrix">
                <div class="cm-cell cm-tn">
                    <span class="label">True Negatives (TN)</span>
                    <span class="value">{tn}</span>
                    <span class="label">Benign Correct</span>
                </div>
                <div class="cm-cell cm-fp">
                    <span class="label">False Positives (FP)</span>
                    <span class="value">{fp}</span>
                    <span class="label">False Alarm</span>
                </div>
                <div class="cm-cell cm-fn">
                    <span class="label">False Negatives (FN)</span>
                    <span class="value">{fn}</span>
                    <span class="label">Missed Disease</span>
                </div>
                <div class="cm-cell cm-tp">
                    <span class="label">True Positives (TP)</span>
                    <span class="value">{tp}</span>
                    <span class="label">Disease Correct</span>
                </div>
            </div>

            <div class="medical-box">
                <h4>🏥 Medical Risk Assessment</h4>
                <p>
                    <strong>False Negative Rate:</strong> {fnr*100:.2f}% 
                    <span class="risk-badge {'risk-high' if fnr > 0.05 else 'risk-medium' if fnr > 0.02 else 'risk-low'}">
                        {'HIGH RISK' if fnr > 0.05 else 'MEDIUM RISK' if fnr > 0.02 else 'LOW RISK'}
                    </span>
                    <br>
                    <strong>False Positive Rate:</strong> {fpr*100:.2f}%
                    <span class="risk-badge {'risk-high' if fpr > 0.1 else 'risk-medium' if fpr > 0.05 else 'risk-low'}">
                        {'HIGH ALERT' if fpr > 0.1 else 'MEDIUM ALERT' if fpr > 0.05 else 'LOW ALERT'}
                    </span>
                </p>
                <p style="margin-top: 10px;">
                    Missing {int(fn)} actual disease cases is <strong>critical</strong> in medical diagnosis.
                    The current model correctly identifies {int(tp)} out of {int(tp+fn)} disease cases.
                </p>
            </div>
        </div>

        <!-- Hyperparameters Section -->
        <div class="chart-container" style="margin-bottom: 40px;">
            <h3>⚙️ Optimized Hyperparameters (GridSearchCV)</h3>
            <div class="hyperparams">
                <h4>Best Configuration Found:</h4>
                <div class="param-item">
                    <span>🔧 Kernel:</span> {best_params['kernel'].upper()}
                </div>
                <div class="param-item">
                    <span>⚡ C (Regularization):</span> {best_params['C']}
                </div>
                <div class="param-item">
                    <span>🎯 Gamma (Influence):</span> {best_params['gamma']}
                </div>
                <div class="param-item">
                    <span>📈 Cross-Validation Score:</span> {best_cv_score*100:.2f}%
                </div>
            </div>
            <div class="medical-box">
                <h4>Why These Parameters?</h4>
                <p>
                    The <strong>{best_params['kernel'].upper()}</strong> kernel was selected because it best captures 
                    the decision boundary in this medical dataset. The C value of <strong>{best_params['C']}</strong> 
                    balances regularization with training accuracy. These parameters were chosen through exhaustive 
                    GridSearchCV evaluation with 5-fold cross-validation.
                </p>
            </div>
        </div>

        <!-- Visualizations -->
        <div class="visualizations-section">
            <h2>📈 Detailed Visualizations</h2>
            <div class="visualization-grid">
                <div class="visualization-card">
                    <div class="visualization-title">Confusion Matrix Heatmap</div>
                    <img src="confusion_matrix_optimized svm.png" alt="Confusion Matrix">
                </div>
                <div class="visualization-card">
                    <div class="visualization-title">ROC Curve & AUC</div>
                    <img src="roc_curve_optimized svm.png" alt="ROC Curve">
                </div>
                <div class="visualization-card">
                    <div class="visualization-title">Decision Boundary (2D Projection)</div>
                    <img src="decision_boundary_optimized svm.png" alt="Decision Boundary">
                </div>
                <div class="visualization-card">
                    <div class="visualization-title">Kernel Comparison</div>
                    <img src="kernel_comparison.png" alt="Kernel Comparison">
                </div>
                <div class="visualization-card">
                    <div class="visualization-title">C Parameter Effect on Performance</div>
                    <img src="c_parameter_effect.png" alt="C Parameter">
                </div>
                <div class="visualization-card">
                    <div class="visualization-title">Gamma Parameter Effect on Performance</div>
                    <img src="gamma_parameter_effect.png" alt="Gamma Parameter">
                </div>
            </div>
        </div>

        <!-- Key Insights -->
        <div class="insights-section">
            <h2>💡 Key Insights & Analysis</h2>

            <h3 style="color: var(--primary-color); margin-top: 20px; margin-bottom: 10px;">Model Performance Insights</h3>
            <div class="insight-item">
                <strong>✅ Excellent Overall Accuracy:</strong> The model achieves {accuracy*100:.2f}% accuracy, 
                correctly classifying {int((accuracy) * (tp+tn+fp+fn))} out of {int(tp+tn+fp+fn)} cases.
            </div>
            <div class="insight-item">
                <strong>✅ High Sensitivity (Recall):</strong> {recall*100:.2f}% of actual disease cases are correctly 
                identified, minimizing missed diagnoses.
            </div>
            <div class="insight-item">
                <strong>✅ Strong Precision:</strong> {precision*100:.2f}% of positive predictions are correct, 
                reducing unnecessary patient anxiety from false alarms.
            </div>
            <div class="insight-item">
                <strong>✅ Balanced Performance:</strong> F1 Score of {f1:.4f} indicates excellent balance between 
                precision and recall, both critical for medical diagnosis.
            </div>

            <h3 style="color: var(--primary-color); margin-top: 20px; margin-bottom: 10px;">Feature & Algorithm Insights</h3>
            <div class="insight-item">
                <strong>🎯 Optimal Kernel Selected:</strong> {best_params['kernel'].upper()} kernel works best for this dataset, 
                indicating {'linear' if best_params['kernel'] == 'linear' else 'non-linear'} decision boundaries in the medical features.
            </div>
            <div class="insight-item">
                <strong>📊 Feature Scaling Impact:</strong> StandardScaler was essential - it ensured all 30 medical measurements 
                contributed equally to the decision boundary, preventing high-range features from dominating.
            </div>
            <div class="insight-item">
                <strong>🔍 Support Vectors:</strong> The model uses only support vectors (boundary points) for prediction, 
                making it memory-efficient and interpretable.
            </div>
            <div class="insight-item">
                <strong>⚙️ Hyperparameter Optimization:</strong> GridSearchCV tested 96 parameter combinations (4 kernels × 4 C values × 6 gamma values) 
                to find the optimal configuration with {best_cv_score*100:.2f}% cross-validation accuracy.
            </div>

            <h3 style="color: var(--primary-color); margin-top: 20px; margin-bottom: 10px;">Medical Applicability</h3>
            <div class="insight-item">
                <strong>🏥 Clinical Readiness:</strong> With {recall*100:.2f}% sensitivity and {precision*100:.2f}% precision, 
                this model is suitable as a <strong>decision support tool</strong> for radiologists and pathologists.
            </div>
            <div class="insight-item">
                <strong>⚠️ Risk Management:</strong> False negative rate of {fnr*100:.2f}% means approximately {int(fnr*100)} in 100 
                diseased patients might be missed. Recommend human expert review before finalizing diagnosis.
            </div>
            <div class="insight-item">
                <strong>👨‍⚕️ Integration Strategy:</strong> Best used as preliminary screening tool, with positive cases 
                referred for detailed specialist examination.
            </div>

            <h3 style="color: var(--primary-color); margin-top: 20px; margin-bottom: 10px;">Why SVM Succeeded Here</h3>
            <div class="insight-item">
                <strong>1️⃣ High-Dimensional Data:</strong> 30 medical features - SVM handles this well through kernel trick 
                and doesn't suffer from curse of dimensionality like some algorithms.
            </div>
            <div class="insight-item">
                <strong>2️⃣ Clear Separability:</strong> Medical measurements naturally separate benign from malignant cases, 
                and SVM excels at finding optimal separating hyperplanes.
            </div>
            <div class="insight-item">
                <strong>3️⃣ Robust Margins:</strong> Maximum margin principle ensures the decision boundary stays far from 
                training points, improving generalization to new patients.
            </div>
            <div class="insight-item">
                <strong>4️⃣ Interpretability:</strong> Support vectors identify the most informative cases, helping clinicians 
                understand which features matter most.
            </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations">
            <h2>🎯 Recommendations for Deployment</h2>
            <ul class="recommendation-list">
                <li><strong>Validation:</strong> Validate model on independent external dataset before clinical deployment</li>
                <li><strong>Monitoring:</strong> Continuously monitor model performance as new patient data arrives</li>
                <li><strong>Retraining:</strong> Retrain model quarterly or when performance drops below 95% accuracy</li>
                <li><strong>Ensemble:</strong> Combine SVM with other algorithms (Random Forest, Neural Networks) for robustness</li>
                <li><strong>Documentation:</strong> Maintain audit trail of all predictions for regulatory compliance</li>
                <li><strong>User Training:</strong> Educate clinicians on model limitations and when to seek expert review</li>
                <li><strong>Confidence Scores:</strong> Use probability estimates to flag uncertain predictions for review</li>
                <li><strong>Fairness Testing:</strong> Test for bias across demographic groups before deployment</li>
                <li><strong>API Development:</strong> Create REST API for easy integration into hospital information systems</li>
                <li><strong>Performance Dashboard:</strong> Set up real-time monitoring dashboard for model metrics</li>
            </ul>
        </div>

        <!-- Footer -->
        <footer>
            <p>🔬 SVM Medical Diagnosis Dashboard</p>
            <p>Generated with Industrial-Grade Machine Learning Pipeline</p>
            <p>Dataset: Breast Cancer Wisconsin | Algorithm: Support Vector Machine</p>
            <p>All visualizations and insights computed with high accuracy standards</p>
        </footer>
    </div>

    <script>
        // Metrics Comparison Chart
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        new Chart(metricsCtx, {{
            type: 'radar',
            data: {{
                labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Specificity', 'Sensitivity'],
                datasets: [{{
                    label: 'Model Performance',
                    data: [{accuracy:.4f}, {precision:.4f}, {recall:.4f}, {f1:.4f}, {specificity:.4f}, {sensitivity:.4f}],
                    borderColor: 'rgb(46, 134, 171)',
                    backgroundColor: 'rgba(46, 134, 171, 0.2)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointBackgroundColor: 'rgb(46, 134, 171)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'bottom'
                    }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 1,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100).toFixed(0) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Kernel Comparison Chart
        const kernelCtx = document.getElementById('kernelChart').getContext('2d');
        new Chart(kernelCtx, {{
            type: 'bar',
            data: {{
                labels: {list(metrics_dict.keys())},
                datasets: [{{
                    label: 'Accuracy',
                    data: {kernel_accuracies},
                    backgroundColor: [
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(78, 205, 196, 0.8)',
                        'rgba(69, 183, 209, 0.8)',
                        'rgba(255, 160, 122, 0.8)'
                    ],
                    borderColor: [
                        'rgb(255, 107, 107)',
                        'rgb(78, 205, 196)',
                        'rgb(69, 183, 209)',
                        'rgb(255, 160, 122)'
                    ],
                    borderWidth: 2,
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'x',
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'bottom'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100).toFixed(0) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """

    # Save HTML file
    html_filename = 'svm_insights_dashboard.html'
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Beautiful HTML dashboard created: {html_filename}")
        print(f"✓ Open the file in your web browser to view interactive insights")
        logger.info(f"HTML dashboard generated successfully: {html_filename}")

        # Also try to open the file in default browser
        import webbrowser
        webbrowser.open(html_filename)
        print(f"✓ Opening dashboard in your default browser...\n")

    except Exception as e:
        logger.error(f"Error generating HTML dashboard: {str(e)}")
        print(f"✗ Error creating HTML dashboard: {str(e)}\n")


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================


@log_execution_time
def main() -> None:
    """
    Main execution function - orchestrates the entire SVM pipeline.
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SUPPORT VECTOR MACHINE (SVM) FOR MEDICAL DIAGNOSIS".center(78) + "║")
    print("║" + "Industrial-Ready Implementation with Educational Focus".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # ====================================================================
        # PHASE 1: DATA LOADING & EXPLORATION
        # ====================================================================

        X, y, feature_descriptions = load_medical_dataset()
        explore_dataset(X, y)
        check_feature_correlation(X)

        # ====================================================================
        # PHASE 2: THEORY & CONCEPTS
        # ====================================================================

        explain_svm_fundamentals()
        explain_kernels()
        explain_hyperparameters()

        # ====================================================================
        # PHASE 3: DATA PREPARATION
        # ====================================================================

        X_train_scaled, X_test_scaled, y_train, y_test, scaler = prepare_data(X, y)
        explain_feature_scaling_importance()

        # ====================================================================
        # PHASE 4: MODEL TRAINING
        # ====================================================================

        # Train with different kernels
        models = train_svm_models(X_train_scaled, y_train)

        # Hyperparameter tuning
        best_model, best_params, grid_search = train_optimal_svm(X_train_scaled, y_train)

        # ====================================================================
        # PHASE 5: EVALUATION WITH DIFFERENT KERNELS
        # ====================================================================

        print_section("COMPARING DIFFERENT KERNELS")

        metrics_dict = {}
        for kernel_name, model in models.items():
            print(f"\n→ Evaluating {kernel_name.upper()} kernel:")
            kernel_metrics = evaluate_model(model, X_test_scaled, y_test, kernel_name.upper())
            metrics_dict[kernel_name] = kernel_metrics

        # ====================================================================
        # PHASE 6: OPTIMAL MODEL EVALUATION
        # ====================================================================

        optimal_metrics = evaluate_model(best_model, X_test_scaled, y_test, "OPTIMIZED SVM (GridSearchCV)")

        # ====================================================================
        # PHASE 7: VISUALIZATIONS
        # ====================================================================

        print_section("GENERATING VISUALIZATIONS")

        # Confusion matrix
        visualize_confusion_matrix(optimal_metrics['confusion_matrix'], "Optimized SVM")

        # ROC curve
        visualize_roc_curve(
            optimal_metrics['fpr'],
            optimal_metrics['tpr'],
            optimal_metrics['roc_auc'],
            "Optimized SVM"
        )

        # Decision boundary
        visualize_decision_boundary(
            X_train_scaled, y_train, best_model,
            feature_idx1=0, feature_idx2=1,
            model_name="Optimized SVM"
        )

        # Kernel comparison
        visualize_kernel_comparison(models, metrics_dict)

        # Hyperparameter effects
        visualize_c_parameter_effect(X_train_scaled, X_test_scaled, y_train, y_test)
        visualize_gamma_parameter_effect(X_train_scaled, X_test_scaled, y_train, y_test)

        # ====================================================================
        # PHASE 8: EXPLAINABILITY & INSIGHTS
        # ====================================================================

        explain_svm_performance(best_model, optimal_metrics, best_params, feature_descriptions)
        explain_svm_vs_other_algorithms()

        # ====================================================================
        # SUMMARY
        # ====================================================================

        print_section("FINAL SUMMARY & KEY TAKEAWAYS")

        print("""
🎓 WHAT YOU'VE LEARNED:
═══════════════════════════════════════════════════════════════════════════════

1. SVM FUNDAMENTALS:
   ✓ SVM finds optimal hyperplane with maximum margin
   ✓ Support vectors are critical for decision boundary
   ✓ Kernel trick enables non-linear classification
   ✓ Feature scaling is essential for SVM performance

2. FEATURE SCALING:
   ✓ StandardScaler normalizes features to mean=0, std=1
   ✓ Prevents features with large ranges from dominating
   ✓ Improves convergence speed and hyperparameter tuning
   ✓ MANDATORY for distance-based algorithms like SVM

3. KERNELS & WHEN TO USE THEM:
   ✓ Linear: When data is linearly separable
   ✓ RBF: Default choice for non-linear problems
   ✓ Polynomial: For specific polynomial relationships
   ✓ Sigmoid: When similar to neural network boundaries

4. HYPERPARAMETER TUNING:
   ✓ C: Controls regularization strength
   ✓ Gamma: Controls influence of training examples
   ✓ GridSearchCV finds optimal combination via cross-validation
   ✓ Always use cross-validation to prevent overfitting

5. EVALUATION METRICS FOR MEDICAL DIAGNOSIS:
   ✓ Accuracy: Overall correctness (not enough alone)
   ✓ Precision: False positive rate (important for this domain)
   ✓ Recall: False negative rate (CRITICAL - missing disease is dangerous)
   ✓ F1 Score: Harmonic mean (balances precision and recall)
   ✓ ROC-AUC: Threshold-independent performance measure
   ✓ Confusion Matrix: Detailed breakdown of all prediction types

6. MEDICAL APPLICATION INSIGHTS:
   ✓ SVM achieves excellent accuracy on this dataset
   ✓ Must be used as support tool, not replacement for doctors
   ✓ Missing cases (false negatives) more dangerous than false alarms
   ✓ Feature scaling prevents biased learning
   ✓ Regular revalidation needed with new data

7. INDUSTRIAL BEST PRACTICES:
   ✓ Use reproducible random seeds
   ✓ Implement proper error handling and logging
   ✓ Measure execution time and track performance
   ✓ Document all assumptions and design decisions
   ✓ Create visualizations for stakeholder communication
   ✓ Follow PEP8 and clean code principles

8. WHEN SVM IS IDEAL:
   ✓ High-dimensional data (30+ features)
   ✓ Binary classification problems
   ✓ Limited training data (100-10,000 samples)
   ✓ When interpretability matters
   ✓ When regulatory approval is needed

🔬 NEXT STEPS FOR PRODUCTION:
═════════════════════════════

1. Validate on independent external dataset
2. Implement cross-platform testing
3. Add model persistence (save/load)
4. Create API endpoint for predictions
5. Implement monitoring for model drift
6. Combine with other algorithms (ensemble)
7. Document feature engineering choices
8. Establish retraining schedule
9. Create interpretability reports
10. Implement confidence intervals for predictions

📊 KEY METRICS FROM THIS SESSION:
═════════════════════════════════
""")

        print(f"Best Model Configuration:")
        print(f"  Kernel: {best_params['kernel']}")
        print(f"  C: {best_params['C']}")
        print(f"  Gamma: {best_params['gamma']}")
        print(f"  Test Accuracy: {optimal_metrics['accuracy']:.4f} ({optimal_metrics['accuracy']*100:.2f}%)")
        print(f"  Precision: {optimal_metrics['precision']:.4f}")
        print(f"  Recall: {optimal_metrics['recall']:.4f}")
        print(f"  F1 Score: {optimal_metrics['f1']:.4f}")
        print(f"  ROC-AUC: {optimal_metrics['roc_auc']:.4f}")

        print("\n✅ ALL PHASES COMPLETED SUCCESSFULLY!")
        print("📁 Check current directory for saved visualizations (*.png files)")
        print("📝 Check 'svm_medical_diagnosis.log' for detailed execution log")

        # ====================================================================
        # PHASE 9: GENERATE INTERACTIVE HTML DASHBOARD
        # ====================================================================

        generate_html_dashboard(optimal_metrics, best_params, metrics_dict, grid_search)

        logger.info("SVM medical diagnosis pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}")
        raise


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()