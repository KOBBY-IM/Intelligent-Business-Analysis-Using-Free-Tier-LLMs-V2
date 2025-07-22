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
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Blind Evaluation Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Blind Evaluation Analysis", required_role="admin"):
    st.stop()

# ---- DATA PROCESSING FUNCTIONS ----
def get_actual_model_name(response_id: str, model_mapping: dict = None) -> str:
    """
    Get actual model name from response ID with fallback mapping.
    
    Args:
        response_id: Anonymous response ID (A, B, C, D)
        model_mapping: Dictionary mapping response_id to actual model name
    
    Returns:
        Actual model name or fallback name
    """
    # First try to use provided mapping
    if model_mapping and response_id in model_mapping:
        return model_mapping[response_id]
    
    # Fallback mapping for when model_mapping is not available
    # NOTE: This is a best-guess fallback since responses are shuffled randomly
    # The actual mapping can vary between evaluation sessions
    fallback_mapping = {
        "A": "llama3-70b-8192",
        "B": "moonshotai/kimi-k2-instruct", 
        "C": "mistralai/mistral-7b-instruct",
        "D": "deepseek/deepseek-r1-0528-qwen3-8b"
    }
    
    return fallback_mapping.get(response_id, f"Model {response_id}")

def detect_model_from_responses(responses_data: list) -> dict:
    """
    Try to detect actual model mapping from response data structure.
    
    Args:
        responses_data: List of response objects from evaluation session
    
    Returns:
        Dictionary mapping anonymous_id to actual model name
    """
    model_mapping = {}
    
    if not responses_data or not isinstance(responses_data, list):
        return model_mapping
    
    for response in responses_data:
        if isinstance(response, dict):
            anonymous_id = response.get("anonymous_id")
            llm_model = response.get("llm_model")
            
            if anonymous_id and llm_model:
                model_mapping[anonymous_id] = llm_model
    
    return model_mapping

def flatten_ratings_data(df):
    """
    Flatten nested ratings data structure for analysis.
    
    Converts nested ratings format:
    {'ratings': {'A': {'quality': 4, 'relevance': 5}, 'B': {...}}}
    
    To flat format with one row per response:
    quality: 4, relevance: 5, response_id: 'A', llm_model: 'Model A'
    """
    if df.empty:
        return df
    
    flattened_rows = []
    empty_ratings_count = 0
    total_records = len(df)
    
    for _, row in df.iterrows():
        try:
            base_data = row.to_dict()
            
            # Handle new bulk saving format with individual_question_ratings
            if 'individual_question_ratings' in base_data:
                individual_ratings = base_data.get('individual_question_ratings', {})
                if isinstance(individual_ratings, dict):
                    for question_key, question_data in individual_ratings.items():
                        if isinstance(question_data, dict) and 'ratings' in question_data:
                            # Create a row for each question's ratings
                            question_base = base_data.copy()
                            question_base['question_key'] = question_key
                            question_base['question'] = question_data.get('question', '')
                            question_base['current_industry'] = question_data.get('industry', '')
                            
                            ratings = question_data.get('ratings', {})
                            model_mapping = question_data.get('model_mapping', {})  # Get the model mapping
                            
                            # Try to extract model mapping from the evaluation session if not found
                            if not model_mapping and 'evaluation_session' in base_data:
                                session_data = base_data.get('evaluation_session', {})
                                selected_responses = session_data.get('selected_responses', [])
                                model_mapping = detect_model_from_responses(selected_responses)
                            
                            if ratings and isinstance(ratings, dict):
                                has_valid_ratings = False
                                for response_id, rating_data in ratings.items():
                                    if isinstance(rating_data, dict) and len(rating_data) > 0:
                                        new_row = question_base.copy()
                                        new_row['response_id'] = response_id
                                        new_row['quality'] = rating_data.get('quality', None)
                                        new_row['relevance'] = rating_data.get('relevance', None) 
                                        new_row['accuracy'] = rating_data.get('accuracy', None)
                                        new_row['uniformity'] = rating_data.get('uniformity', None)
                                        
                                        # Use actual model name from mapping if available
                                        if model_mapping and response_id in model_mapping:
                                            new_row['llm_model'] = model_mapping[response_id]
                                        else:
                                            new_row['llm_model'] = get_actual_model_name(response_id, model_mapping) # Use fallback
                                            
                                        flattened_rows.append(new_row)
                                        has_valid_ratings = True
                                
                                if not has_valid_ratings:
                                    empty_ratings_count += 1
                continue  # Skip old format processing for this row
            
            # Handle old format with direct ratings field
            ratings = base_data.pop('ratings', {})
            
            # Handle different types of ratings data
            if ratings and isinstance(ratings, dict) and len(ratings) > 0:
                # Valid ratings found
                has_valid_ratings = False
                for response_id, rating_data in ratings.items():
                    if isinstance(rating_data, dict) and len(rating_data) > 0:
                        new_row = base_data.copy()
                        new_row['response_id'] = response_id
                        new_row['quality'] = rating_data.get('quality', None)
                        new_row['relevance'] = rating_data.get('relevance', None) 
                        new_row['accuracy'] = rating_data.get('accuracy', None)
                        new_row['uniformity'] = rating_data.get('uniformity', None)
                        # Use response_id as model identifier since this is blind evaluation
                        new_row['llm_model'] = get_actual_model_name(response_id)  # Use fallback mapping
                        flattened_rows.append(new_row)
                        has_valid_ratings = True
                
                if not has_valid_ratings:
                    empty_ratings_count += 1
            else:
                # Empty or invalid ratings
                empty_ratings_count += 1
                # Still create a record for tracking purposes
                base_data['response_id'] = 'no_ratings'
                base_data['quality'] = None
                base_data['relevance'] = None
                base_data['accuracy'] = None
                base_data['uniformity'] = None
                base_data['llm_model'] = 'No Ratings'
                flattened_rows.append(base_data)
                
        except Exception as e:
            # Handle any unexpected data format issues
            st.warning(f"Warning: Error processing row {len(flattened_rows)}: {str(e)}")
            continue
    
    # Create flattened DataFrame
    result_df = pd.DataFrame(flattened_rows)
    
    # Add data quality info to session state for display
    if 'data_quality_info' not in st.session_state:
        st.session_state['data_quality_info'] = {}
    
    st.session_state['data_quality_info'].update({
        'total_records': total_records,
        'empty_ratings_count': empty_ratings_count,
        'valid_ratings_count': total_records - empty_ratings_count,
        'flattened_rows': len(result_df)
    })
    
    return result_df

