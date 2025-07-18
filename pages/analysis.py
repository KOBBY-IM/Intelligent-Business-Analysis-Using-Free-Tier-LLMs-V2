import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.auth import enforce_page_access
from utils.data_store import DataStore
import os
import altair as alt
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="LLM Evaluation Analysis", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Analysis Dashboard", required_role="admin"):
    st.stop()

st.title("📊 LLM Evaluation Analysis Dashboard")

# ---- DATA LOADING HELPERS ----
def load_human_evaluation_data():
    # Use DataStore to load from GCS or local fallback
    ds = DataStore("gcs" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "local")
    try:
        evals = ds.load_evaluation_data()
        return pd.DataFrame(evals) if evals else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load human evaluation data: {e}")
        return pd.DataFrame()

def load_technical_metrics_data():
    # Try to load from GCS or local fallback
    metrics_path = os.path.join("data", "batch_eval_metrics.csv")
    if not os.path.exists(metrics_path):
        st.warning("Technical metrics file not found locally. Please upload or sync from cloud.")
        return pd.DataFrame()
    try:
        return pd.read_csv(metrics_path)
    except Exception as e:
        st.error(f"Failed to load technical metrics: {e}")
        return pd.DataFrame()

# ---- LOAD DATA ----
human_df = load_human_evaluation_data()
technical_df = load_technical_metrics_data()

filtered_human = pd.DataFrame()
filtered_tech = pd.DataFrame()

# ---- FILTERS ----
st.sidebar.header("Filters")
# Robustly get available columns for filters
human_industry_col = "current_industry" if "current_industry" in human_df.columns else None
tech_industry_col = "industry" if "industry" in technical_df.columns else None
human_llm_col = "llm_model" if "llm_model" in human_df.columns else None
tech_llm_col = "llm_model" if "llm_model" in technical_df.columns else None

industries = sorted(
    ({i for i in set(human_df[human_industry_col]) if i is not None} if human_industry_col else set()) |
    ({i for i in set(technical_df[tech_industry_col]) if i is not None} if tech_industry_col else set())
) if not human_df.empty or not technical_df.empty else []

llms = sorted(
    ({l for l in set(human_df[human_llm_col]) if l is not None} if human_llm_col else set()) |
    ({l for l in set(technical_df[tech_llm_col]) if l is not None} if tech_llm_col else set())
) if not human_df.empty or not technical_df.empty else []

industry_filter = st.sidebar.multiselect("Industry", industries, default=industries)
llm_filter = st.sidebar.multiselect("LLM Model", llms, default=llms)
date_range = st.sidebar.date_input("Date Range", [])

def apply_filters(df, industry_col, llm_col, date_col=None):
    if df.empty:
        return df
    if industry_col and industry_col in df.columns and industry_filter:
        df = df[df[industry_col].isin(industry_filter)]
    if llm_col and llm_col in df.columns and llm_filter:
        df = df[df[llm_col].isin(llm_filter)]
    if date_col and date_col in df.columns and date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        # If the column is timezone-aware, localize start/end to UTC
        if pd.api.types.is_datetime64tz_dtype(df[date_col]):
            start = start.tz_localize('UTC') if start.tzinfo is None else start.tz_convert('UTC')
            end = end.tz_localize('UTC') if end.tzinfo is None else end.tz_convert('UTC')
        df = df[(df[date_col] >= start) & (df[date_col] <= end)]
    return df

# ---- HUMAN EVALUATION ANALYSIS ----
st.header("Human Evaluation Feedback")
if human_df.empty:
    st.info("No human evaluation data available.")
else:
    filtered_human = apply_filters(human_df, human_industry_col, human_llm_col, "evaluation_timestamp")
    # Aggregate ratings
    all_rating_cols = ["quality", "relevance", "accuracy", "uniformity"]
    present_rating_cols = [col for col in all_rating_cols if col in filtered_human.columns]
    group_cols = []
    if human_industry_col and human_industry_col in filtered_human.columns:
        group_cols.append(human_industry_col)
    if human_llm_col and human_llm_col in filtered_human.columns:
        group_cols.append(human_llm_col)
    if group_cols and present_rating_cols:
        agg = filtered_human.groupby(group_cols)[present_rating_cols].mean().reset_index()
        st.subheader("Average Ratings per LLM and Industry")
        st.dataframe(agg, use_container_width=True)
        if all(col in agg.columns for col in group_cols) and not agg.empty:
            try:
                for col in group_cols:
                    agg[col] = agg[col].astype(str)
                numeric_cols = [col for col in present_rating_cols if col in agg.columns and pd.api.types.is_numeric_dtype(agg[col])]
                if numeric_cols:
                    st.bar_chart(agg[numeric_cols])
                else:
                    st.info("No numeric columns to plot for human evaluation.")
            except Exception as e:
                st.info(f"Could not display bar chart for human evaluation: {e}")
        else:
            st.info("Not enough data to display bar chart for human evaluation.")
    else:
        st.info("Not enough columns to group and aggregate human evaluation data.")
    # Show qualitative comments
    if "comments" in filtered_human.columns:
        st.subheader("Qualitative Comments")
        comments = filtered_human[["current_industry", "llm_model", "comments"]].dropna()
        for _, row in comments.iterrows():
            st.markdown(f"**{row['current_industry']} | {row['llm_model']}:** {row['comments']}")

