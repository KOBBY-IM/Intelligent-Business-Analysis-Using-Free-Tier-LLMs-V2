import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.auth import enforce_page_access
from utils.data_store import DataStore
import os
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import time
import json

st.set_page_config(page_title="Blind Evaluation Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Blind Evaluation Analysis", required_role="admin"):
    st.stop()

# ---- GCS DATA RETRIEVAL ----
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_blind_evaluation_data():
    """Load blind evaluation data from GCS with fallback to local files"""
    
    # Try to load from GCS using DataStore
    try:
        # Check if GCS credentials are available in secrets
        if "gcp_service_account" in st.secrets:
            ds = DataStore("gcs")
            if ds.storage_type == "gcs":
                human_evals = ds.load_evaluation_data()
                if human_evals:
                    human_df = pd.DataFrame(human_evals)
                    
                    # Convert timestamp columns if present
                    for col in ['timestamp', 'evaluation_timestamp']:
                        if col in human_df.columns:
                            human_df[col] = pd.to_datetime(human_df[col])
                    
                    st.success(f"📊 Loaded {len(human_df)} blind evaluation records from GCS")
                    return human_df
                else:
                    st.warning("⚠️ No blind evaluation data found in GCS yet")
            else:
                st.warning("⚠️ DataStore could not initialize with GCS - using local fallback")
        else:
            st.info("ℹ️ GCS credentials not found - using local fallback")
            
    except Exception as e:
        st.warning(f"⚠️ Could not load from GCS: {str(e)} - using local fallback")
    
    # Fallback to local DataStore
    try:
        ds = DataStore("local")
        human_evals = ds.load_evaluation_data()
        if human_evals:
            human_df = pd.DataFrame(human_evals)
            
            # Convert timestamp columns if present
            for col in ['timestamp', 'evaluation_timestamp']:
                if col in human_df.columns:
                    human_df[col] = pd.to_datetime(human_df[col])
            
            st.info(f"📊 Using local blind evaluation data ({len(human_df)} records)")
            return human_df
    except Exception as e:
        st.warning(f"⚠️ Could not load from local DataStore: {str(e)}")
    
    # Final fallback to sample data
    try:
        sample_path = os.path.join("data", "sample_evaluations.json")
        if os.path.exists(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            human_df = pd.DataFrame(sample_data)
            
            # Convert timestamp columns if present
            for col in ['timestamp', 'evaluation_timestamp']:
                if col in human_df.columns:
                    human_df[col] = pd.to_datetime(human_df[col])
            
            st.info(f"📈 Using sample blind evaluation data ({len(human_df)} records)")
            return human_df
    except Exception as e:
        st.error(f"❌ Failed to load sample data: {e}")
    
    # Return empty DataFrame if all else fails
    st.warning("⚠️ No blind evaluation data available")
    return pd.DataFrame()

# ---- STATISTICAL ANALYSIS FUNCTIONS ----
def calculate_confidence_intervals(data, confidence=0.95):
    """Calculate confidence intervals for ratings"""
    if len(data) < 2:
        return None, None
    
    mean = np.mean(data)
    std_err = stats.sem(data)
    ci = stats.t.interval(confidence, len(data)-1, loc=mean, scale=std_err)
    return ci[0], ci[1]

def perform_statistical_tests(human_df, group_cols, rating_cols):
    """Perform statistical significance tests"""
    results = {}
    
    for rating_col in rating_cols:
        if rating_col not in human_df.columns:
            continue
            
        # ANOVA test for multiple groups
        if len(group_cols) > 0:
            groups = human_df.groupby(group_cols[0])[rating_col].apply(list)
            if len(groups) > 1:
                try:
                    f_stat, p_value = stats.f_oneway(*groups.values)
                    results[f"{rating_col}_anova"] = {
                        "f_statistic": f_stat,
                        "p_value": p_value,
                        "significant": p_value < 0.05
                    }
                except:
                    pass
    
    return results

def calculate_effect_size(group1, group2):
    """Calculate Cohen's d effect size"""
    if len(group1) == 0 or len(group2) == 0:
        return 0
    
    pooled_std = np.sqrt(((len(group1) - 1) * np.var(group1, ddof=1) + 
                         (len(group2) - 1) * np.var(group2, ddof=1)) / 
                        (len(group1) + len(group2) - 2))
    
    if pooled_std == 0:
        return 0
    
    return (np.mean(group1) - np.mean(group2)) / pooled_std

# ---- ENHANCED VISUALIZATION FUNCTIONS ----
def create_radar_chart(data, llm_models, rating_cols):
    """Create radar chart for multi-dimensional comparison"""
    if data.empty or not rating_cols:
        return None
    
    fig = go.Figure()
    
    for model in llm_models:
        model_data = data[data['llm_model'] == model]
        if model_data.empty:
            continue
            
        values = [model_data[col].mean() for col in rating_cols if col in model_data.columns]
        if len(values) == len(rating_cols):
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=rating_cols,
                fill='toself',
                name=model
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title="Multi-dimensional LLM Performance Comparison"
    )
    
    return fig

