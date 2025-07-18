import streamlit as st
import time
from utils.auth import enforce_page_access
from utils.llm_clients import get_llm_client

# ---- ACCESS CONTROL ----
if not enforce_page_access("LLM Health Check", required_role="admin"):
    st.stop()

st.set_page_config(page_title="LLM Health Check", layout="wide")
st.title("🤖 LLM Health Check Dashboard")

LLMS = [
    {"provider": "groq", "model": "llama3-70b-8192"},
    {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
    {"provider": "openrouter", "model": "google/gemma-3-27b-it:free"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct:free"}
]

TEST_PROMPT = "What is the capital of France?"

st.info("This page checks the live status of all configured LLMs. Only admins can access this page.")

run_check = st.button("Run Health Check", type="primary")

if run_check:
    results = []
    for llm in LLMS:
        provider = llm["provider"]
        model = llm["model"]
        status = ""
        latency = None
        response_snippet = ""
        try:
            client = get_llm_client(provider, model)
            start = time.time()
            response = client.generate(TEST_PROMPT)
            latency = time.time() - start
            status = "✅ OK"
            response_snippet = response[:120] + ("..." if len(response) > 120 else "")
        except Exception as e:
            latency = None
            status = "❌ FAIL"
            response_snippet = str(e)[:120] + ("..." if len(str(e)) > 120 else "")
        results.append({
            "Provider": provider,
            "Model": model,
            "Status": status,
            "Latency (s)": f"{latency:.2f}" if latency else "-",
            "Response/Error": response_snippet
        })
    st.subheader("LLM Health Status")
    st.table(results)
    st.caption("Last checked: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
else:
    st.info("Click 'Run Health Check' to test all LLMs.") 