# ---- TECHNICAL METRICS ANALYSIS ----
st.header("Automated Technical Performance Metrics")
if technical_df.empty:
    st.info("No technical metrics data available.")
else:
    filtered_tech = apply_filters(technical_df, tech_industry_col, tech_llm_col, "timestamp")
    # Aggregate metrics
    metric_cols = ["latency_sec", "throughput_tps", "success", "coverage_score"]
    tech_group_cols = []
    if tech_industry_col and tech_industry_col in filtered_tech.columns:
        tech_group_cols.append(tech_industry_col)
    if tech_llm_col and tech_llm_col in filtered_tech.columns:
        tech_group_cols.append(tech_llm_col)
    if tech_group_cols:
        agg_tech = filtered_tech.groupby(tech_group_cols)[metric_cols].mean(numeric_only=True).reset_index()
        st.subheader("Average Technical Metrics per LLM and Industry")
        st.dataframe(agg_tech, use_container_width=True)
        if all(col in agg_tech.columns for col in tech_group_cols) and not agg_tech.empty:
            try:
                for col in tech_group_cols:
                    agg_tech[col] = agg_tech[col].astype(str)
                numeric_cols = [col for col in metric_cols if col in agg_tech.columns and pd.api.types.is_numeric_dtype(agg_tech[col])]
                if numeric_cols:
                    st.bar_chart(agg_tech[numeric_cols])
                else:
                    st.info("No numeric columns to plot for technical metrics.")
            except Exception as e:
                st.info(f"Could not display bar chart for technical metrics: {e}")
        else:
            st.info("Not enough data to display bar chart for technical metrics.")
    else:
        st.info("Not enough columns to group and aggregate technical metrics data.")
    # Show time series for latency and throughput
    st.subheader("Latency and Throughput Over Time")
    if not filtered_tech.empty:
        st.line_chart(filtered_tech.set_index("timestamp")[["latency_sec", "throughput_tps"]])

# ---- ADVANCED VISUALIZATIONS ----
st.header("Advanced Visualizations")

# 1. Time Series Line Chart for Latency
if not filtered_tech.empty and "timestamp" in filtered_tech.columns and "latency_sec" in filtered_tech.columns and "llm_model" in filtered_tech.columns:
    st.subheader("Latency Over Time (by LLM)")
    try:
        chart = alt.Chart(filtered_tech).mark_line().encode(
            x=alt.X('timestamp:T', title='Timestamp'),
            y=alt.Y('latency_sec:Q', title='Latency (sec)'),
            color='llm_model:N',
            tooltip=['timestamp', 'llm_model', 'latency_sec']
        ).properties(width=700, height=300)
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.info(f"Could not display latency time series: {e}")

# 2. Boxplot for Ratings
if not filtered_human.empty and any(col in filtered_human.columns for col in ["quality", "relevance", "accuracy", "uniformity"]):
    st.subheader("Distribution of Ratings (Boxplot)")
    try:
        rating_cols = [col for col in ["quality", "relevance", "accuracy", "uniformity"] if col in filtered_human.columns]
        melted = filtered_human.melt(value_vars=rating_cols, var_name="Rating Type", value_name="Score")
        fig = px.box(melted, x="Rating Type", y="Score", points="all")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Could not display boxplot: {e}")

# 3. Heatmap for LLM/Industry Average Ratings
if not filtered_human.empty and "current_industry" in filtered_human.columns and "llm_model" in filtered_human.columns and "quality" in filtered_human.columns:
    st.subheader("LLM/Industry Average Quality Rating (Heatmap)")
    try:
        pivot = filtered_human.pivot_table(index="llm_model", columns="current_industry", values="quality", aggfunc="mean")
        fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Could not display heatmap: {e}")

# 4. Pie Chart for API Success Rate
if not filtered_tech.empty and "success" in filtered_tech.columns:
    st.subheader("API Success Rate (Pie Chart)")
    try:
        success_counts = filtered_tech["success"].value_counts().rename({1: "Success", 0: "Failure"})
        fig = px.pie(names=success_counts.index, values=success_counts.values, title="API Success vs Failure")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Could not display pie chart: {e}")

# 5. Word Cloud for Comments
if not filtered_human.empty and "comments" in filtered_human.columns:
    st.subheader("Word Cloud of Qualitative Comments")
    try:
        text = " ".join([str(c) for c in filtered_human["comments"].dropna() if c])
        if text.strip():
            wc = WordCloud(width=800, height=300, background_color='white').generate(text)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No comments available for word cloud.")
    except Exception as e:
        st.info(f"Could not display word cloud: {e}")

# ---- RAW DATA (OPTIONAL) ----
with st.expander("Show Raw Data"):
    st.write("Human Evaluation Data:")
    st.dataframe(human_df, use_container_width=True)
    st.write("Technical Metrics Data:")
    st.dataframe(technical_df, use_container_width=True) 