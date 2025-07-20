import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.auth import enforce_page_access
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

st.set_page_config(page_title="Technical Metrics Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Technical Metrics Analysis", required_role="admin"):
    st.stop()

# ---- REAL-TIME UPDATE CONFIGURATION ----
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_technical_metrics_data():
    """Load technical metrics data with caching for real-time updates"""
    try:
        metrics_path = os.path.join("data", "batch_eval_metrics.csv")
        if os.path.exists(metrics_path):
            technical_df = pd.read_csv(metrics_path)
            st.info("📈 Using sample batch evaluation data for demonstration")
        else:
            technical_df = pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load technical metrics: {e}")
        technical_df = pd.DataFrame()
    
    return technical_df

# ---- ENHANCED VISUALIZATION FUNCTIONS ----
def create_performance_dashboard(technical_df):
    """Create comprehensive performance dashboard"""
    if technical_df.empty:
        return None
    
    # Create subplots for different metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Latency (seconds)', 'Throughput (tokens/sec)', 'Success Rate (%)', 'Coverage Score'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    metrics = ['latency_sec', 'throughput_tps', 'success', 'coverage_score']
    for i, metric in enumerate(metrics):
        if metric in technical_df.columns:
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            for model in technical_df['llm_model'].unique():
                model_data = technical_df[technical_df['llm_model'] == model]
                if 'timestamp' in model_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=model_data['timestamp'],
                            y=model_data[metric],
                            mode='lines+markers',
                            name=f"{model}",
                            showlegend=(row == 1 and col == 1)
                        ),
                        row=row, col=col
                    )
    
    fig.update_layout(height=700, title_text="Technical Performance Metrics Over Time")
    return fig

def create_failure_analysis(technical_df):
    """Create failure and rate limit analysis"""
    if technical_df.empty:
        return None
    
    # Calculate failure rates
    failure_analysis = technical_df.groupby(['llm_model', 'industry']).agg({
        'success': ['count', 'sum', 'mean'],
        'error_message': lambda x: x.notna().sum()
    }).reset_index()
    
    failure_analysis.columns = ['LLM Model', 'Industry', 'Total Tests', 'Successful Tests', 'Success Rate', 'Error Count']
    failure_analysis['Failure Rate'] = 1 - failure_analysis['Success Rate']
    failure_analysis['Success Rate'] = failure_analysis['Success Rate'] * 100
    failure_analysis['Failure Rate'] = failure_analysis['Failure Rate'] * 100
    
    return failure_analysis

def create_failure_visualizations(technical_df):
    """Create visualizations for failure analysis"""
    if technical_df.empty:
        return None
    
    # 1. Success Rate by LLM
    success_by_llm = technical_df.groupby('llm_model')['success'].agg(['mean', 'count']).reset_index()
    success_by_llm.columns = ['LLM Model', 'Success Rate', 'Total Tests']
    success_by_llm['Success Rate'] = success_by_llm['Success Rate'] * 100
    
    fig1 = px.bar(
        success_by_llm,
        x='LLM Model',
        y='Success Rate',
        title="Success Rate by LLM Model",
        color='Success Rate',
        color_continuous_scale='RdYlGn'
    )
    fig1.update_layout(yaxis_title="Success Rate (%)")
    
    # 2. Error Analysis
    if 'error_message' in technical_df.columns:
        error_counts = technical_df[technical_df['error_message'].notna()]['error_message'].value_counts()
        if not error_counts.empty:
            fig2 = px.pie(
                values=error_counts.values,
                names=error_counts.index,
                title="Error Type Distribution"
            )
        else:
            fig2 = None
    else:
        fig2 = None
    
    # 3. Failure Rate Over Time
    if 'timestamp' in technical_df.columns:
        tech_df = technical_df.copy()
        tech_df['timestamp'] = pd.to_datetime(tech_df['timestamp'])
        tech_df['date'] = tech_df['timestamp'].dt.date
        
        daily_failure = tech_df.groupby(['date', 'llm_model'])['success'].mean().reset_index()
        daily_failure['Failure Rate'] = (1 - daily_failure['success']) * 100
        
        fig3 = px.line(
            daily_failure,
            x='date',
            y='Failure Rate',
            color='llm_model',
            title="Daily Failure Rate by LLM Model"
        )
        fig3.update_layout(yaxis_title="Failure Rate (%)")
    else:
        fig3 = None
    
    return fig1, fig2, fig3

