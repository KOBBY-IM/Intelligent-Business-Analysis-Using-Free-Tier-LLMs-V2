import streamlit as st
from utils.auth import enforce_page_access

st.set_page_config(page_title="Analysis Hub", layout="wide")

# ---- ACCESS CONTROL ----
if not enforce_page_access("Analysis Hub", required_role="admin"):
    st.stop()

# ---- MAIN ANALYSIS HUB PAGE ----
st.title("🔬 LLM Evaluation Analysis Hub")

st.markdown("""
Welcome to the LLM Evaluation Analysis Hub! This is your central dashboard for accessing comprehensive analysis tools.

## 📊 Available Analysis Tools

Choose from the following specialized analysis pages:

### 👥 **Blind Evaluation Analysis**
- **Purpose**: Analyze human evaluation data from blind assessments
- **Features**: 
  - Statistical analysis with confidence intervals
  - Multi-dimensional LLM performance comparison
  - Rating distributions and significance testing
  - Qualitative feedback analysis
  - Real-time filtering and updates

### ⚡ **Technical Metrics Analysis**
- **Purpose**: Analyze automated technical performance metrics
- **Features**:
  - Performance metrics over time
  - Latency, throughput, and reliability analysis
  - Industry-specific performance comparisons
  - Heatmap visualizations
  - Reliability and coverage analysis

## 🎯 **How to Use**

1. **Navigate to the desired analysis page** using the sidebar
2. **Apply filters** to focus on specific data subsets
3. **Explore visualizations** and statistical insights
4. **Export results** for further analysis

## 📈 **Data Sources**

- **Blind Evaluation Data**: Human assessments of LLM responses
- **Technical Metrics**: Automated batch evaluation results
- **Real-time Updates**: Live data refresh capabilities

---

**Select an analysis page from the sidebar to get started!**
""")

# Display current status
col1, col2 = st.columns(2)

with col1:
    st.info("👥 **Blind Evaluation Analysis**\n\nAccess comprehensive human evaluation insights with statistical analysis and visualizations.")

with col2:
    st.info("⚡ **Technical Metrics Analysis**\n\nExplore automated performance metrics with real-time monitoring and industry comparisons.")

# Footer
st.markdown("---")
st.markdown("*Analysis Hub - Central dashboard for LLM evaluation insights*") 