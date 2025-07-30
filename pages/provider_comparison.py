"""
Provider Comparison Page

This page provides comprehensive analysis and comparison of LLM providers
(Groq vs OpenRouter) for service selection decisions.
"""

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

st.set_page_config(page_title="Provider Comparison Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Provider Comparison Analysis", required_role="admin"):
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
            
            st.success(f"📊 Loaded {len(technical_df)} records from local file")
            return technical_df
        else:
            st.error("❌ No technical metrics data found locally")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading local data: {str(e)}")
        return pd.DataFrame()

def create_provider_scorecard(technical_df):
    """Create a comprehensive provider scorecard for service selection"""
    if technical_df.empty:
        return None
    
    # Calculate provider-level metrics
    provider_analysis = {}
    
    for provider in technical_df['llm_provider'].unique():
        provider_data = technical_df[technical_df['llm_provider'] == provider]
        
        # Performance metrics
        avg_latency = provider_data['latency_sec'].mean()
        avg_throughput = provider_data['throughput_tps'].mean()
        success_rate = provider_data['success'].mean() * 100
        
        # Reliability metrics
        total_requests = len(provider_data)
        error_rate = (total_requests - provider_data['success'].sum()) / total_requests * 100
        rate_limit_incidents = provider_data['rate_limit_hit'].sum()
        rate_limit_rate = (rate_limit_incidents / total_requests) * 100
        
        # Consistency metrics
        latency_std = provider_data['latency_sec'].std()
        latency_consistency = 1 - (latency_std / avg_latency) if avg_latency > 0 else 0
        
        # Quality metrics
        avg_coverage = provider_data['coverage_score'].mean()
        avg_response_length = provider_data['response_length'].mean()
        
        # Cost estimation (approximate)
        total_tokens = provider_data['total_tokens'].sum()
        if provider == 'groq':
            estimated_cost = (total_tokens / 1000) * 0.0008  # Approximate Groq pricing
        else:  # openrouter
            estimated_cost = (total_tokens / 1000) * 0.0003  # Approximate OpenRouter pricing
        
        # Calculate scores (0-100 scale)
        latency_score = max(0, 100 - (avg_latency * 10))  # Lower latency = higher score
        throughput_score = min(100, avg_throughput / 2)  # Higher throughput = higher score
        reliability_score = success_rate
        consistency_score = latency_consistency * 100
        cost_efficiency_score = max(0, 100 - (estimated_cost * 1000))  # Lower cost = higher score
        
        # Overall score (weighted average)
        overall_score = (
            latency_score * 0.25 +
            throughput_score * 0.20 +
            reliability_score * 0.25 +
            consistency_score * 0.15 +
            cost_efficiency_score * 0.15
        )
        
        provider_analysis[provider] = {
            'avg_latency': avg_latency,
            'avg_throughput': avg_throughput,
            'success_rate': success_rate,
            'error_rate': error_rate,
            'rate_limit_rate': rate_limit_rate,
            'latency_consistency': latency_consistency,
            'avg_coverage': avg_coverage,
            'avg_response_length': avg_response_length,
            'total_requests': total_requests,
            'estimated_cost': estimated_cost,
            'latency_score': latency_score,
            'throughput_score': throughput_score,
            'reliability_score': reliability_score,
            'consistency_score': consistency_score,
            'cost_efficiency_score': cost_efficiency_score,
            'overall_score': overall_score
        }
    
    return provider_analysis

def create_provider_recommendation(provider_analysis):
    """Generate provider recommendations based on analysis"""
    if not provider_analysis:
        return None
    
    recommendations = []
    
    # Find best provider for each metric
    metrics = ['latency_score', 'throughput_score', 'reliability_score', 'consistency_score', 'cost_efficiency_score']
    metric_names = ['Latency', 'Throughput', 'Reliability', 'Consistency', 'Cost Efficiency']
    
    for metric, metric_name in zip(metrics, metric_names):
        best_provider = max(provider_analysis.keys(), key=lambda p: provider_analysis[p][metric])
        best_score = provider_analysis[best_provider][metric]
        recommendations.append({
            'metric': metric_name,
            'best_provider': best_provider,
            'score': best_score,
            'recommendation': f"{best_provider.title()} performs best for {metric_name.lower()}"
        })
    
    # Overall recommendation
    best_overall = max(provider_analysis.keys(), key=lambda p: provider_analysis[p]['overall_score'])
    overall_score = provider_analysis[best_overall]['overall_score']
    
    return recommendations, best_overall, overall_score