def create_rate_limit_analysis(technical_df):
    """Create rate limit and performance degradation analysis"""
    if technical_df.empty:
        return None
    
    # Analyze performance patterns that might indicate rate limiting
    if 'timestamp' in technical_df.columns:
        tech_df = technical_df.copy()
        tech_df['timestamp'] = pd.to_datetime(tech_df['timestamp'])
        tech_df['hour'] = tech_df['timestamp'].dt.hour
        
        # Group by hour to see if there are patterns
        hourly_performance = tech_df.groupby(['hour', 'llm_model']).agg({
            'latency_sec': 'mean',
            'throughput_tps': 'mean',
            'success': 'mean'
        }).reset_index()
        
        # Create subplots for hourly analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Hourly Latency', 'Hourly Throughput', 'Hourly Success Rate', 'Performance Correlation'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Hourly latency
        for model in hourly_performance['llm_model'].unique():
            model_data = hourly_performance[hourly_performance['llm_model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['hour'], y=model_data['latency_sec'], 
                          mode='lines+markers', name=f"{model} - Latency"),
                row=1, col=1
            )
        
        # Hourly throughput
        for model in hourly_performance['llm_model'].unique():
            model_data = hourly_performance[hourly_performance['llm_model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['hour'], y=model_data['throughput_tps'], 
                          mode='lines+markers', name=f"{model} - Throughput"),
                row=1, col=2
            )
        
        # Hourly success rate
        for model in hourly_performance['llm_model'].unique():
            model_data = hourly_performance[hourly_performance['llm_model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['hour'], y=model_data['success']*100, 
                          mode='lines+markers', name=f"{model} - Success"),
                row=2, col=1
            )
        
        # Performance correlation (latency vs throughput)
        for model in tech_df['llm_model'].unique():
            model_data = tech_df[tech_df['llm_model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['latency_sec'], y=model_data['throughput_tps'], 
                          mode='markers', name=f"{model} - Correlation"),
                row=2, col=2
            )
        
        fig.update_layout(height=700, title_text="Rate Limit and Performance Analysis")
        return fig
    
    return None

def create_heatmap_comparison(technical_df):
    """Create heatmap comparing LLM performance across industries"""
    if technical_df.empty:
        return None
    
    # Aggregate data by LLM and industry
    agg_data = technical_df.groupby(['llm_model', 'industry']).agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean',
        'coverage_score': 'mean'
    }).reset_index()
    
    # Create heatmap for each metric
    metrics = ['latency_sec', 'throughput_tps', 'success', 'coverage_score']
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f'{metric.replace("_", " ").title()}' for metric in metrics],
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}],
               [{"type": "heatmap"}, {"type": "heatmap"}]]
    )
    
    for i, metric in enumerate(metrics):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        # Pivot data for heatmap
        pivot_data = agg_data.pivot(index='llm_model', columns='industry', values=metric)
        
        fig.add_trace(
            go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                text=pivot_data.values.round(3),
                texttemplate="%{text}",
                textfont={"size": 10},
                colorscale='Viridis',
                showscale=True
            ),
            row=row, col=col
        )
    
    fig.update_layout(height=600, title_text="LLM Performance Heatmap by Industry")
    return fig

