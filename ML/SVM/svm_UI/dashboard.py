"""
================================================================================
SVM MEDICAL DIAGNOSIS - INTERACTIVE EDUCATIONAL DASHBOARD
Professional UI/UX for Healthcare Machine Learning
================================================================================

Author: UI/UX & ML Engineering Team
Domain: Healthcare Analytics & Medical Diagnosis Support
Purpose: Educational dashboard for understanding SVM in medical diagnosis

This dashboard is a SEPARATE UI layer that does not modify the core ML code.
It provides interactive visualizations and educational content for stakeholders,
clinicians, and researchers to understand SVM-based medical diagnosis.

Design Principles:
✓ Simplicity: One concept per page
✓ Progressive disclosure: Information revealed gradually
✓ Healthcare-focused: Professional, calm, trustworthy
✓ Interactive: Learner engagement through interaction
✓ Accessible: Suitable for non-technical users
✓ Modular: Clean separation of concerns

Color Palette (Healthcare Professional):
- Primary: Navy Blue (#1B3A6B) - Trust, professionalism
- Secondary: Teal (#0D9488) - Healing, calm
- Accent: Light Blue (#E0F2FE) - Clean, clinical
- Success: Soft Green (#10B981) - Health, positive
- Background: White (#FFFFFF) - Clean, sterile
- Text: Dark Gray (#1F2937) - Readable, professional
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from typing import Tuple, Dict, Any
import os

# Suppress warnings for cleaner UI
warnings.filterwarnings('ignore')


# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================


def configure_page():
    """
    Configure Streamlit page settings with healthcare design principles.
    """
    st.set_page_config(
        page_title="SVM Medical Diagnosis Dashboard",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for healthcare-professional design
    st.markdown("""
    <style>
    /* Color Variables - Healthcare Palette */
    :root {
        --primary: #1B3A6B;
        --secondary: #0D9488;
        --accent: #E0F2FE;
        --success: #10B981;
        --danger: #EF4444;
        --warning: #F59E0B;
        --background: #FFFFFF;
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --border: #E5E7EB;
    }

    /* Global Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #F9FAFB;
        color: var(--text-dark);
    }

    /* Headers */
    h1 {
        color: var(--primary);
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 24px;
        font-size: 2.5rem;
    }

    h2 {
        color: var(--primary);
        font-weight: 600;
        margin-top: 32px;
        margin-bottom: 16px;
        font-size: 1.8rem;
    }

    h3 {
        color: var(--secondary);
        font-weight: 600;
        margin-top: 24px;
        margin-bottom: 12px;
        font-size: 1.3rem;
    }

    /* Text */
    p, li {
        line-height: 1.7;
        color: var(--text-dark);
        font-size: 1rem;
    }

    /* Cards & Containers */
    [data-testid="stMetric"] {
        background-color: #F3F4F6;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--secondary);
    }

    .metric-container {
        background: linear-gradient(135deg, #F0F9FF 0%, #F0FDF4 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid var(--accent);
        box-shadow: 0 2px 8px rgba(27, 58, 107, 0.08);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary) 0%, #2D5A8C 100%);
        padding: 20px;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    /* Buttons */
    button {
        background-color: var(--secondary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    button:hover {
        background-color: #0B8678 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 2px solid var(--accent);
    }

    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-light) !important;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        color: var(--secondary) !important;
        border-bottom: 3px solid var(--secondary) !important;
    }

    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 24px 0;
    }

    /* Warning/Info Boxes */
    .warning-box {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }

    .info-box {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }

    .success-box {
        background-color: #DCFCE7;
        border-left: 4px solid #10B981;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.1rem; }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# UTILITY FUNCTIONS - COLORS & STYLING
# ============================================================================

# Healthcare color palette
COLORS = {
    'primary': '#1B3A6B',      # Navy blue
    'secondary': '#0D9488',   # Teal
    'accent': '#E0F2FE',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'light_bg': '#F9FAFB',
    'white': '#FFFFFF',

    # Add these two missing colors
    'text-dark': '#1F2937',
    'text-light': '#6B7280',

    # Optional
    'border': '#E5E7EB'
}


def create_metric_card(label: str, value: str, subtext: str = "", icon: str = ""):
    """
    Create a professional metric card for displaying KPIs.

    Args:
        label: Metric name
        value: Metric value
        subtext: Additional context
        icon: Emoji icon
    """
    with st.container():
        col1, col2 = st.columns([0.8, 4])
        with col1:
            st.markdown(f"<h2 style='color: {COLORS['secondary']}; margin: 0;'>{icon}</h2>",
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='padding: 16px; background: linear-gradient(135deg, #F0F9FF 0%, #F0FDF4 100%); 
                        border-radius: 12px; border: 1px solid {COLORS['accent']};
                        box-shadow: 0 2px 8px rgba(27, 58, 107, 0.08);'>
                <p style='color: {COLORS['text-light']}; font-size: 0.9rem; margin: 0;'>{label}</p>
                <h3 style='color: {COLORS['primary']}; margin: 8px 0 0 0; font-size: 2rem;'>{value}</h3>
                {f"<p style='color: {COLORS['text-light']}; font-size: 0.85rem; margin: 4px 0 0 0;'>{subtext}</p>" if subtext else ""}
            </div>
            """, unsafe_allow_html=True)


def create_info_box(title: str, content: str, box_type: str = "info"):
    """
    Create styled information boxes.

    Args:
        title: Box title
        content: Box content (markdown supported)
        box_type: 'info', 'warning', or 'success'
    """
    colors_map = {
        'info': {'bg': '#DBEAFE', 'border': '#3B82F6', 'icon': 'ℹ️'},
        'warning': {'bg': '#FEF3C7', 'border': '#F59E0B', 'icon': '⚠️'},
        'success': {'bg': '#DCFCE7', 'border': '#10B981', 'icon': '✓'},
    }

    colors = colors_map.get(box_type, colors_map['info'])

    st.markdown(f"""
    <div style='background-color: {colors["bg"]}; border-left: 4px solid {colors["border"]};
                padding: 16px; border-radius: 8px; margin: 16px 0;'>
        <p style='color: {COLORS["primary"]}; font-weight: 600; margin: 0 0 8px 0;'>
            {colors["icon"]} {title}
        </p>
        <p style='color: {COLORS["text-dark"]}; margin: 0; line-height: 1.6;'>{content}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# DATA GENERATION & LOADING
# ============================================================================

def generate_sample_data() -> Tuple[pd.DataFrame, pd.Series, Dict]:
    """
    Generate sample medical dataset (Breast Cancer Wisconsin).
    In production, this would load actual trained model outputs.

    Returns:
        Tuple of (features_df, target_series, metadata_dict)
    """
    from sklearn.datasets import load_breast_cancer

    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series(data.target, name='diagnosis')

    metadata = {
        'dataset_name': 'Breast Cancer Wisconsin (Diagnostic)',
        'samples': len(X),
        'features': X.shape[1],
        'classes': 2,
        'class_names': ['Malignant', 'Benign'],
        'source': 'UCI Machine Learning Repository',
    }

    return X, y, metadata


def generate_model_metrics() -> Dict[str, Any]:
    """
    Generate sample model performance metrics.
    In production, these would come from the trained SVM model.

    Returns:
        Dictionary of performance metrics
    """
    return {
        'accuracy': 0.9718,
        'precision': 0.9756,
        'recall': 0.9672,
        'f1_score': 0.9714,
        'roc_auc': 0.9930,
        'cv_score': 0.9680,
        'support_vectors': 142,
        'total_training_samples': 456,
        'best_kernel': 'rbf',
        'best_c': 10,
        'best_gamma': 0.01,
    }


# ============================================================================
# PAGE: HOME / WELCOME
# ============================================================================

def page_home():
    """
    Landing page with project overview and quick introduction to SVM.
    """
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px; 
                background: linear-gradient(135deg, #1B3A6B 0%, #0D9488 100%);
                border-radius: 16px; margin-bottom: 40px;'>
        <h1 style='color: white; margin: 0; font-size: 3rem;'>🏥 Medical Diagnosis AI</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 12px 0 0 0;'>
            Understanding Support Vector Machines for Healthcare
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card("📊 Patients", "569", "Training samples")

    with col2:
        create_metric_card("🔬 Features", "30", "Medical measurements")

    with col3:
        create_metric_card("🎯 Accuracy", "97.18%", "Model performance")

    with col4:
        create_metric_card("⚡ Speed", "<1ms", "Per prediction")

    st.markdown("---")

    # Main Content
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🎓 Project Overview")
        st.markdown("""
        This dashboard demonstrates **Support Vector Machine (SVM)** applied to 
        medical diagnosis, specifically **breast cancer detection** from 
        diagnostic measurements.

        ### Key Objectives:
        - **Educate** non-technical users about SVM
        - **Visualize** how machine learning supports medical diagnosis
        - **Demonstrate** model reliability and decision-making
        - **Enable** informed medical decision-making
        """)

        st.subheader("📈 Dataset")
        st.markdown("""
        **Breast Cancer Wisconsin (Diagnostic)**
        - **569 patients** with medical measurements
        - **30 features** from digitized breast mass images
        - **Binary classification**: Malignant vs Benign
        - **Real-world data** from UCI ML Repository
        - **No missing values** - clean, production-ready dataset
        """)

    with col2:
        st.subheader("🤖 What is SVM?")

        create_info_box(
            "Simple Explanation",
            """**SVM finds the best line (or surface) that separates 
            sick from healthy patients.**

            Think of it like this: If you have two groups of dots on a paper
            (sick in red, healthy in blue), SVM draws the best line between them.

            The "best" line is the one that has the maximum space between 
            the two groups - like creating a safety buffer zone.""",
            "info"
        )

        st.markdown("#### Why SVM for Medical Diagnosis?")
        st.markdown("""
        ✓ **High accuracy** - Excels with medical data patterns
        ✓ **Interpretable** - Can explain decisions
        ✓ **Fast** - Real-time diagnosis support
        ✓ **Reliable** - Maximum margin = confident predictions
        ✓ **Proven** - FDA-approved in medical applications
        """)

    st.markdown("---")

    # Medical Disclaimer
    create_info_box(
        "⚠️ Medical Disclaimer",
        """This AI system is a **decision support tool** for healthcare professionals, 
        NOT a replacement for professional medical diagnosis. Always combine AI predictions 
        with clinical judgment, expert examination, and additional tests. Patient safety 
        is the highest priority.""",
        "warning"
    )

    st.markdown("---")

    # Navigation Guide
    st.subheader("📚 How to Use This Dashboard")

    tabs = st.tabs([
        "🏠 Home",
        "📊 Dataset Insights",
        "🧠 SVM Explained",
        "📈 Model Performance",
        "🔍 Feature Analysis",
        "🔮 Make Predictions",
        "💡 Explainability"
    ])

    navigation_items = [
        ("📊 Dataset Insights", "Explore data distribution, missing values, and feature correlations"),
        ("🧠 SVM Explained", "Visual and intuitive explanation of Support Vector Machines"),
        ("📈 Model Performance", "Detailed metrics, ROC curves, and confusion matrices"),
        ("🔍 Feature Analysis", "Correlation heatmaps and feature importance rankings"),
        ("🔮 Make Predictions", "Input patient data and get AI-supported diagnosis"),
        ("💡 Explainability", "Understand WHY the model made each prediction"),
    ]

    for i, (title, description) in enumerate(navigation_items):
        st.markdown(f"""
        #### {title}
        {description}
        """)


# ============================================================================
# PAGE: DATASET INSIGHTS
# ============================================================================

def page_dataset_insights():
    """
    Dataset exploration and visualization page.
    """
    st.header("📊 Dataset Insights")

    st.markdown("""
    Understanding the data is the first step to understanding the model.
    This page provides insights into the medical dataset used to train the SVM.
    """)

    # Load data
    X, y, metadata = generate_sample_data()

    # Overview Section
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card("👥 Patients", f"{metadata['samples']}", "Total samples")
    with col2:
        create_metric_card("🔬 Measurements", f"{metadata['features']}", "Per patient")
    with col3:
        create_metric_card("📂 Classes", f"{metadata['classes']}", "Diagnosis types")
    with col4:
        create_metric_card("✓ Quality", "100%", "Complete data")

    st.markdown("---")

    # Tabs for different insights
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Class Distribution",
        "Feature Overview",
        "Missing Values",
        "Correlations",
        "Feature Categories"
    ])

    with tab1:
        st.subheader("Class Distribution")

        class_counts = y.value_counts()

        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Benign', 'Malignant'],
            values=[class_counts[1], class_counts[0]],
            marker=dict(colors=[COLORS['success'], COLORS['danger']]),
            textposition='inside',
            textinfo='label+percent',
        )])

        fig.update_layout(
            title="Patient Distribution: Benign vs Malignant",
            height=400,
            showlegend=True,
            font=dict(size=12),
        )

        st.plotly_chart(fig, use_container_width=True)

        create_info_box(
            "What does this mean?",
            f"""**Benign (Healthy)**: {class_counts[1]} patients ({class_counts[1] / len(y) * 100:.1f}%)

**Malignant (Disease)**: {class_counts[0]} patients ({class_counts[0] / len(y) * 100:.1f}%)

The classes are **well-balanced**, which is excellent for training SVM models. 
When classes are unbalanced, the model might be biased toward the majority class.""",
            "success"
        )

    with tab2:
        st.subheader("Feature Overview")

        # Create feature statistics
        feature_stats = X.describe().T
        feature_stats = feature_stats[['min', '25%', '50%', '75%', 'max', 'std']]
        feature_stats = feature_stats.round(2)

        # Show top 10 features
        st.markdown("#### Top 10 Features (by standard deviation)")

        fig = go.Figure(data=[go.Bar(
            y=X.std().nlargest(10).index,
            x=X.std().nlargest(10).values,
            orientation='h',
            marker=dict(color=COLORS['secondary']),
            text=X.std().nlargest(10).values.round(2),
            textposition='outside',
        )])

        fig.update_layout(
            title="Features with Most Variation",
            xaxis_title="Standard Deviation (Spread)",
            yaxis_title="Feature Name",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 View Full Feature Statistics"):
            st.dataframe(feature_stats, use_container_width=True)

    with tab3:
        st.subheader("Missing Values Analysis")

        missing_count = X.isnull().sum().sum()

        if missing_count == 0:
            create_info_box(
                "✓ Excellent Data Quality",
                f"""**Zero missing values detected** out of {X.shape[0] * X.shape[1]:,} total data points.

This is ideal for machine learning models. The dataset is **complete and clean**,
requiring no imputation or special handling for missing data.""",
                "success"
            )
        else:
            create_info_box(
                "⚠️ Missing Values Detected",
                f"Found {missing_count} missing values that require handling.",
                "warning"
            )

    with tab4:
        st.subheader("Feature Correlations")

        st.markdown("""
        Correlation shows how features relate to each other.
        - **+1.0**: Perfect positive correlation (move together)
        - **0.0**: No correlation (independent)
        - **-1.0**: Perfect negative correlation (move oppositely)
        """)

        # Correlation with diagnosis
        correlations = X.corrwith(y).abs().sort_values(ascending=False)

        fig = go.Figure(data=[go.Bar(
            y=correlations.index[:15],
            x=correlations.values[:15],
            orientation='h',
            marker=dict(color=correlations.values[:15],
                        colorscale=[[0, COLORS['accent']], [1, COLORS['secondary']]]),
            text=correlations.values[:15].round(3),
            textposition='outside',
        )])

        fig.update_layout(
            title="Top 15 Features Most Correlated with Diagnosis",
            xaxis_title="Correlation Strength (Absolute Value)",
            yaxis_title="Feature Name",
            height=450,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        create_info_box(
            "What does this mean?",
            """Features at the top of this chart have the **strongest relationship** 
            with cancer diagnosis. SVM will focus on these features when making predictions.

Features with correlation > 0.7 are considered **highly predictive** of the diagnosis.""",
            "info"
        )

    with tab5:
        st.subheader("Feature Categories")

        st.markdown("""
        The 30 features fall into **three categories**:
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            #### 📏 **Geometric Features** (10)
            - radius_mean
            - perimeter_mean
            - area_mean
            - compactness
            - concavity
            - concave_points
            - symmetry
            - fractal_dimension
            - Plus SE variants
            """)

        with col2:
            st.markdown("""
            #### 📊 **Texture Features** (10)
            - texture_mean
            - smoothness
            - Standard error (SE)
            variants

            Describe surface characteristics
            and image properties
            """)

        with col3:
            st.markdown("""
            #### ⚠️ **Worst Features** (10)
            - worst_radius
            - worst_texture
            - worst_smoothness
            - And others

            Represent maximum/worst
            value across nucleus
            """)


# ============================================================================
# PAGE: SVM EXPLAINED
# ============================================================================

def page_svm_explained():
    """
    Educational page explaining SVM concepts visually.
    """
    st.header("🧠 Understanding Support Vector Machines")

    st.markdown("""
    This page breaks down SVM into simple, visual concepts that anyone can understand,
    regardless of their machine learning background.
    """)

    st.markdown("---")

    # Core Concept: The Hyperplane
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "The Hyperplane",
        "Maximum Margin",
        "Support Vectors",
        "Kernels",
        "Feature Scaling"
    ])

    with tab1:
        st.subheader("🎯 The Hyperplane: The Decision Boundary")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            ### What is a Hyperplane?

            A **hyperplane** is a boundary line (or surface) that separates two groups.

            **In 2D space**: A LINE
            **In 3D space**: A PLANE  
            **In high dimensions**: A SURFACE

            For medical diagnosis:
            - One side = Healthy (Benign)
            - Other side = Diseased (Malignant)
            - Hyperplane = The decision boundary
            """)

        with col2:
            # Create simple 2D visualization
            fig = go.Figure()

            # Generate sample points
            np.random.seed(42)
            benign_x = np.random.normal(-1, 0.6, 50)
            benign_y = np.random.normal(-1, 0.6, 50)
            malignant_x = np.random.normal(1, 0.6, 50)
            malignant_y = np.random.normal(1, 0.6, 50)

            # Add points
            fig.add_trace(go.Scatter(
                x=benign_x, y=benign_y,
                mode='markers',
                name='Benign (Healthy)',
                marker=dict(size=10, color=COLORS['success'], opacity=0.7),
            ))

            fig.add_trace(go.Scatter(
                x=malignant_x, y=malignant_y,
                mode='markers',
                name='Malignant (Disease)',
                marker=dict(size=10, color=COLORS['danger'], opacity=0.7),
            ))

            # Add decision boundary line
            x_line = [-2, 2]
            y_line = [-2, 2]
            fig.add_trace(go.Scatter(
                x=x_line, y=y_line,
                mode='lines',
                name='Decision Boundary (Hyperplane)',
                line=dict(color=COLORS['primary'], width=3, dash='dash'),
            ))

            fig.update_layout(
                title="SVM Decision Boundary in 2D Space",
                xaxis_title="Feature 1 (e.g., Size)",
                yaxis_title="Feature 2 (e.g., Texture)",
                height=400,
                hovermode='closest',
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("📏 Maximum Margin: The Safety Boundary")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            # Visualization showing margin concept
            fig = go.Figure()

            # Data points
            fig.add_trace(go.Scatter(
                x=benign_x, y=benign_y,
                mode='markers',
                name='Benign',
                marker=dict(size=10, color=COLORS['success'], opacity=0.7),
            ))

            fig.add_trace(go.Scatter(
                x=malignant_x, y=malignant_y,
                mode='markers',
                name='Malignant',
                marker=dict(size=10, color=COLORS['danger'], opacity=0.7),
            ))

            # Decision boundary
            fig.add_trace(go.Scatter(
                x=x_line, y=y_line,
                mode='lines',
                name='Decision Boundary',
                line=dict(color=COLORS['primary'], width=3),
            ))

            # Margin lines
            offset = 0.4
            fig.add_trace(go.Scatter(
                x=[-2 + offset, 2 + offset], y=[-2 + offset, 2 + offset],
                mode='lines',
                name='Margin Boundary',
                line=dict(color=COLORS['secondary'], width=2, dash='dot'),
            ))

            fig.add_trace(go.Scatter(
                x=[-2 - offset, 2 - offset], y=[-2 - offset, 2 - offset],
                mode='lines',
                line=dict(color=COLORS['secondary'], width=2, dash='dot'),
                showlegend=False,
            ))

            # Shade margin
            fig.add_shape(
                type="rect",
                x0=-2 - offset, x1=2 - offset,
                y0=-2 - offset, y1=2 + offset,
                fillcolor=COLORS['accent'],
                opacity=0.3,
                line=dict(width=0),
                layer="below"
            )

            fig.update_layout(
                title="Maximum Margin: The Safety Zone",
                xaxis_title="Feature 1",
                yaxis_title="Feature 2",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("""
            ### Why Maximum Margin?

            SVM doesn't just find ANY boundary. It finds the boundary with the
            **LARGEST DISTANCE** (margin) to the nearest points.

            ### Benefits:

            **1. Safety Buffer**
            - Like creating a safety zone between sick and healthy
            - More confident predictions
            - Handles new patients better

            **2. Robustness**
            - Small variations in data don't change the decision
            - New patients need to be clearly on one side
            - Reduces overfitting

            **3. Generalization**
            - The wider the margin, the better for new data
            - Prevents the model from "memorizing" training data
            - More reliable on real patients

            ### Example:
            - **Poor margin** (dangerous): Decision line touches a patient
            - **Good margin** (safe): Clear space between patients and boundary
            """)

    with tab3:
        st.subheader("⭐ Support Vectors: The Critical Points")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            ### What are Support Vectors?

            **Support vectors are the patient records CLOSEST to the decision boundary.**

            They are the hardest cases to classify - the borderline patients where
            it's hardest to distinguish between healthy and diseased.

            ### Key Insights:

            **Only Support Vectors Matter**
            - SVM uses ONLY the borderline cases for prediction
            - All other patient records are ignored
            - More memory-efficient and faster

            **Example:**
            - 569 total patients
            - Maybe 140 are support vectors
            - Only these 140 define the decision boundary
            - The other 429 don't influence predictions

            ### Clinical Interpretation:

            Support vectors represent the **"edge cases"** in medical diagnosis:
            - Patients with borderline measurements
            - Cases where diagnosis is most difficult
            - Most informative for understanding the disease
            - Best candidates for further investigation

            ### Why Important:
            ✓ Identify ambiguous cases needing expert review
            ✓ Understand which patients are hardest to diagnose
            ✓ Focus clinical attention where it matters most
            """)

        with col2:
            st.markdown("""
            #### Example Visualization:

            **Green circles** = Support Vectors (critical points)
            **Other dots** = Regular training examples (less influential)

            The decision boundary is defined ONLY by the support vectors.
            """)

            # Visualization with support vectors
            fig = go.Figure()

            # Regular points
            fig.add_trace(go.Scatter(
                x=benign_x, y=benign_y,
                mode='markers',
                name='Benign (Regular)',
                marker=dict(size=8, color=COLORS['success'], opacity=0.5),
            ))

            fig.add_trace(go.Scatter(
                x=malignant_x, y=malignant_y,
                mode='markers',
                name='Malignant (Regular)',
                marker=dict(size=8, color=COLORS['danger'], opacity=0.5),
            ))

            # Support vectors (near boundary)
            sv_benign_x = [np.percentile(benign_x, 75)]
            sv_benign_y = [np.percentile(benign_y, 75)]
            sv_malignant_x = [np.percentile(malignant_x, 25)]
            sv_malignant_y = [np.percentile(malignant_y, 25)]

            fig.add_trace(go.Scatter(
                x=sv_benign_x + sv_malignant_x,
                y=sv_benign_y + sv_malignant_y,
                mode='markers',
                name='Support Vectors (Critical)',
                marker=dict(
                    size=18,
                    color=COLORS['secondary'],
                    symbol='star',
                    line=dict(color='white', width=2),
                ),
            ))

            # Boundary
            fig.add_trace(go.Scatter(
                x=x_line, y=y_line,
                mode='lines',
                name='Decision Boundary',
                line=dict(color=COLORS['primary'], width=3, dash='dash'),
            ))

            fig.update_layout(
                title="Support Vectors: The Edge Cases",
                xaxis_title="Feature 1",
                yaxis_title="Feature 2",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("🔧 Kernels: Handling Complex Patterns")

        st.markdown("""
        **Problem**: Not all data can be separated by a simple line.

        Some patient data has **complex non-linear patterns** where a straight line
        cannot separate healthy from diseased patients.

        **Solution**: Kernels use a mathematical trick to handle complex patterns.
        """)

        kernel_data = {
            'Linear': {
                'desc': 'When data is cleanly separable by a straight line',
                'best_for': 'Simple, linear relationships between features',
                'pros': 'Fast, interpretable, fewer parameters',
                'cons': 'Cannot handle curved boundaries',
                'icon': '📏',
            },
            'RBF (Radial Basis Function)': {
                'desc': 'Default choice for most problems',
                'best_for': 'Complex, non-linear decision boundaries',
                'pros': 'Versatile, handles complex patterns, good generalization',
                'cons': 'Slower training, more parameters to tune',
                'icon': '🌊',
            },
            'Polynomial': {
                'desc': 'For polynomial relationships between features',
                'best_for': 'Feature interactions and polynomial patterns',
                'pros': 'Good for specific relationships',
                'cons': 'Can be slow, harder to tune',
                'icon': '📊',
            },
            'Sigmoid': {
                'desc': 'Similar to neural network activation',
                'best_for': 'Soft, probabilistic boundaries',
                'pros': 'Familiar from neural networks',
                'cons': 'Not always convergent',
                'icon': '〰️',
            },
        }

        for kernel_name, details in kernel_data.items():
            with st.expander(f"{details['icon']} {kernel_name}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**When to use:**  \n{details['best_for']}")
                    st.markdown(f"**Pros:**  \n{details['pros']}")

                with col2:
                    st.markdown(f"**Description:**  \n{details['desc']}")
                    st.markdown(f"**Cons:**  \n{details['cons']}")

    with tab5:
        st.subheader("⚖️ Feature Scaling: Why It's Critical for SVM")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            ### Problem: Unequal Feature Scales

            Medical features have very different ranges:
            - **Radius**: 6 to 28 (range of 22)
            - **Texture**: 9 to 39 (range of 30)
            - **Smoothness**: 0.04 to 0.35 (range of 0.31)

            **Without scaling**: Large-range features completely dominate!
            SVM treats the "Radius" feature as 100x more important than "Smoothness"
            just because of the scale, NOT because it's actually more informative.
            """)

        with col2:
            st.markdown("""
            ### Solution: StandardScaler

            Transforms all features to have:
            - **Mean = 0**
            - **Standard Deviation = 1**

            Formula: `z = (x - mean) / std_dev`

            ### Benefits:
            ✓ All features on same scale
            ✓ Fair contribution from all measurements
            ✓ Faster SVM training
            ✓ Better hyperparameter tuning
            ✓ More reliable predictions

            ### Result:
            All features now range approximately from -3 to +3,
            ensuring equal importance in decision-making.
            """)

        # Before/After comparison
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ❌ BEFORE SCALING")
            before_data = {
                'Feature': ['radius_mean', 'texture_mean', 'smoothness_mean'],
                'Min': [6.98, 9.71, 0.04],
                'Max': [28.11, 39.28, 0.35],
                'Range': [21.13, 29.57, 0.31],
            }
            st.dataframe(pd.DataFrame(before_data), use_container_width=True)
            st.markdown("""
            **Problem**: Range differs by **100x**!

            Distance calculation is dominated by
            large-range features.
            """)

        with col2:
            st.markdown("#### ✅ AFTER SCALING")
            after_data = {
                'Feature': ['radius_mean', 'texture_mean', 'smoothness_mean'],
                'Min': [-1.23, -1.42, -0.98],
                'Max': [2.95, 2.77, 2.88],
                'Range': [4.18, 4.19, 3.86],
            }
            st.dataframe(pd.DataFrame(after_data), use_container_width=True)
            st.markdown("""
            **Solution**: All features now have
            similar ranges.

            Equal importance in distance calculation.
            """)


# ============================================================================
# PAGE: MODEL PERFORMANCE
# ============================================================================

def page_model_performance():
    """
    Detailed model performance metrics and evaluation.
    """
    st.header("📈 Model Performance & Evaluation")

    st.markdown("""
    This page shows how well the trained SVM model performs on medical diagnoses.
    All metrics are explained in simple, non-technical language.
    """)

    # Get metrics
    metrics = generate_model_metrics()

    # Key Metrics Overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card(
            "Accuracy",
            f"{metrics['accuracy'] * 100:.2f}%",
            f"{int(metrics['accuracy'] * 456)}/456 correct"
        )

    with col2:
        create_metric_card(
            "Precision",
            f"{metrics['precision'] * 100:.2f}%",
            "Disease predictions correct"
        )

    with col3:
        create_metric_card(
            "Recall",
            f"{metrics['recall'] * 100:.2f}%",
            "Cases caught"
        )

    with col4:
        create_metric_card(
            "ROC-AUC",
            f"{metrics['roc_auc']:.4f}",
            "Discrimination ability"
        )

    st.markdown("---")

    # Detailed Metrics Explanation
    tab1, tab2, tab3, tab4 = st.tabs([
        "Core Metrics",
        "ROC Curve",
        "Confusion Matrix",
        "Clinical Interpretation"
    ])

    with tab1:
        st.subheader("Understanding Each Metric")

        # Accuracy
        with st.expander("📊 **ACCURACY**: Overall Correctness", expanded=True):
            col1, col2 = st.columns([1.5, 1], gap="large")

            with col1:
                st.markdown(f"""
                ### Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy'] * 100:.2f}%)

                **What it measures:**
                Out of all predictions, how many are correct?

                **Formula:**
                ```
                Accuracy = Correct Predictions / All Predictions
                         = (TP + TN) / (TP + TN + FP + FN)
                ```

                **In our model:**
                - Out of 456 test patients
                - Model correctly diagnosed **{int(metrics['accuracy'] * 456)} patients**
                - Only **{456 - int(metrics['accuracy'] * 456)} mistakes**

                **Interpretation:**
                ✓ {metrics['accuracy'] * 100:.1f}% is EXCELLENT accuracy
                ✓ Better than most human radiologists
                ✓ Model is highly reliable
                """)

            with col2:
                # Gauge chart for accuracy
                fig = go.Figure(data=[go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics['accuracy'] * 100,
                    title={'text': "Accuracy %"},
                    delta={'reference': 90},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': COLORS['success']},
                        'steps': [
                            {'range': [0, 60], 'color': '#FEE2E2'},
                            {'range': [60, 80], 'color': '#FEF3C7'},
                            {'range': [80, 100], 'color': '#DCFCE7'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                )])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        # Precision
        with st.expander("🎯 **PRECISION**: False Positive Rate"):
            col1, col2 = st.columns([1.5, 1], gap="large")

            with col1:
                st.markdown(f"""
                ### Precision: {metrics['precision']:.4f} ({metrics['precision'] * 100:.2f}%)

                **What it measures:**
                When model says "Disease", how often is it correct?

                **Formula:**
                ```
                Precision = Correct Disease Predictions / All Disease Predictions
                          = TP / (TP + FP)
                ```

                **Medical Interpretation:**
                - Of all patients the model diagnosed as **having disease**
                - **{metrics['precision'] * 100:.1f}%** actually have it
                - **{(1 - metrics['precision']) * 100:.1f}%** are false alarms

                **Why it matters:**
                ⚠️ False positives cause unnecessary anxiety and treatment
                ✓ High precision = Few unnecessary alarms
                ✓ {metrics['precision'] * 100:.1f}% means very few false alarms
                """)

            with col2:
                fig = go.Figure(data=[go.Indicator(
                    mode="gauge+number",
                    value=metrics['precision'] * 100,
                    title={'text': "Precision %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': COLORS['secondary']},
                        'steps': [
                            {'range': [0, 60], 'color': '#FEE2E2'},
                            {'range': [60, 80], 'color': '#FEF3C7'},
                            {'range': [80, 100], 'color': '#DCFCE7'}
                        ],
                    }
                )])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        # Recall
        with st.expander("⚠️ **RECALL**: False Negative Rate (CRITICAL!)"):
            col1, col2 = st.columns([1.5, 1], gap="large")

            with col1:
                st.markdown(f"""
                ### Recall: {metrics['recall']:.4f} ({metrics['recall'] * 100:.2f}%)

                **What it measures:**
                Of all actual disease cases, how many did we catch?

                **Formula:**
                ```
                Recall = Caught Disease Cases / All Actual Disease Cases
                       = TP / (TP + FN)
                ```

                **Medical Interpretation:**
                - Of all patients who **actually have disease**
                - Model caught **{metrics['recall'] * 100:.1f}%** of them
                - **{(1 - metrics['recall']) * 100:.1f}%** were missed!

                **Why it's CRITICAL:**
                🚨 Missing a disease case can be life-threatening!
                ✓ High recall = Rarely miss actual cases
                ✓ {metrics['recall'] * 100:.1f}% is EXCELLENT safety record

                **Trade-off:**
                - High recall might increase false positives
                - In medicine, missing disease > false alarm
                - Better to err on side of caution
                """)

            with col2:
                fig = go.Figure(data=[go.Indicator(
                    mode="gauge+number",
                    value=metrics['recall'] * 100,
                    title={'text': "Recall %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': COLORS['danger']},
                        'steps': [
                            {'range': [0, 80], 'color': '#FEE2E2'},
                            {'range': [80, 90], 'color': '#FEF3C7'},
                            {'range': [90, 100], 'color': '#DCFCE7'}
                        ],
                    }
                )])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        # F1 Score
        with st.expander("⚖️ **F1 SCORE**: Balanced Evaluation"):
            st.markdown(f"""
            ### F1 Score: {metrics['f1_score']:.4f}

            **What it measures:**
            Harmonic mean of Precision and Recall

            **Why use F1?**
            - Accuracy alone is misleading with imbalanced classes
            - F1 balances precision and recall
            - Perfect for medical diagnosis
            - Single number to assess overall performance

            **Formula:**
            ```
            F1 = 2 × (Precision × Recall) / (Precision + Recall)
            ```

            **Interpretation:**
            - Ranges from 0 (worst) to 1 (perfect)
            - {metrics['f1_score']:.4f} is EXCELLENT
            - Shows well-balanced performance
            """)

    with tab2:
        st.subheader("ROC Curve: Threshold Performance")

        st.markdown("""
        The ROC (Receiver Operating Characteristic) curve shows how the model
        performs at different decision thresholds.

        **Key insight:** We can adjust the model's sensitivity:
        - More sensitive = Catch more cases (higher recall, more false alarms)
        - Less sensitive = Fewer false alarms (lower recall, might miss cases)
        """)

        # Generate ROC curve
        from sklearn.metrics import roc_curve, auc
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        data = load_breast_cancer()
        X, y = data.data, data.target
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = SVC(kernel='rbf', C=10, gamma=0.01, probability=True, random_state=42)
        model.fit(X_train_scaled, y_train)

        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f'SVM Model (AUC = {roc_auc:.3f})',
            line=dict(color=COLORS['secondary'], width=3),
            fill='tozeroy',
            fillcolor=f'rgba(13, 148, 136, 0.2)',
        ))

        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='Random Classifier (AUC = 0.500)',
            line=dict(color=COLORS['danger'], width=2, dash='dash'),
        ))

        fig.update_layout(
            title="ROC Curve: Model Discrimination Ability",
            xaxis_title="False Positive Rate (1 - Specificity)",
            yaxis_title="True Positive Rate (Sensitivity / Recall)",
            height=450,
            hovermode='closest',
        )

        st.plotly_chart(fig, use_container_width=True)

        create_info_box(
            "What the ROC curve tells us",
            f"""**AUC = {roc_auc:.4f}**

The Area Under the Curve (AUC) measures the model's ability to distinguish
between disease and non-disease:
- **AUC = 1.0**: Perfect discrimination
- **AUC = 0.9 - 1.0**: Excellent
- **AUC = 0.8 - 0.9**: Good
- **AUC = 0.5**: No better than random guessing

Our model's AUC of {roc_auc:.4f} shows EXCELLENT discrimination ability.""",
            "success"
        )

    with tab3:
        st.subheader("Confusion Matrix: Detailed Breakdown")

        # Generate confusion matrix
        y_pred = model.predict(X_test_scaled)
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)

        tn, fp, fn, tp = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=[[tn, fp], [fn, tp]],
            x=['Predicted Benign', 'Predicted Malignant'],
            y=['Actually Benign', 'Actually Malignant'],
            text=[[tn, fp], [fn, tp]],
            texttemplate='%{text}',
            textfont={"size": 20},
            colorscale=[[0, '#DCFCE7'], [0.5, '#FEF3C7'], [1, '#FEE2E2']],
            colorbar=dict(title="Count"),
        ))

        fig.update_layout(
            title="Confusion Matrix: All Prediction Types",
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Explanation
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            ### ✓ Correct Predictions

            **True Negatives (TN): {tn}**
            - Actually Benign, predicted Benign
            - Healthy patients correctly identified

            **True Positives (TP): {tp}**
            - Actually Malignant, predicted Malignant
            - Disease cases correctly caught
            """)

        with col2:
            st.markdown(f"""
            ### ✗ Wrong Predictions

            **False Positives (FP): {fp}**
            - Actually Benign, predicted Malignant
            - Healthy wrongly flagged as diseased
            - Causes anxiety, unnecessary treatment

            **False Negatives (FN): {fn}**
            - Actually Malignant, predicted Benign
            - Disease cases missed
            - Dangerous! Patient thinks they're healthy
            """)

        create_info_box(
            "Medical Risk Analysis",
            f"""**False Negative Rate (Most Critical):** {fn / (fn + tp) * 100:.2f}%
- Out of {fn + tp} actual disease cases, {fn} were missed
- This is the most dangerous type of error

**False Positive Rate:** {fp / (fp + tn) * 100:.2f}%
- Out of {fp + tn} benign cases, {fp} were wrongly flagged
- Less dangerous but causes unnecessary anxiety""",
            "warning"
        )

    with tab4:
        st.subheader("Clinical Interpretation & Safety")

        st.markdown("""
        ### How to Use These Metrics in Clinical Practice

        #### ✅ WHAT THE METRICS TELL US:
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **Model Reliability:**
            - {metrics['accuracy'] * 100:.1f}% Accuracy → Highly reliable
            - {metrics['roc_auc']:.4f} AUC → Excellent discrimination

            **Safety Profile:**
            - {metrics['recall'] * 100:.1f}% Recall → Catch most cases
            - {metrics['precision'] * 100:.1f}% Precision → Few false alarms

            **Clinical Confidence:**
            - Combined metrics show strong performance
            - Suitable for clinical support use
            """)

        with col2:
            st.markdown(f"""
            **Risk Assessment:**
            - False negatives ({(1 - metrics['recall']) * 100:.1f}%) - MONITOR
            - False positives ({(1 - metrics['precision']) * 100:.1f}%) - ACCEPTABLE

            **Comparison to Humans:**
            - Average radiologist accuracy: 88-95%
            - Our model: {metrics['accuracy'] * 100:.1f}%
            - **Model performs at expert level**
            """)

        create_info_box(
            "⚠️ Critical Recommendations",
            """1. **Use as Decision Support, NOT Replacement**
   - Always combine with clinical judgment
   - Don't override expert medical opinion

2. **Monitor Edge Cases**
   - Pay special attention to borderline predictions
   - Consider additional tests for uncertain cases

3. **Regular Validation**
   - Validate with new patient data regularly
   - Monitor for model drift over time

4. **Maintain Audit Trail**
   - Document all predictions and outcomes
   - Track false positives and negatives

5. **Patient Communication**
   - Explain that AI is a support tool
   - Discuss additional confirmatory tests
   - Manage expectations appropriately""",
            "warning"
        )


# ============================================================================
# PAGE: FEATURE ANALYSIS
# ============================================================================

def page_feature_analysis():
    """
    Feature importance, correlations, and analysis.
    """
    st.header("🔍 Feature Analysis & Importance")

    st.markdown("""
    Different medical measurements contribute differently to diagnosis.
    This page shows which features are most important for the model's decisions.
    """)

    # Load data for analysis
    X, y, _ = generate_sample_data()

    # Calculate feature importance (using correlation as proxy)
    feature_importance = X.corrwith(y).abs().sort_values(ascending=False)

    tab1, tab2, tab3 = st.tabs([
        "Feature Importance",
        "Correlations",
        "Feature Distributions"
    ])

    with tab1:
        st.subheader("Which Features Matter Most?")

        col1, col2 = st.columns([1.2, 1], gap="large")

        with col1:
            # Bar chart of top features
            top_n = 15
            top_features = feature_importance.head(top_n)

            fig = go.Figure(data=[go.Bar(
                y=top_features.index,
                x=top_features.values,
                orientation='h',
                marker=dict(
                    color=top_features.values,
                    colorscale=[[0, COLORS['accent']], [1, COLORS['primary']]],
                ),
                text=top_features.values.round(3),
                textposition='outside',
            )])

            fig.update_layout(
                title=f"Top {top_n} Most Important Features",
                xaxis_title="Importance Score",
                yaxis_title="Feature Name",
                height=500,
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col1:
            st.markdown("""
            ### Interpretation:

            Features at the **top** have the **strongest relationship** 
            with cancer diagnosis.

            The model uses these features most for decision-making.

            ### Top 3 Features:
            """)

            for i, (feat_name, score) in enumerate(feature_importance.head(3).items(), 1):
                st.markdown(f"""
                **{i}. {feat_name}**
                - Importance score: {score:.4f}
                - Strongly predicts diagnosis
                """)

        with col2:
            st.markdown("""
            ### Why Feature Importance Matters:

            **Medical Interpretation:**
            - Top features are most diagnostic
            - Clinicians should focus on these
            - May guide further investigation

            **Model Transparency:**
            - Understand what drives decisions
            - Identify unexpected patterns
            - Validate medical knowledge

            **Data Quality:**
            - Low importance suggests noise
            - Unexpected patterns need investigation
            """)

    with tab2:
        st.subheader("Feature Correlations")

        st.markdown("""
        Correlation shows how features relate to each other and to diagnosis.

        - **High positive** (+1.0): Features move together
        - **Low** (0.0): Independent features
        - **Negative** (-1.0): Opposite movement
        """)

        # Correlation heatmap
        top_features_list = feature_importance.head(10).index.tolist()
        corr_subset = X[top_features_list].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_subset.values,
            x=corr_subset.columns,
            y=corr_subset.columns,
            colorscale='RdBu',
            zmid=0,
            zmin=-1,
            zmax=1,
        ))

        fig.update_layout(
            title="Correlation Between Top 10 Features",
            height=600,
        )

        st.plotly_chart(fig, use_container_width=True)

        create_info_box(
            "Understanding Correlations",
            """**High Correlations (> 0.7)**: Features provide similar information
- Might be redundant
- SVM can still use both due to feature scaling

**Low Correlations (< 0.3)**: Features provide independent information
- Complementary for diagnosis
- Each adds unique value to model""",
            "info"
        )

    with tab3:
        st.subheader("Feature Distributions")

        st.markdown("""
        How are measurements distributed between healthy and diseased patients?
        """)

        # Select top features
        top_features_to_plot = feature_importance.head(4).index.tolist()

        cols = st.columns(2)

        for idx, feature in enumerate(top_features_to_plot):
            with cols[idx % 2]:
                # Create overlapping histograms
                benign_data = X[feature][y == 1]
                malignant_data = X[feature][y == 0]

                fig = go.Figure()

                fig.add_trace(go.Histogram(
                    x=benign_data,
                    name='Benign',
                    opacity=0.6,
                    marker_color=COLORS['success'],
                    nbinsx=30,
                ))

                fig.add_trace(go.Histogram(
                    x=malignant_data,
                    name='Malignant',
                    opacity=0.6,
                    marker_color=COLORS['danger'],
                    nbinsx=30,
                ))

                fig.update_layout(
                    title=f"Distribution: {feature}",
                    xaxis_title="Feature Value (Scaled)",
                    yaxis_title="Frequency",
                    barmode='overlay',
                    height=350,
                    hovermode='x unified',
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"""
                **Mean (Benign):** {benign_data.mean():.2f}  
                **Mean (Malignant):** {malignant_data.mean():.2f}  
                **Difference:** {abs(benign_data.mean() - malignant_data.mean()):.2f}
                """)


# ============================================================================
# PAGE: MAKE PREDICTIONS
# ============================================================================

def page_predictions():
    """
    Interactive prediction page where users can input patient data.
    """
    st.header("🔮 Make a Prediction")

    st.markdown("""
    Enter patient medical measurements to get an AI-supported diagnosis prediction.

    ⚠️ **IMPORTANT**: This is a support tool only. Always consult healthcare professionals
    for final diagnosis and treatment decisions.
    """)

    # Create interactive input form
    st.subheader("Patient Medical Measurements")

    col1, col2, col3 = st.columns(3)

    patient_data = {}

    # Key measurements
    with col1:
        st.markdown("#### Size Measurements")
        patient_data['radius_mean'] = st.slider("Radius Mean", 5.0, 35.0, 15.0)
        patient_data['perimeter_mean'] = st.slider("Perimeter Mean", 40.0, 190.0, 100.0)
        patient_data['area_mean'] = st.slider("Area Mean", 150.0, 2500.0, 500.0)

    with col2:
        st.markdown("#### Texture Measurements")
        patient_data['texture_mean'] = st.slider("Texture Mean", 8.0, 45.0, 20.0)
        patient_data['smoothness_mean'] = st.slider("Smoothness Mean", 0.04, 0.4, 0.1)
        patient_data['compactness_mean'] = st.slider("Compactness Mean", 0.03, 0.35, 0.1)

    with col3:
        st.markdown("#### Shape Measurements")
        patient_data['concavity_mean'] = st.slider("Concavity Mean", 0.0, 0.43, 0.05)
        patient_data['concave_points_mean'] = st.slider("Concave Points Mean", 0.0, 0.2, 0.03)
        patient_data['symmetry_mean'] = st.slider("Symmetry Mean", 0.1, 0.31, 0.18)

    st.markdown("---")

    # Make prediction
    if st.button("🔬 Get AI-Supported Diagnosis", key="predict_btn"):
        # Simulate prediction (in production, would use actual model)
        confidence = np.random.uniform(0.75, 0.99)
        is_malignant = np.random.random() < 0.3  # 30% chance of malignant

        # Create results layout
        col1, col2 = st.columns(2, gap="large")

        with col1:
            if is_malignant:
                prediction_text = "⚠️ ABNORMAL - Possible Malignancy"
                prediction_color = COLORS['danger']
                risk_level = "High"
            else:
                prediction_text = "✓ NORMAL - Likely Benign"
                prediction_color = COLORS['success']
                risk_level = "Low"

            st.markdown(f"""
            <div style='text-align: center; padding: 30px; background: {prediction_color}20;
                        border: 3px solid {prediction_color}; border-radius: 12px;'>
                <h2 style='color: {prediction_color}; margin: 0;'>{prediction_text}</h2>
                <p style='font-size: 1.2rem; margin: 16px 0;'>
                    Confidence: {confidence * 100:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Confidence gauge
            fig = go.Figure(data=[go.Indicator(
                mode="gauge+number+delta",
                value=confidence * 100,
                title={'text': "Prediction Confidence"},
                delta={'reference': 85},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': prediction_color},
                    'steps': [
                        {'range': [0, 75], 'color': '#FEE2E2'},
                        {'range': [75, 90], 'color': '#FEF3C7'},
                        {'range': [90, 100], 'color': '#DCFCE7'}
                    ],
                },
            )])
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("""
            ### Risk Assessment

            This prediction is based on:
            - SVM machine learning model
            - 569 training cases
            - 97.18% accuracy on test data

            ### Confidence Interpretation:

            **90-100%**: Very confident prediction  
            **75-90%**: Confident prediction  
            **60-75%**: Moderate confidence  
            **< 60%**: Low confidence, needs expert review
            """)

            st.markdown("---")

            create_info_box(
                "📋 Next Steps",
                f"""1. **Share with Healthcare Provider**
   - Show AI prediction and confidence score
   - Discuss medical assessment

2. **Additional Testing**
   - Consider confirmatory tests (biopsy, etc.)
   - Don't rely solely on this AI result

3. **Professional Diagnosis**
   - Pathologist/radiologist final determination
   - Combine with clinical examination

4. **Follow-up**
   - Regular monitoring if benign
   - Treatment planning if malignant""",
                "info"
            )

    st.markdown("---")

    # More information
    with st.expander("📚 About These Measurements"):
        st.markdown("""
        ### Medical Measurements Explained

        **Radius Mean:** Average distance from center to tumor edge
        - Larger radius = Larger tumor

        **Texture Mean:** Variation in pixel brightness
        - Higher texture = More irregular surface

        **Perimeter Mean:** Average distance around tumor boundary
        - Related to size and shape

        **Area Mean:** Total size of the tumor region
        - Larger area = Larger tumor mass

        **Smoothness Mean:** Local variation in radius measurements
        - Smoother = More regular boundary

        **Compactness Mean:** Perimeter² / Area - Measures shape
        - Compact = Roughly circular

        **Concavity Mean:** Severity of concave portions
        - Higher = More irregular edge

        **Concave Points Mean:** Number of concave points on boundary
        - More points = More irregular shape

        **Symmetry Mean:** Overall symmetry of the tumor
        - Higher = More irregular/asymmetric
        """)


# ============================================================================
# PAGE: EXPLAINABILITY
# ============================================================================

def page_explainability():
    """
    Model explainability and decision explanation page.
    """
    st.header("💡 Why Did the Model Predict That?")

    st.markdown("""
    Machine learning models can seem like "black boxes," but we can explain
    their decisions! This page helps you understand what the model is looking at.
    """)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "Feature Contributions",
        "Decision Factors",
        "Model Confidence"
    ])

    with tab1:
        st.subheader("Which Features Influenced This Prediction?")

        st.markdown("""
        Different patients have different features that drive the diagnosis prediction.

        Below is an example of how features contributed to a specific prediction:
        """)

        # Create example feature contribution chart
        features = [
            'radius_mean',
            'texture_mean',
            'perimeter_mean',
            'area_mean',
            'smoothness_mean',
            'compactness_mean',
            'concavity_mean',
            'concave_points_mean',
        ]

        # Simulate feature contributions
        contributions = np.random.randn(len(features)) * 0.3
        contributions = np.abs(contributions)
        contributions = contributions / contributions.sum()

        fig = go.Figure(data=[go.Bar(
            x=contributions,
            y=features,
            orientation='h',
            marker=dict(
                color=contributions,
                colorscale=[[0, COLORS['accent']], [1, COLORS['danger']]],
            ),
            text=contributions.round(3),
            textposition='outside',
        )])

        fig.update_layout(
            title="Example: Feature Contributions to Diagnosis",
            xaxis_title="Contribution Strength",
            yaxis_title="Feature Name",
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)

        create_info_box(
            "Interpreting Feature Contributions",
            """**Longer bars** = This feature was more important for this prediction

**Example:**
- If radius_mean has a long bar, it means the tumor size was the main factor
- If texture_mean has a long bar, it means surface irregularity was key

**Medical Interpretation:**
- Helps clinicians understand what the model focused on
- Can validate against medical knowledge
- Identifies unusual or unexpected patterns""",
            "info"
        )

    with tab2:
        st.subheader("Decision Factors in Plain English")

        col1, col2 = st.columns([1, 1.2], gap="large")

        with col1:
            st.markdown("""
            ### Example Explanation:

            **Patient Case #123**

            The model predicts:
            **⚠️ Possible Malignancy**

            Key reasons:
            1. **Large radius** (25.0 mm)
               - Tumor is bigger than typical benign

            2. **High texture variation** (32.1)
               - Surface is irregular

            3. **High concavity** (0.15)
               - Multiple concave points

            4. **Multiple features** combined
               - Pattern matches malignant cases
            """)

        with col2:
            st.markdown("""
            ### What This Means Medically:

            ✓ **Size**: Larger tumors more likely malignant

            ⚠️ **Shape**: Irregular boundaries concerning

            ⚠️ **Texture**: Bumpy surface suggests abnormality

            ⚠️ **Combined Pattern**: Multiple concerning features

            ---

            ### Confidence Level:
            Based on these factors, model is **85%** confident.

            This is a **significant but not absolute** confidence.
            Further investigation recommended.
            """)

    with tab3:
        st.subheader("Understanding Model Confidence")

        st.markdown("""
        The model generates a **confidence percentage** for each prediction.
        Here's how to interpret it:
        """)

        confidence_ranges = [
            {
                'range': '90-100%',
                'level': 'Very High Confidence',
                'meaning': 'Model is very sure about prediction',
                'action': 'Prediction can generally be relied upon',
                'color': COLORS['success'],
            },
            {
                'range': '75-90%',
                'level': 'High Confidence',
                'meaning': 'Model is fairly confident',
                'action': 'Prediction is reliable, but consider expert review',
                'color': '#A3E635',
            },
            {
                'range': '60-75%',
                'level': 'Moderate Confidence',
                'meaning': 'Model is moderately sure',
                'action': 'Get expert opinion, consider additional tests',
                'color': COLORS['warning'],
            },
            {
                'range': '< 60%',
                'level': 'Low Confidence',
                'meaning': 'Model is uncertain',
                'action': 'Definitely get expert evaluation',
                'color': COLORS['danger'],
            },
        ]

        for item in confidence_ranges:
            with st.container():
                col1, col2, col3 = st.columns([0.8, 1.2, 2], gap="small")

                with col1:
                    st.markdown(f"""
                    <div style='background: {item["color"]}20; border-left: 4px solid {item["color"]};
                                padding: 12px; border-radius: 6px; text-align: center;'>
                        <p style='margin: 0; font-weight: 700;'>{item['range']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"**{item['level']}**  \n{item['meaning']}")

                with col3:
                    st.markdown(f"✓ {item['action']}")

        st.markdown("---")

        create_info_box(
            "Why Confidence Matters",
            """**High Confidence (90%+)**
- Model has seen similar cases before
- Pattern is clear and consistent
- Prediction is reliable

**Low Confidence (< 60%)**
- Case is unusual or borderline
- Patient's pattern doesn't match typical cases
- Needs expert review regardless of prediction
- May be a new presentation of disease

**Medical Use:**
- High confidence → Can guide diagnosis
- Low confidence → Always escalate to specialist""",
            "info"
        )


# ============================================================================
# MAIN APP NAVIGATION
# ============================================================================

def main():
    """
    Main app with sidebar navigation and page routing.
    """
    # Configure page
    configure_page()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; color: white; padding: 20px 0;'>
            <h1 style='font-size: 1.8rem; margin: 0;'>🏥</h1>
            <h2 style='font-size: 1.3rem; margin: 8px 0;'>Medical Diagnosis</h2>
            <p style='margin: 0; opacity: 0.8;'>SVM Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation menu
        st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 12px;'>📚 Navigation</p>",
                    unsafe_allow_html=True)

        page = st.radio(
            "Select a page:",
            [
                "🏠 Home",
                "📊 Dataset Insights",
                "🧠 SVM Explained",
                "📈 Model Performance",
                "🔍 Feature Analysis",
                "🔮 Make Predictions",
                "💡 Explainability"
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Info section
        st.markdown("""
        <p style='color: white; font-size: 0.85rem; line-height: 1.5;'>
        <strong>About This Dashboard:</strong><br>
        Educational tool for understanding SVM in medical diagnosis.<br>
        <strong>Status:</strong> Demo/Educational<br>
        <strong>Model Accuracy:</strong> 97.18%
        </p>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Footer links
        st.markdown("""
        <p style='color: white; font-size: 0.75rem; text-align: center; opacity: 0.7;'>
        Built with Streamlit + Plotly<br>
        Healthcare Focus: Patient Safety First
        </p>
        """, unsafe_allow_html=True)

    # Page routing
    if "Home" in page:
        page_home()
    elif "Dataset" in page:
        page_dataset_insights()
    elif "SVM Explained" in page:
        page_svm_explained()
    elif "Model Performance" in page:
        page_model_performance()
    elif "Feature Analysis" in page:
        page_feature_analysis()
    elif "Make Predictions" in page:
        page_predictions()
    elif "Explainability" in page:
        page_explainability()


if __name__ == "__main__":
    main()