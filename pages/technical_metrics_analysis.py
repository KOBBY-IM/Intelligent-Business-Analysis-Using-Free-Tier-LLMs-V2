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
import json
from io import StringIO

st.set_page_config(page_title="Technical Metrics Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Technical Metrics Analysis", required_role="admin"):
    st.stop()

# ---- GCS DATA RETRIEVAL ----
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_technical_metrics_data():
    """Load technical metrics data from GCS with fallback to local files"""
    
    # Try to load from GCS first
    try:
        # Import GCS dependencies
        from google.cloud import storage
        from google.oauth2 import service_account
        
        # Get credentials from Streamlit secrets
        service_account_info = None
        bucket_name = None
        
        # Check for different secret key formats
        if "gcp_service_account" in st.secrets:
            service_account_info = st.secrets["gcp_service_account"]
            bucket_name = st.secrets.get("gcs_bucket_name", "llm-evaluation-data")
        elif "gcs" in st.secrets and "service_account" in st.secrets["gcs"]:
            service_account_info = st.secrets["gcs"]["service_account"]
            bucket_name = st.secrets["gcs"].get("bucket_name", "llm-evaluation-data")
        
        if service_account_info:
            # Handle case where service account is stored as string
            if isinstance(service_account_info, str):
                service_account_info = json.loads(service_account_info)
            
            # Create credentials and client
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            client = storage.Client(credentials=credentials)
            
            # Check if bucket exists
            if not bucket_name:
                bucket_name = "llm-evaluation-data"  # fallback
            
            bucket = client.bucket(bucket_name)
            
            # Check if bucket exists
            if not bucket.exists():
                st.error(f"❌ GCS bucket '{bucket_name}' does not exist or is not accessible")
                raise Exception(f"Bucket {bucket_name} not found")
            
            # Try to download CSV data
            csv_blob = bucket.blob("batch_eval_metrics.csv")
            if csv_blob.exists():
                csv_content = csv_blob.download_as_text()
                technical_df = pd.read_csv(StringIO(csv_content))
                
                # Convert timestamp column if present
                if 'timestamp' in technical_df.columns:
                    technical_df['timestamp'] = pd.to_datetime(technical_df['timestamp'])
                
                st.success(f"📊 Loaded {len(technical_df)} records from GCS (bucket: {bucket_name})")
                st.info(f"🔍 Data last modified: {csv_blob.updated}")
                return technical_df
            else:
                st.warning(f"⚠️ File 'batch_eval_metrics.csv' not found in GCS bucket '{bucket_name}'")
                
                # List available files for debugging
                blobs = list(bucket.list_blobs(prefix="batch_eval"))
                if blobs:
                    blob_names = [blob.name for blob in blobs]
                    st.info(f"🔍 Available files in bucket: {blob_names}")
                else:
                    st.info("🔍 No batch evaluation files found in bucket")
        else:
            st.warning("⚠️ GCS credentials not found in Streamlit secrets")
            st.info("💡 Looking for 'gcp_service_account' or 'gcs.service_account' in secrets")
            
    except ImportError:
        st.warning("⚠️ Google Cloud Storage library not available - using local fallback")
    except Exception as e:
        st.warning(f"⚠️ Could not load from GCS: {str(e)} - using local fallback")
        st.info("💡 **To enable GCS access**: Configure 'gcp_service_account' and 'gcs_bucket_name' in Streamlit secrets")
    
    # Fallback to local file
    try:
        metrics_path = os.path.join("data", "batch_eval_metrics.csv")
        if os.path.exists(metrics_path):
            technical_df = pd.read_csv(metrics_path)
            
            # Convert timestamp column if present
            if 'timestamp' in technical_df.columns:
                technical_df['timestamp'] = pd.to_datetime(technical_df['timestamp'])
            
            st.info(f"📈 Using local batch evaluation data ({len(technical_df)} records)")
            return technical_df
        else:
            st.warning("⚠️ No local batch evaluation data found")
            st.info("💡 **To generate data**: Run the batch evaluator script or create sample data")
            
    except Exception as e:
        st.error(f"❌ Failed to load technical metrics: {e}")
    
    # Return empty DataFrame if all else fails
    return pd.DataFrame()