def create_summary_statistics(technical_df):
    """Create summary statistics table"""
    if technical_df.empty:
        return None
    
    # Calculate summary statistics by LLM and industry
    summary_stats = technical_df.groupby(['llm_model', 'industry']).agg({
        'latency_sec': ['mean', 'std', 'min', 'max'],
        'throughput_tps': ['mean', 'std', 'min', 'max'],
        'success': ['mean', 'std'],
        'coverage_score': ['mean', 'std', 'min', 'max']
    }).round(3)
    
    return summary_stats

# ---- SIDEBAR FILTERS ----
def create_sidebar_filters(technical_df):
    """Create sidebar filters for technical metrics analysis"""
    st.sidebar.title("🎛️ Technical Metrics Filters")
    
    # Real-time update controls
    st.sidebar.subheader("🔄 Real-Time Updates")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=True)
    if st.sidebar.button("🔄 Manual Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    # Technical Metrics Filters
    if not technical_df.empty:
        industries = sorted(technical_df['industry'].unique()) if 'industry' in technical_df.columns else []
        industry_filter = st.sidebar.multiselect("Industry", industries, default=industries, key="tech_industry")
        
        llm_models = sorted(technical_df['llm_model'].unique()) if 'llm_model' in technical_df.columns else []
        llm_filter = st.sidebar.multiselect("LLM Model", llm_models, default=llm_models, key="tech_llm")
        
        if 'timestamp' in technical_df.columns:
            tech_df = technical_df.copy()
            tech_df['timestamp'] = pd.to_datetime(tech_df['timestamp'])
            min_date = tech_df['timestamp'].min().date()
            max_date = tech_df['timestamp'].max().date()
            date_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="tech_date")
        else:
            date_range = []
        
        # Metric-specific filters
        st.sidebar.subheader("📊 Metric Filters")
        min_latency = st.sidebar.number_input("Min Latency (s)", 0.0, 20.0, 0.0, 0.1, key="min_latency")
        max_latency = st.sidebar.number_input("Max Latency (s)", 0.0, 20.0, 20.0, 0.1, key="max_latency")
        min_throughput = st.sidebar.number_input("Min Throughput (tokens/s)", 0.0, 500.0, 0.0, 1.0, key="min_throughput")
        min_coverage = st.sidebar.slider("Min Coverage Score", 0.0, 1.0, 0.0, 0.01, key="min_coverage")
    else:
        industry_filter = []
        llm_filter = []
        date_range = []
        min_latency = 0.0
        max_latency = 20.0
        min_throughput = 0.0
        min_coverage = 0.0
    
    return {
        'auto_refresh': auto_refresh,
        'industry': industry_filter,
        'llm_model': llm_filter,
        'date_range': date_range,
        'min_latency': min_latency,
        'max_latency': max_latency,
        'min_throughput': min_throughput,
        'min_coverage': min_coverage
    }

# ---- MAIN TECHNICAL METRICS ANALYSIS PAGE ----
st.title("⚡ Technical Metrics Analysis Dashboard")

# Load data
technical_df = load_technical_metrics_data()

# Create sidebar filters
filters = create_sidebar_filters(technical_df)