def create_provider_competitiveness_analysis(technical_df):
    """Analyze provider competitiveness across different scenarios"""
    if technical_df.empty:
        return None
    
    # Define scenarios
    scenarios = {
        'high_performance': {'latency_weight': 0.4, 'throughput_weight': 0.3, 'reliability_weight': 0.2, 'cost_weight': 0.1},
        'cost_optimized': {'latency_weight': 0.2, 'throughput_weight': 0.2, 'reliability_weight': 0.3, 'cost_weight': 0.3},
        'balanced': {'latency_weight': 0.25, 'throughput_weight': 0.25, 'reliability_weight': 0.25, 'cost_weight': 0.25},
        'reliability_focused': {'latency_weight': 0.2, 'throughput_weight': 0.2, 'reliability_weight': 0.4, 'cost_weight': 0.2}
    }
    
    scenario_scores = {}
    
    for scenario_name, weights in scenarios.items():
        scenario_scores[scenario_name] = {}
        
        for provider in technical_df['llm_provider'].unique():
            provider_data = technical_df[technical_df['llm_provider'] == provider]
            
            # Calculate normalized scores
            avg_latency = provider_data['latency_sec'].mean()
            avg_throughput = provider_data['throughput_tps'].mean()
            success_rate = provider_data['success'].mean()
            
            # Cost estimation
            total_tokens = provider_data['total_tokens'].sum()
            if provider == 'groq':
                estimated_cost = (total_tokens / 1000) * 0.0008
            else:
                estimated_cost = (total_tokens / 1000) * 0.0003
            
            # Normalize scores (0-1 scale)
            latency_score = max(0, 1 - (avg_latency / 10))  # Lower latency = higher score
            throughput_score = min(1, avg_throughput / 200)  # Higher throughput = higher score
            reliability_score = success_rate
            cost_score = max(0, 1 - (estimated_cost * 100))  # Lower cost = higher score
            
            # Calculate weighted score
            weighted_score = (
                latency_score * weights['latency_weight'] +
                throughput_score * weights['throughput_weight'] +
                reliability_score * weights['reliability_weight'] +
                cost_score * weights['cost_weight']
            )
            
            scenario_scores[scenario_name][provider] = weighted_score
    
    return scenario_scores

# ---- MAIN PAGE CONTENT ----
st.title("🏢 Provider Comparison Analysis")
st.markdown("Comprehensive analysis and comparison of LLM providers for service selection decisions")

# Load data
technical_df = load_technical_metrics_data()

if technical_df.empty:
    st.warning("⚠️ No technical metrics data available. Please run batch evaluations first.")
    st.stop()

# Filter data by provider
providers = sorted(technical_df['llm_provider'].unique())
selected_providers = st.sidebar.multiselect(
    "Select Providers to Compare",
    providers,
    default=providers,
    key="provider_comparison"
)

if not selected_providers:
    st.warning("⚠️ Please select at least one provider to analyze.")
    st.stop()

# Filter data
filtered_df = technical_df[technical_df['llm_provider'].isin(selected_providers)]

# ---- PROVIDER SCORECARD ----
st.header("📊 Provider Scorecard")

provider_analysis = create_provider_scorecard(filtered_df)