def flatten_blind_evaluation_json(json_data):
    rows = []
    for eval in json_data:
        tester_email = eval.get("tester_email", "")
        tester_name = eval.get("tester_name", "")
        timestamp = eval.get("evaluation_timestamp", "")
        for qkey, qdata in eval.get("individual_question_ratings", {}).items():
            question = qdata.get("question", "")
            industry = qdata.get("industry", "")
            model_mapping = qdata.get("model_mapping", {})
            for resp_id, rating in qdata.get("ratings", {}).items():
                row = {
                    "tester_email": tester_email,
                    "tester_name": tester_name,
                    "evaluation_timestamp": timestamp,
                    "question_key": qkey,
                    "question": question,
                    "industry": industry,
                    "response_id": resp_id,
                    "llm_model": rating.get("response_id", model_mapping.get(resp_id, "")),
                    "relevance": rating.get("relevance", ""),
                    "clarity": rating.get("clarity", ""),
                    "actionability": rating.get("actionability", "")
                }
                rows.append(row)
    return pd.DataFrame(rows)

# Replace load_blind_evaluation_data to use JSON flattening if CSV is empty or missing
@st.cache_data(ttl=300)
def load_blind_evaluation_data():
    ds = DataStore("gcs")
    human_evals = ds.load_evaluation_data()
    if human_evals:
        return flatten_blind_evaluation_json(human_evals)
    else:
        st.warning("⚠️ No blind evaluation data found in GCS yet")
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
    st.sidebar.title("🎛️ Blind Evaluation Filters")
    # Real-time update controls
    st.sidebar.subheader("🔄 Real-Time Updates")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=True)
    if st.sidebar.button("🔄 Manual Refresh"):
        st.cache_data.clear()
        st.rerun()

    # Blind Evaluation Filters
    if not human_df.empty:
        # Robust industry extraction
        if 'current_industry' in human_df.columns:
            try:
                industries = sorted([
                    x for x in human_df['current_industry'].dropna().unique()
                    if isinstance(x, str) and x.strip()
                ])
            except Exception:
                industries = []
        else:
            industries = []
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

# Defensive: ensure human_df is always a DataFrame
if not isinstance(human_df, pd.DataFrame):
    human_df = pd.DataFrame()

# Create sidebar filters
filters = create_sidebar_filters(human_df)