# Display data freshness
last_update = datetime.now()
st.info(f"📅 Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# ---- DATA OVERVIEW ----
st.header("📊 Data Overview")

if technical_df.empty:
    st.warning("⚠️ No technical metrics data available. Please run batch evaluations first.")
else:
    # Apply filters
    filtered_tech = technical_df.copy()
    
    if filters['industry'] and 'industry' in filtered_tech.columns:
        filtered_tech = filtered_tech[filtered_tech['industry'].isin(filters['industry'])]
    if filters['llm_model'] and 'llm_model' in filtered_tech.columns:
        filtered_tech = filtered_tech[filtered_tech['llm_model'].isin(filters['llm_model'])]
    
    # Apply metric filters
    if 'latency_sec' in filtered_tech.columns:
        filtered_tech = filtered_tech[
            (filtered_tech['latency_sec'] >= filters['min_latency']) &
            (filtered_tech['latency_sec'] <= filters['max_latency'])
        ]
    if 'throughput_tps' in filtered_tech.columns:
        filtered_tech = filtered_tech[filtered_tech['throughput_tps'] >= filters['min_throughput']]
    if 'coverage_score' in filtered_tech.columns:
        filtered_tech = filtered_tech[filtered_tech['coverage_score'] >= filters['min_coverage']]
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Measurements", len(filtered_tech))
    with col2:
        st.metric("LLM Models", filtered_tech['llm_model'].nunique() if 'llm_model' in filtered_tech.columns else 0)
    with col3:
        st.metric("Industries", filtered_tech['industry'].nunique() if 'industry' in filtered_tech.columns else 0)
    with col4:
        avg_latency = filtered_tech['latency_sec'].mean() if 'latency_sec' in filtered_tech.columns else 0
        st.metric("Avg Latency (s)", f"{avg_latency:.2f}")

    # ---- PERFORMANCE DASHBOARD ----
    st.header("📈 Performance Dashboard")
    
    if not filtered_tech.empty:
        # Performance metrics over time
        performance_fig = create_performance_dashboard(filtered_tech)
        if performance_fig:
            st.plotly_chart(performance_fig, use_container_width=True)
        
        # Summary statistics table
        st.write("**Detailed Summary Statistics:**")
        summary_stats = create_summary_statistics(filtered_tech)
        if summary_stats is not None:
            st.dataframe(summary_stats, use_container_width=True)
    
    # ---- HEATMAP COMPARISON ----
    st.header("🔥 Performance Heatmap")
    
    if not filtered_tech.empty:
        heatmap_fig = create_heatmap_comparison(filtered_tech)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # ---- METRIC DISTRIBUTIONS ----
    st.header("📊 Metric Distributions")
    
    if not filtered_tech.empty:
        metrics = ['latency_sec', 'throughput_tps', 'success', 'coverage_score']
        available_metrics = [m for m in metrics if m in filtered_tech.columns]
        
        if available_metrics:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[f'{metric.replace("_", " ").title()}' for metric in available_metrics],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            for i, metric in enumerate(available_metrics):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                # Histogram for each metric
                fig.add_trace(
                    go.Histogram(x=filtered_tech[metric], name=metric, showlegend=False),
                    row=row, col=col
                )
            
            fig.update_layout(height=600, title_text="Metric Distributions")
            st.plotly_chart(fig, use_container_width=True)
    
    # ---- RELIABILITY ANALYSIS ----
    st.header("🛡️ Reliability Analysis")
    
    if not filtered_tech.empty and 'success' in filtered_tech.columns:
        # Success rate by LLM and industry
        success_analysis = filtered_tech.groupby(['llm_model', 'industry'])['success'].agg(['mean', 'count']).reset_index()
        success_analysis.columns = ['LLM Model', 'Industry', 'Success Rate', 'Total Tests']
        success_analysis['Success Rate'] = success_analysis['Success Rate'] * 100
        
        st.write("**Success Rate Analysis:**")
        st.dataframe(success_analysis, use_container_width=True)
        
        # Success rate visualization
        fig = px.bar(
            success_analysis,
            x='LLM Model',
            y='Success Rate',
            color='Industry',
            title="Success Rate by LLM Model and Industry",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- FAILURE ANALYSIS ----
    st.header("💥 Failure Analysis")
    
    if not filtered_tech.empty:
        # Create failure analysis visualizations
        fig1, fig2, fig3 = create_failure_visualizations(filtered_tech)
        
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    # ---- RATE LIMIT ANALYSIS ----
    st.header("⚡ Rate Limit Analysis")
    
    if not filtered_tech.empty:
        rate_limit_fig = create_rate_limit_analysis(filtered_tech)
        if rate_limit_fig:
            st.plotly_chart(rate_limit_fig, use_container_width=True)

# ---- AUTO-REFRESH FUNCTIONALITY ----
if filters['auto_refresh']:
    time.sleep(300)  # Wait 5 minutes
    st.rerun() 