# ---- ENHANCED VISUALIZATION FUNCTIONS ----

def create_additional_metric_distributions(technical_df):
    """Return up to three Plotly histogram figures for additional numeric columns not already visualized."""
    if technical_df.empty:
        return None, None, None
    # Metrics already visualized
    exclude = {'latency_sec', 'throughput_tps', 'success', 'coverage_score'}
    # Find additional numeric columns
    numeric_cols = [col for col in technical_df.select_dtypes(include='number').columns if col not in exclude]
    figs = []
    for col in numeric_cols[:3]:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=technical_df[col], name=col, marker_color='#1f77b4'))
        fig.update_layout(title=f"Distribution of {col}", xaxis_title=col, yaxis_title="Count", height=350)
        figs.append(fig)
    # Pad with None if fewer than 3
    while len(figs) < 3:
        figs.append(None)
    return tuple(figs)

def create_performance_dashboard(technical_df):
    """Create comprehensive performance dashboard with moving averages"""
    if technical_df.empty:
        return None
    # Compute moving averages (window=10)
    tech_df = technical_df.copy()
    if 'latency_sec' in tech_df.columns:
        tech_df['latency_ma'] = tech_df['latency_sec'].rolling(window=10, min_periods=1).mean()
    if 'throughput_tps' in tech_df.columns:
        tech_df['throughput_ma'] = tech_df['throughput_tps'].rolling(window=10, min_periods=1).mean()
    if 'success' in tech_df.columns:
        tech_df['success_ma'] = tech_df['success'].rolling(window=10, min_periods=1).mean()
    # Create subplots for different metrics
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=['Latency (seconds)', 'Latency (Moving Avg)', 'Throughput (tokens/sec)', 'Throughput (Moving Avg)', 'Success Rate (%)', 'Success Rate (Moving Avg)'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    # Latency and moving average
    if 'latency_sec' in tech_df.columns:
        for model in tech_df['llm_model'].unique():
            model_data = tech_df[tech_df['llm_model'] == model]
            if 'timestamp' in model_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['latency_sec'],
                        mode='lines+markers',
                        name=f"{model} Latency",
                        showlegend=False
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['latency_ma'],
                        mode='lines',
                        name=f"{model} Latency MA",
                        showlegend=True
                    ),
                    row=1, col=2
                )
    # Throughput and moving average
    if 'throughput_tps' in tech_df.columns:
        for model in tech_df['llm_model'].unique():
            model_data = tech_df[tech_df['llm_model'] == model]
            if 'timestamp' in model_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['throughput_tps'],
                        mode='lines+markers',
                        name=f"{model} Throughput",
                        showlegend=False
                    ),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['throughput_ma'],
                        mode='lines',
                        name=f"{model} Throughput MA",
                        showlegend=True
                    ),
                    row=2, col=2
                )
    # Success and moving average
    if 'success' in tech_df.columns:
        for model in tech_df['llm_model'].unique():
            model_data = tech_df[tech_df['llm_model'] == model]
            if 'timestamp' in model_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['success']*100,
                        mode='lines+markers',
                        name=f"{model} Success",
                        showlegend=False
                    ),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=model_data['timestamp'],
                        y=model_data['success_ma']*100,
                        mode='lines',
                        name=f"{model} Success MA",
                        showlegend=True
                    ),
                    row=3, col=2
                )
    fig.update_layout(height=900, title_text="Technical Performance Metrics and Moving Averages Over Time")
    return fig