# Display data freshness
last_update = datetime.now()
st.info(f"📅 Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# ---- DATA OVERVIEW ----
st.header("📊 Data Overview")

# Display data quality information
if 'data_quality_info' in st.session_state:
    info = st.session_state['data_quality_info']
    
    if info['empty_ratings_count'] > 0:
        st.warning(f"""
        ⚠️ **Data Quality Notice**: {info['empty_ratings_count']} out of {info['total_records']} evaluation records contain empty ratings.
        
        This typically happens when:
        - Data was collected before the rating system fixes were applied
        - There were technical issues during evaluation submission
        
        **Action needed**: New evaluations will contain complete rating data for full analysis.
        """)
    
    # Show data breakdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Records", info['total_records'])
    with col2:
        st.metric("✅ Complete Ratings", info['valid_ratings_count'])
    with col3:
        st.metric("❌ Empty Ratings", info['empty_ratings_count'])

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
        
        # Check if we have any actual rating data
        complete_ratings = filtered_human[filtered_human['quality'].notna()] if 'quality' in filtered_human.columns else pd.DataFrame()
        
        if available_ratings and not complete_ratings.empty:
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
    
        elif available_ratings and complete_ratings.empty:
            st.info("""
            📊 **Rating Analysis Not Available**
            
            The evaluation records in the database do not contain individual response ratings. This can happen when:
            
            - Evaluations were submitted before the rating collection system was fully implemented
            - There were technical issues during data submission
            
            **What you can still see:**
            - Overall evaluation summary from final assessments
            - Tester participation statistics
            - Question completion tracking
            
            **For complete analysis**: New evaluations will include detailed ratings for each LLM response (A, B, C, D).
            """)
        else:
            st.info("ℹ️ Rating analysis requires evaluation data with individual response ratings.")

    # ---- ADVANCED VISUALIZATIONS ----
    st.header("📊 Advanced Visualizations")
    
    if not filtered_human.empty:
        # Check if we have complete rating data for visualizations
        complete_ratings = filtered_human[filtered_human['quality'].notna()] if 'quality' in filtered_human.columns else pd.DataFrame()
        
        if not complete_ratings.empty and 'llm_model' in complete_ratings.columns:
            # 1. Radar Chart
            if available_ratings:
                radar_fig = create_radar_chart(complete_ratings, filters['llm_model'], available_ratings)
                if radar_fig:
                    st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.warning("⚠️ No complete rating data available for advanced visualizations. This could happen if:")
            st.write("- No evaluations have been completed yet")
            st.write("- All ratings are empty/null")
            st.write("- Data structure doesn't match expected format")
            st.stop()  # Exit early if no complete data
        
        if not complete_ratings.empty:
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
                        go.Box(y=complete_ratings[rating_col], name=rating_col, showlegend=False),
                        row=row, col=col
                    )
                    
                    # Confidence interval
                    ci_lower, ci_upper = calculate_confidence_intervals(complete_ratings[rating_col].dropna())
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
            if 'llm_model' in complete_ratings.columns and available_ratings:
                st.write("**LLM Performance Comparison:**")
                
                # Calculate performance scores
                performance_data = []
                for model in complete_ratings['llm_model'].unique():
                    model_data = complete_ratings[complete_ratings['llm_model'] == model]
                    scores = {}
                    for rating_col in available_ratings:
                        scores[rating_col] = model_data[rating_col].mean()
                    scores['llm_model'] = model
                    performance_data.append(scores)
                
                perf_df = pd.DataFrame(performance_data)
                
                # Create performance comparison chart only if we have data
                if not perf_df.empty and 'llm_model' in perf_df.columns:
                    fig = go.Figure()
                    for rating_col in available_ratings:
                        if rating_col in perf_df.columns:
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
                        barmode='group',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display performance summary table
                    st.write("**Performance Summary:**")
                    st.dataframe(perf_df.round(2), use_container_width=True)
                else:
                    st.warning("⚠️ No performance data available for comparison.")
        else:
            # Show alternative visualizations when we don't have complete rating data
            st.info("""
            🔄 **Limited Visualization Available**
            
            Detailed rating visualizations require complete evaluation data. Currently showing basic statistics only.
            
            **Available Information:**
            - Evaluation completion timeline
            - Question coverage by industry
            - Overall participation metrics
            
            **For full analysis**: Complete evaluations with individual response ratings will unlock:
            - LLM performance comparisons
            - Statistical significance testing  
            - Multi-dimensional radar charts
            - Rating distribution analysis
            """)
            
            # Show basic timeline of evaluations
            if 'evaluation_timestamp' in filtered_human.columns:
                st.subheader("📅 Evaluation Timeline")
                
                # Convert timestamps and plot
                filtered_human['evaluation_timestamp'] = pd.to_datetime(filtered_human['evaluation_timestamp'])
                timeline_data = filtered_human.groupby(filtered_human['evaluation_timestamp'].dt.date).size().reset_index()
                timeline_data.columns = ['Date', 'Evaluations']
                
                fig = px.line(timeline_data, x='Date', y='Evaluations', 
                             title="Daily Evaluation Submissions",
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # Show question coverage
            if 'question_key' in filtered_human.columns:
                st.subheader("📊 Question Coverage")
                
                question_counts = filtered_human['question_key'].value_counts().head(10)
                fig = px.bar(x=question_counts.index, y=question_counts.values,
                           title="Most Evaluated Questions",
                           labels={'x': 'Question', 'y': 'Number of Evaluations'})
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        # 5. Qualitative Feedback Table
        st.write("**Qualitative Feedback Comments:**")
        feedback_table = create_qualitative_feedback_table(filtered_human)
        if feedback_table is not None:
            st.dataframe(feedback_table, use_container_width=True, height=400)
        else:
            st.info("No qualitative feedback comments available.")

        if feedback_table is not None and not feedback_table['comments'].empty:
            st.write('**Word Cloud of Feedback Comments:**')
            text = ' '.join(feedback_table['comments'].dropna().astype(str))
            if text.strip():
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info('No feedback comments available for word cloud.')

# ---- AUTO-REFRESH FUNCTIONALITY ----
if filters['auto_refresh']:
    time.sleep(300)  # Wait 5 minutes
    st.rerun() 