if provider_analysis:
    # Create scorecard display
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Performance Metrics")
        for provider, metrics in provider_analysis.items():
            with st.expander(f"{provider.upper()} Performance", expanded=True):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Overall Score", f"{metrics['overall_score']:.1f}/100")
                    st.metric("Latency", f"{metrics['avg_latency']:.3f}s")
                    st.metric("Throughput", f"{metrics['avg_throughput']:.1f} tokens/s")
                    st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
                
                with col_b:
                    st.metric("Error Rate", f"{metrics['error_rate']:.1f}%")
                    st.metric("Rate Limit Rate", f"{metrics['rate_limit_rate']:.1f}%")
                    st.metric("Consistency", f"{metrics['latency_consistency']:.1f}")
                    st.metric("Est. Cost", f"${metrics['estimated_cost']:.4f}")
    
    with col2:
        st.subheader("🏆 Component Scores")
        score_data = []
        for provider, metrics in provider_analysis.items():
            score_data.append({
                'Provider': provider.upper(),
                'Latency': metrics['latency_score'],
                'Throughput': metrics['throughput_score'],
                'Reliability': metrics['reliability_score'],
                'Consistency': metrics['consistency_score'],
                'Cost Efficiency': metrics['cost_efficiency_score']
            })
        
        score_df = pd.DataFrame(score_data)
        score_df.set_index('Provider', inplace=True)
        
        # Create radar chart
        fig = go.Figure()
        
        for _, row in score_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=row.values,
                theta=row.index,
                fill='toself',
                name=row.name
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Provider Performance Radar Chart",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---- PROVIDER RECOMMENDATIONS ----
st.header("💡 Provider Recommendations")

recommendations, best_overall, overall_score = create_provider_recommendation(provider_analysis)

if recommendations:
    # Display recommendations
    st.subheader("🎯 Best Provider by Metric")
    
    for rec in recommendations:
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.write(f"**{rec['metric']}:**")
        with col2:
            st.write(f"**{rec['best_provider'].upper()}**")
        with col3:
            st.write(f"Score: {rec['score']:.1f}/100")
    
    st.markdown("---")
    
    # Overall recommendation
    st.subheader("🏆 Overall Recommendation")
    st.success(f"**{best_overall.upper()}** is recommended as the best overall provider with a score of **{overall_score:.1f}/100**")
    
    # Detailed reasoning
    st.write("**Reasoning:**")
    best_metrics = provider_analysis[best_overall]
    
    reasoning_points = []
    if best_metrics['latency_score'] > 80:
        reasoning_points.append("Excellent latency performance")
    if best_metrics['reliability_score'] > 95:
        reasoning_points.append("High reliability and success rate")
    if best_metrics['cost_efficiency_score'] > 80:
        reasoning_points.append("Cost-effective pricing")
    if best_metrics['consistency_score'] > 80:
        reasoning_points.append("Consistent performance")
    
    for point in reasoning_points:
        st.write(f"• {point}")

# ---- COMPETITIVENESS ANALYSIS ----
st.header("⚔️ Competitiveness Analysis")

scenario_scores = create_provider_competitiveness_analysis(filtered_df)