def create_failure_analysis(technical_df):
    """Create comprehensive failure and error analysis"""
    if technical_df.empty:
        return None
    
    # Calculate failure rates by provider and model
    failure_analysis = technical_df.groupby(['llm_provider', 'llm_model', 'industry']).agg({
        'success': ['count', 'sum', 'mean'],
        'error': lambda x: x.notna().sum(),
        'error_type': lambda x: x.value_counts().to_dict() if x.notna().any() else {},
        'rate_limit_hit': 'sum',
        'retry_count': 'mean'
    }).reset_index()
    
    # Flatten column names
    failure_analysis.columns = ['Provider', 'LLM Model', 'Industry', 'Total Tests', 'Successful Tests', 'Success Rate', 'Error Count', 'Error Types', 'Rate Limit Hits', 'Avg Retries']
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

def create_provider_comparison_analysis(technical_df):
    """Create comprehensive provider-level comparison analysis"""
    if technical_df.empty:
        return None, None, None, None
    
    # Provider-level aggregations
    provider_stats = technical_df.groupby('llm_provider').agg({
        'latency_sec': ['mean', 'std', 'min', 'max'],
        'throughput_tps': ['mean', 'std', 'min', 'max'],
        'success': 'mean',
        'rate_limit_hit': 'sum',
        'error_type': lambda x: x.value_counts().to_dict() if x.notna().any() else {},
        'response_length': ['mean', 'std'],
        'coverage_score': ['mean', 'std'],
        'retry_count': 'mean'
    }).round(3)
    
    # Flatten column names
    provider_stats.columns = ['_'.join(col).strip() for col in provider_stats.columns]
    
    # Calculate additional provider metrics
    provider_metrics = {}
    for provider in technical_df['llm_provider'].unique():
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        
        # Reliability metrics
        total_requests = len(provider_data)
        successful_requests = provider_data['success'].sum()
        reliability_score = (successful_requests / total_requests) * 100
        
        # Consistency metrics (lower std = more consistent)
        latency_consistency = 1 - (provider_data['latency_sec'].std() / provider_data['latency_sec'].mean()) if provider_data['latency_sec'].mean() > 0 else 0
        throughput_consistency = 1 - (provider_data['throughput_tps'].std() / provider_data['throughput_tps'].mean()) if provider_data['throughput_tps'].mean() > 0 else 0
        
        # Error analysis
        error_counts = provider_data['error_type'].value_counts()
        most_common_error = error_counts.index[0] if len(error_counts) > 0 else 'None'
        error_rate = (len(provider_data) - successful_requests) / len(provider_data) * 100
        
        # Rate limit analysis
        rate_limit_incidents = provider_data['rate_limit_hit'].sum()
        rate_limit_rate = (rate_limit_incidents / total_requests) * 100
        
        provider_metrics[provider] = {
            'total_requests': total_requests,
            'reliability_score': reliability_score,
            'latency_consistency': latency_consistency,
            'throughput_consistency': throughput_consistency,
            'error_rate': error_rate,
            'most_common_error': most_common_error,
            'rate_limit_rate': rate_limit_rate,
            'avg_response_length': provider_data['response_length'].mean(),
            'avg_coverage_score': provider_data['coverage_score'].mean()
        }
    
    return provider_stats, provider_metrics