def create_qualitative_feedback_table(data):
    """Create a table of qualitative feedback comments"""
    if 'comments' not in data.columns:
        return None
    
    feedback_data = data[['llm_model', 'current_industry', 'comments']].copy()
    feedback_data = feedback_data.dropna(subset=['comments'])
    
    if feedback_data.empty:
        return None
    
    return feedback_data

# ---- SIDEBAR FILTERS ----
def create_sidebar_filters(human_df):
    """Create sidebar filters for blind evaluation analysis"""
    st.sidebar.title("🎛️ Blind Evaluation Filters")
    
    # Real-time update controls
    st.sidebar.subheader("🔄 Real-Time Updates")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=True)
    if st.sidebar.button("🔄 Manual Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    # Blind Evaluation Filters
    if not human_df.empty:
        industries = sorted(human_df['current_industry'].unique()) if 'current_industry' in human_df.columns else []
        industry_filter = st.sidebar.multiselect("Industry", industries, default=industries, key="blind_industry")
        
        llm_models = sorted(human_df['llm_model'].unique()) if 'llm_model' in human_df.columns else []
        llm_filter = st.sidebar.multiselect("LLM Model", llm_models, default=llm_models, key="blind_llm")
        
        min_ratings = st.sidebar.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.1, key="blind_ratings")
    else:
        industry_filter = []
        llm_filter = []
        min_ratings = 1.0
    
    return {
        'auto_refresh': auto_refresh,
        'industry': industry_filter,
        'llm_model': llm_filter,
        'min_ratings': min_ratings
    }

# ---- MAIN BLIND EVALUATION ANALYSIS PAGE ----
st.title("👥 Blind Evaluation Analysis Dashboard")

# Load data
human_df = load_blind_evaluation_data()

# Create sidebar filters
filters = create_sidebar_filters(human_df)