if scenario_scores:
    st.subheader("📈 Provider Performance by Use Case")
    
    # Create scenario comparison chart
    scenario_data = []
    for scenario, scores in scenario_scores.items():
        for provider, score in scores.items():
            scenario_data.append({
                'Scenario': scenario.replace('_', ' ').title(),
                'Provider': provider.upper(),
                'Score': score
            })
    
    scenario_df = pd.DataFrame(scenario_data)
    
    fig = px.bar(
        scenario_df,
        x='Scenario',
        y='Score',
        color='Provider',
        title="Provider Competitiveness by Use Case",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scenario-specific recommendations
    st.subheader("🎯 Recommendations by Use Case")
    
    for scenario, scores in scenario_scores.items():
        best_provider = max(scores.keys(), key=lambda p: scores[p])
        best_score = scores[best_provider]
        
        scenario_name = scenario.replace('_', ' ').title()
        
        with st.expander(f"{scenario_name} Use Case", expanded=False):
            st.write(f"**Best Provider:** {best_provider.upper()} (Score: {best_score:.3f})")
            
            # Use case descriptions
            descriptions = {
                'high_performance': "Prioritizes speed and throughput over cost considerations",
                'cost_optimized': "Focuses on minimizing costs while maintaining acceptable performance",
                'balanced': "Equal weighting of all factors for general-purpose use",
                'reliability_focused': "Emphasizes reliability and consistency for critical applications"
            }
            
            st.write(f"**Description:** {descriptions.get(scenario, 'Custom scenario')}")

# ---- DETAILED COMPARISON CHARTS ----
st.header("📊 Detailed Performance Comparison")

# Performance comparison charts
col1, col2 = st.columns(2)

with col1:
    # Latency comparison
    fig_latency = px.box(
        filtered_df,
        x='llm_provider',
        y='latency_sec',
        title="Latency Distribution by Provider",
        labels={'latency_sec': 'Latency (seconds)', 'llm_provider': 'Provider'}
    )
    st.plotly_chart(fig_latency, use_container_width=True)

with col2:
    # Throughput comparison
    fig_throughput = px.box(
        filtered_df,
        x='llm_provider',
        y='throughput_tps',
        title="Throughput Distribution by Provider",
        labels={'throughput_tps': 'Throughput (tokens/second)', 'llm_provider': 'Provider'}
    )
    st.plotly_chart(fig_throughput, use_container_width=True)

# Success rate comparison
fig_success = px.bar(
    filtered_df.groupby('llm_provider')['success'].mean().reset_index(),
    x='llm_provider',
    y='success',
    title="Success Rate by Provider",
    labels={'success': 'Success Rate', 'llm_provider': 'Provider'}
)
st.plotly_chart(fig_success, use_container_width=True)

# ---- INDUSTRY-SPECIFIC ANALYSIS ----
st.header("🏭 Industry-Specific Performance")

if 'industry' in filtered_df.columns:
    # Provider performance by industry
    industry_stats = filtered_df.groupby(['llm_provider', 'industry']).agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean',
        'coverage_score': 'mean'
    }).reset_index()
    
    # Create industry comparison heatmap
    fig_industry = px.imshow(
        industry_stats.pivot(index='llm_provider', columns='industry', values='latency_sec'),
        title="Provider Latency by Industry (seconds)",
        color_continuous_scale='Reds',
        aspect='auto'
    )
    st.plotly_chart(fig_industry, use_container_width=True)
    
    # Industry-specific recommendations
    st.subheader("🎯 Industry-Specific Recommendations")
    
    for industry in filtered_df['industry'].unique():
        industry_data = industry_stats[industry_stats['industry'] == industry]
        best_latency = industry_data.loc[industry_data['latency_sec'].idxmin(), 'llm_provider']
        best_throughput = industry_data.loc[industry_data['throughput_tps'].idxmax(), 'llm_provider']
        best_success = industry_data.loc[industry_data['success'].idxmax(), 'llm_provider']
        
        with st.expander(f"{industry.title()} Industry", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Best Latency:** {best_latency.upper()}")
            with col2:
                st.write(f"**Best Throughput:** {best_throughput.upper()}")
            with col3:
                st.write(f"**Best Reliability:** {best_success.upper()}")

# ---- ERROR ANALYSIS ----
st.header("🚨 Error Analysis")

# Check if we have any failures
total_failures = len(filtered_df[filtered_df['success'] == False])
total_requests = len(filtered_df)
failure_rate = (total_failures / total_requests) * 100 if total_requests > 0 else 0

if total_failures > 0:
    st.subheader("📊 Error Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requests", total_requests)
    with col2:
        st.metric("Failed Requests", total_failures)
    with col3:
        st.metric("Failure Rate", f"{failure_rate:.2f}%")
    with col4:
        st.metric("Success Rate", f"{100 - failure_rate:.2f}%")
    
    # Provider-specific error analysis
    st.subheader("🏢 Provider Error Comparison")
    
    provider_error_data = []
    for provider in selected_providers:
        provider_data = filtered_df[filtered_df['llm_provider'] == provider]
        provider_failures = len(provider_data[provider_data['success'] == False])
        provider_total = len(provider_data)
        provider_failure_rate = (provider_failures / provider_total) * 100 if provider_total > 0 else 0
        
        # Error types for this provider
        error_types = provider_data[provider_data['success'] == False]['error_type'].value_counts()
        most_common_error = error_types.index[0] if len(error_types) > 0 else 'None'
        
        provider_error_data.append({
            'Provider': provider.upper(),
            'Total Requests': provider_total,
            'Failed Requests': provider_failures,
            'Failure Rate (%)': provider_failure_rate,
            'Success Rate (%)': 100 - provider_failure_rate,
            'Most Common Error': most_common_error,
            'Rate Limit Hits': provider_data['rate_limit_hit'].sum(),
            'Avg Retries': provider_data['retry_count'].mean()
        })
    
    error_df = pd.DataFrame(provider_error_data)
    st.dataframe(error_df, use_container_width=True)
    
    # Error type distribution by provider
    st.subheader("📈 Error Type Distribution")
    
    error_type_data = []
    for provider in selected_providers:
        provider_data = filtered_df[filtered_df['llm_provider'] == provider]
        failed_data = provider_data[provider_data['success'] == False]
        
        if len(failed_data) > 0:
            error_counts = failed_data['error_type'].value_counts()
            for error_type, count in error_counts.items():
                error_type_data.append({
                    'Provider': provider.upper(),
                    'Error Type': error_type,
                    'Count': count,
                    'Percentage': (count / len(failed_data)) * 100
                })
    
    if error_type_data:
        error_type_df = pd.DataFrame(error_type_data)
        
        # Create error type comparison chart
        fig_error_types = px.bar(
            error_type_df,
            x='Provider',
            y='Count',
            color='Error Type',
            title="Error Types by Provider",
            barmode='stack'
        )
        st.plotly_chart(fig_error_types, use_container_width=True)
        
        # Show detailed error type table
        st.write("**Detailed Error Type Analysis:**")
        st.dataframe(error_type_df, use_container_width=True)
    
    # Sample error messages
    st.subheader("📝 Recent Error Messages")
    recent_errors = filtered_df[filtered_df['error'].notna()].tail(10)
    
    for _, row in recent_errors.iterrows():
        # Convert timestamp to string and format it properly
        timestamp_str = str(row['timestamp'])[:19] if pd.notna(row['timestamp']) else "Unknown"
        with st.expander(f"{row['llm_provider'].upper()} - {row['llm_model']} - {timestamp_str}", expanded=False):
            st.write(f"**Error Type:** {row['error_type']}")
            st.write(f"**Retry Count:** {row['retry_count']}")
            st.write(f"**Rate Limit Hit:** {row['rate_limit_hit']}")
            st.code(row['error'], language='text')
else:
    st.success("🎉 No failures detected in the current dataset!")
    st.info("All requests were successful. This indicates excellent service availability across all providers.")

# ---- COST ANALYSIS ----
st.header("💰 Cost Analysis")

# Calculate and display cost metrics
cost_data = []
for provider in selected_providers:
    provider_data = filtered_df[filtered_df['llm_provider'] == provider]
    total_tokens = provider_data['total_tokens'].sum()
    
    if provider == 'groq':
        estimated_cost = (total_tokens / 1000) * 0.0008
    else:  # openrouter
        estimated_cost = (total_tokens / 1000) * 0.0003
    
    cost_data.append({
        'Provider': provider.upper(),
        'Total Tokens': total_tokens,
        'Estimated Cost': estimated_cost,
        'Cost per 1K Tokens': estimated_cost / (total_tokens / 1000) if total_tokens > 0 else 0
    })

cost_df = pd.DataFrame(cost_data)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Cost Summary")
    st.dataframe(cost_df, use_container_width=True)

with col2:
    st.subheader("💰 Cost Comparison")
    fig_cost = px.bar(
        cost_df,
        x='Provider',
        y='Estimated Cost',
        title="Estimated Total Cost by Provider",
        labels={'Estimated Cost': 'Cost ($)', 'Provider': 'Provider'}
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# ---- CONCLUSION ----
st.header("📋 Summary and Next Steps")

st.write("""
### Key Findings:
1. **Performance**: Compare latency and throughput metrics above
2. **Reliability**: Check success rates and error patterns
3. **Cost**: Review cost analysis for budget considerations
4. **Use Case Fit**: Consider scenario-specific recommendations

### Recommended Next Steps:
1. **Pilot Testing**: Test the recommended provider with your specific use cases
2. **Load Testing**: Conduct concurrent request testing for production readiness
3. **Cost Monitoring**: Set up cost tracking for ongoing optimization
4. **Performance Monitoring**: Implement continuous performance monitoring
""")

# Auto-refresh functionality
if st.sidebar.checkbox("🔄 Auto-refresh (5 min)", value=False):
    time.sleep(300)
    st.rerun() 