def create_provider_performance_comparison(technical_df):
    """Create provider performance comparison visualizations"""
    if technical_df.empty:
        return None, None, None
    
    # Performance comparison by provider
    fig1 = go.Figure()
    
    providers = technical_df['llm_provider'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, provider in enumerate(providers):
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        
        fig1.add_trace(go.Box(
            y=provider_data['latency_sec'],
            name=f'{provider} - Latency',
            marker_color=colors[i % len(colors)],
            boxpoints='outliers'
        ))
    
    fig1.update_layout(
        title="Provider Latency Comparison",
        yaxis_title="Latency (seconds)",
        showlegend=True,
        height=400
    )
    
    # Throughput comparison
    fig2 = go.Figure()
    
    for i, provider in enumerate(providers):
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        
        fig2.add_trace(go.Box(
            y=provider_data['throughput_tps'],
            name=f'{provider} - Throughput',
            marker_color=colors[i % len(colors)],
            boxpoints='outliers'
        ))
    
    fig2.update_layout(
        title="Provider Throughput Comparison",
        yaxis_title="Throughput (tokens/second)",
        showlegend=True,
        height=400
    )
    
    # Reliability comparison
    fig3 = go.Figure()
    
    reliability_data = []
    for provider in providers:
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        success_rate = provider_data['success'].mean() * 100
        reliability_data.append({
            'provider': provider,
            'success_rate': success_rate,
            'error_rate': 100 - success_rate
        })
    
    reliability_df = pd.DataFrame(reliability_data)
    
    fig3.add_trace(go.Bar(
        x=reliability_df['provider'],
        y=reliability_df['success_rate'],
        name='Success Rate (%)',
        marker_color='green'
    ))
    
    fig3.add_trace(go.Bar(
        x=reliability_df['provider'],
        y=reliability_df['error_rate'],
        name='Error Rate (%)',
        marker_color='red'
    ))
    
    fig3.update_layout(
        title="Provider Reliability Comparison",
        yaxis_title="Rate (%)",
        barmode='stack',
        height=400
    )
    
    return fig1, fig2, fig3

def create_provider_industry_analysis(technical_df):
    """Analyze provider performance across different industries"""
    if technical_df.empty:
        return None, None
    
    # Provider performance by industry
    industry_provider_stats = technical_df.groupby(['llm_provider', 'industry']).agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean',
        'coverage_score': 'mean'
    }).reset_index()
    
    # Create heatmap for provider-industry performance
    fig1 = px.imshow(
        industry_provider_stats.pivot(index='llm_provider', columns='industry', values='latency_sec'),
        title="Provider Latency by Industry (seconds)",
        color_continuous_scale='Reds',
        aspect='auto'
    )
    
    # Create radar chart for provider comparison
    fig2 = go.Figure()
    
    providers = technical_df['llm_provider'].unique()
    metrics = ['latency_sec', 'throughput_tps', 'success', 'coverage_score']
    
    for provider in providers:
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        values = []
        
        for metric in metrics:
            if metric == 'latency_sec':
                # Invert latency (lower is better)
                value = 1 / (provider_data[metric].mean() + 1e-6)
            elif metric == 'throughput_tps':
                # Normalize throughput
                value = provider_data[metric].mean() / technical_df[metric].max()
            else:
                # Direct values for success and coverage
                value = provider_data[metric].mean()
            
            values.append(value)
        
        # Close the radar chart
        values.append(values[0])
        
        fig2.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name=provider
        ))
    
    fig2.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Provider Performance Radar Chart",
        height=500
    )
    
    return fig1, fig2

def create_provider_cost_analysis(technical_df):
    """Create cost analysis for providers (estimated based on token usage)"""
    if technical_df.empty:
        return None, None
    
    # Estimated pricing (per 1K tokens) - these are approximate free-tier rates
    pricing = {
        'groq': {
            'llama3-70b-8192': 0.0008,
            'moonshotai/kimi-k2-instruct': 0.0008
        },
        'openrouter': {
            'mistralai/mistral-7b-instruct': 0.0002,
            'deepseek/deepseek-r1-0528-qwen3-8b': 0.0004
        }
    }
    
    # Calculate estimated costs
    cost_data = []
    for _, row in technical_df.iterrows():
        provider = row['llm_provider']
        model = row['llm_model']
        total_tokens = row['total_tokens']
        
        if provider in pricing and model in pricing[provider]:
            cost_per_1k = pricing[provider][model]
            estimated_cost = (total_tokens / 1000) * cost_per_1k
        else:
            estimated_cost = 0
        
        cost_data.append({
            'provider': provider,
            'model': model,
            'total_tokens': total_tokens,
            'estimated_cost': estimated_cost,
            'latency_sec': row['latency_sec'],
            'success': row['success']
        })
    
    cost_df = pd.DataFrame(cost_data)
    
    # Cost efficiency analysis
    cost_efficiency = cost_df.groupby('provider').agg({
        'estimated_cost': ['sum', 'mean'],
        'total_tokens': 'sum',
        'latency_sec': 'mean',
        'success': 'mean'
    }).round(6)
    
    cost_efficiency.columns = ['total_cost', 'avg_cost_per_request', 'total_tokens', 'avg_latency', 'success_rate']
    
    # Cost vs Performance scatter plot
    fig = px.scatter(
        cost_df.groupby(['provider', 'model']).agg({
            'estimated_cost': 'mean',
            'latency_sec': 'mean',
            'success': 'mean'
        }).reset_index(),
        x='estimated_cost',
        y='latency_sec',
        color='provider',
        size='success',
        hover_data=['model'],
        title="Cost vs Performance Analysis",
        labels={'estimated_cost': 'Estimated Cost per Request ($)', 'latency_sec': 'Average Latency (seconds)'}
    )
    
    return cost_efficiency, fig