# Display data freshness
last_update = datetime.now()
st.info(f"📅 Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# ---- DATA OVERVIEW ----
st.header("📊 Data Overview")

if human_df.empty:
    st.warning("⚠️ No blind evaluation data available. Please complete some evaluations first.")
else:
    # Apply filters
    filtered_human = human_df.copy()
    
    if filters['industry'] and 'current_industry' in filtered_human.columns:
        filtered_human = filtered_human[filtered_human['current_industry'].isin(filters['industry'])]
    if filters['llm_model'] and 'llm_model' in filtered_human.columns:
        filtered_human = filtered_human[filtered_human['llm_model'].isin(filters['llm_model'])]
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Evaluations", len(filtered_human))
    with col2:
        st.metric("LLM Models", filtered_human['llm_model'].nunique() if 'llm_model' in filtered_human.columns else 0)
    with col3:
        st.metric("Industries", filtered_human['current_industry'].nunique() if 'current_industry' in filtered_human.columns else 0)
    with col4:
        avg_quality = filtered_human['quality'].mean() if 'quality' in filtered_human.columns else 0
        st.metric("Avg Quality Rating", f"{avg_quality:.2f}")

    # ---- STATISTICAL SUMMARY ----
    st.header("📈 Statistical Summary")
    
    if not filtered_human.empty:
        rating_cols = ['quality', 'relevance', 'accuracy', 'uniformity']
        available_ratings = [col for col in rating_cols if col in filtered_human.columns]
        
        if available_ratings:
            # Calculate statistics
            stats_summary = filtered_human[available_ratings].describe()
            
            # Add confidence intervals
            ci_data = []
            for col in available_ratings:
                ci_lower, ci_upper = calculate_confidence_intervals(filtered_human[col].dropna())
                if ci_lower is not None:
                    ci_data.append({
                        'Metric': col,
                        'Mean': filtered_human[col].mean(),
                        'Std': filtered_human[col].std(),
                        'CI_Lower': ci_lower,
                        'CI_Upper': ci_upper,
                        'Count': len(filtered_human[col].dropna())
                    })
            
            ci_df = pd.DataFrame(ci_data)
            
            # Display statistics
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Descriptive Statistics:**")
                st.dataframe(stats_summary, use_container_width=True)
            
            with col2:
                st.write("**Confidence Intervals (95%):**")
                st.dataframe(ci_df, use_container_width=True)
    
    # ---- ADVANCED VISUALIZATIONS ----
    st.header("📊 Advanced Visualizations")
    
    if not filtered_human.empty:
        # 1. Radar Chart
        if 'llm_model' in filtered_human.columns and available_ratings:
            radar_fig = create_radar_chart(filtered_human, filters['llm_model'], available_ratings)
            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True)
        
        # 2. Enhanced Boxplots with Confidence Intervals
        if available_ratings:
            st.write("**Rating Distributions with Confidence Intervals:**")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=available_ratings,
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            for i, rating_col in enumerate(available_ratings):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                # Box plot
                fig.add_trace(
                    go.Box(y=filtered_human[rating_col], name=rating_col, showlegend=False),
                    row=row, col=col
                )
                
                # Confidence interval
                ci_lower, ci_upper = calculate_confidence_intervals(filtered_human[rating_col].dropna())
                if ci_lower is not None:
                    fig.add_hline(y=ci_lower, line_dash="dash", line_color="red", 
                                annotation_text=f"95% CI Lower: {ci_lower:.2f}",
                                row=row, col=col)
                    fig.add_hline(y=ci_upper, line_dash="dash", line_color="red",
                                annotation_text=f"95% CI Upper: {ci_upper:.2f}",
                                row=row, col=col)
            
            fig.update_layout(height=600, title_text="Rating Distributions with Confidence Intervals")
            st.plotly_chart(fig, use_container_width=True)
        
        # 3. Statistical Significance Testing
        st.write("**Statistical Significance Tests:**")
        if 'llm_model' in filtered_human.columns and available_ratings:
            test_results = perform_statistical_tests(filtered_human, ['llm_model'], available_ratings)
            
            if test_results:
                test_df = pd.DataFrame([
                    {
                        'Test': key.replace('_anova', ' ANOVA'),
                        'F-Statistic': result['f_statistic'],
                        'P-Value': result['p_value'],
                        'Significant': 'Yes' if result['significant'] else 'No'
                    }
                    for key, result in test_results.items()
                ])
                st.dataframe(test_df, use_container_width=True)
        
        # 4. LLM Performance Comparison
        if 'llm_model' in filtered_human.columns and available_ratings:
            st.write("**LLM Performance Comparison:**")
            
            # Calculate performance scores
            performance_data = []
            for model in filtered_human['llm_model'].unique():
                model_data = filtered_human[filtered_human['llm_model'] == model]
                scores = {}
                for rating_col in available_ratings:
                    scores[rating_col] = model_data[rating_col].mean()
                scores['llm_model'] = model
                performance_data.append(scores)
            
            perf_df = pd.DataFrame(performance_data)
            
            # Create performance comparison chart
            fig = go.Figure()
            for rating_col in available_ratings:
                fig.add_trace(go.Bar(
                    name=rating_col,
                    x=perf_df['llm_model'],
                    y=perf_df[rating_col],
                    text=perf_df[rating_col].round(2),
                    textposition='auto',
                ))
            
            fig.update_layout(
                title="LLM Performance Comparison by Rating Category",
                xaxis_title="LLM Model",
                yaxis_title="Average Rating",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 5. Qualitative Feedback Table
        st.write("**Qualitative Feedback Comments:**")
        feedback_table = create_qualitative_feedback_table(filtered_human)
        if feedback_table is not None:
            st.dataframe(feedback_table, use_container_width=True, height=400)
        else:
            st.info("No qualitative feedback comments available.")

# ---- AUTO-REFRESH FUNCTIONALITY ----
if filters['auto_refresh']:
    time.sleep(300)  # Wait 5 minutes
    st.rerun() 