def create_provider_trend_analysis(technical_df):
    """Analyze provider performance trends over time"""
    if technical_df.empty or 'timestamp' not in technical_df.columns:
        return None, None
    
    # Convert timestamp to datetime
    tech_df = technical_df.copy()
    tech_df['timestamp'] = pd.to_datetime(tech_df['timestamp'])
    tech_df['date'] = tech_df['timestamp'].dt.date
    
    # Daily performance trends by provider
    daily_stats = tech_df.groupby(['date', 'llm_provider']).agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean',
        'rate_limit_hit': 'sum'
    }).reset_index()
    
    # Latency trends
    fig1 = px.line(
        daily_stats,
        x='date',
        y='latency_sec',
        color='llm_provider',
        title="Provider Latency Trends Over Time",
        labels={'latency_sec': 'Average Latency (seconds)', 'date': 'Date'}
    )
    
    # Success rate trends
    fig2 = px.line(
        daily_stats,
        x='date',
        y='success',
        color='llm_provider',
        title="Provider Success Rate Trends Over Time",
        labels={'success': 'Success Rate', 'date': 'Date'}
    )
    
    return fig1, fig2

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
        # Display comprehensive failure analysis
        st.subheader("📊 Error and Failure Statistics")
        
        # Check if we have any failures
        total_failures = len(filtered_tech[filtered_tech['success'] == False])
        total_requests = len(filtered_tech)
        failure_rate = (total_failures / total_requests) * 100 if total_requests > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Requests", total_requests)
        with col2:
            st.metric("Failed Requests", total_failures)
        with col3:
            st.metric("Failure Rate", f"{failure_rate:.2f}%")
        with col4:
            st.metric("Success Rate", f"{100 - failure_rate:.2f}%")
        
        # Show detailed failure analysis if there are failures
        if total_failures > 0:
            st.subheader("🔍 Detailed Error Analysis")
            
            # Error types breakdown
            error_types = filtered_tech[filtered_tech['success'] == False]['error_type'].value_counts()
            if len(error_types) > 0:
                st.write("**Error Types Distribution:**")
                error_df = pd.DataFrame({
                    'Error Type': error_types.index,
                    'Count': error_types.values,
                    'Percentage': (error_types.values / total_failures) * 100
                })
                st.dataframe(error_df, use_container_width=True)
                
                # Error type visualization
                fig_error_types = px.pie(
                    values=error_types.values,
                    names=error_types.index,
                    title="Error Types Distribution"
                )
                st.plotly_chart(fig_error_types, use_container_width=True)
            
            # Provider-specific error analysis
            st.subheader("🏢 Provider Error Analysis")
            provider_errors = filtered_tech[filtered_tech['success'] == False].groupby('llm_provider').agg({
                'error_type': 'value_counts',
                'error': lambda x: x.iloc[0] if len(x) > 0 else None
            }).reset_index()
            
            if len(provider_errors) > 0:
                st.write("**Errors by Provider:**")
                st.dataframe(provider_errors, use_container_width=True)
            
            # Show sample error messages
            st.subheader("📝 Sample Error Messages")
            sample_errors = filtered_tech[filtered_tech['error'].notna()]['error'].head(5)
            for i, error in enumerate(sample_errors, 1):
                with st.expander(f"Error {i}", expanded=False):
                    st.code(error, language='text')
        else:
            st.success("🎉 No failures detected in the current dataset!")
            st.info("All requests were successful. This indicates good service availability.")
        
        # Create failure analysis visualizations
        fig1, fig2, fig3 = create_failure_visualizations(filtered_tech)
        
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    # ---- PROVIDER COMPARISON ANALYSIS ----
    st.header("🏢 Provider Comparison Analysis")
    
    if not filtered_tech.empty:
        # Generate provider analysis
        provider_stats, provider_metrics = create_provider_comparison_analysis(filtered_tech)
        
        if provider_stats is not None and provider_metrics:
            # Provider summary statistics
            st.subheader("📊 Provider Summary Statistics")
            st.dataframe(provider_stats, use_container_width=True)
            
            # Provider metrics overview
            st.subheader("🎯 Provider Performance Metrics")
            metrics_df = pd.DataFrame(provider_metrics).T
            st.dataframe(metrics_df, use_container_width=True)
            
            # Provider performance comparison charts
            st.subheader("📈 Provider Performance Comparison")
            perf_fig1, perf_fig2, perf_fig3 = create_provider_performance_comparison(filtered_tech)
            
            if perf_fig1:
                st.plotly_chart(perf_fig1, use_container_width=True)
            if perf_fig2:
                st.plotly_chart(perf_fig2, use_container_width=True)
            if perf_fig3:
                st.plotly_chart(perf_fig3, use_container_width=True)
            
            # Provider industry analysis
            st.subheader("🏭 Provider Performance by Industry")
            industry_fig1, industry_fig2 = create_provider_industry_analysis(filtered_tech)
            
            if industry_fig1:
                st.plotly_chart(industry_fig1, use_container_width=True)
            if industry_fig2:
                st.plotly_chart(industry_fig2, use_container_width=True)
            
            # Cost analysis
            st.subheader("💰 Provider Cost Analysis")
            cost_efficiency, cost_fig = create_provider_cost_analysis(filtered_tech)
            
            if cost_efficiency is not None:
                st.write("**Cost Efficiency Analysis:**")
                st.dataframe(cost_efficiency, use_container_width=True)
            
            if cost_fig:
                st.plotly_chart(cost_fig, use_container_width=True)
            
            # Trend analysis
            st.subheader("📈 Provider Performance Trends")
            trend_fig1, trend_fig2 = create_provider_trend_analysis(filtered_tech)
            
            if trend_fig1:
                st.plotly_chart(trend_fig1, use_container_width=True)
            if trend_fig2:
                st.plotly_chart(trend_fig2, use_container_width=True)
    
    # ---- RATE LIMIT ANALYSIS ----
    st.header("⚡ Rate Limit Analysis")
    
    if not filtered_tech.empty:
        rate_limit_fig = create_rate_limit_analysis(filtered_tech)
        if rate_limit_fig:
            st.plotly_chart(rate_limit_fig, use_container_width=True)
    
        # ---- ADDITIONAL METRIC DISTRIBUTIONS ----
        st.header("🧮 Additional Metric Distributions")
        if not filtered_tech.empty:
            add_fig, rate_fig, err_fig = create_additional_metric_distributions(filtered_tech)
            if add_fig:
                st.plotly_chart(add_fig, use_container_width=True)
            if rate_fig:
                st.plotly_chart(rate_fig, use_container_width=True)
            if err_fig:
                st.plotly_chart(err_fig, use_container_width=True)

# ---- AUTO-REFRESH FUNCTIONALITY ----
if filters['auto_refresh']:
    time.sleep(300)  # Wait 5 minutes
    st.rerun() 