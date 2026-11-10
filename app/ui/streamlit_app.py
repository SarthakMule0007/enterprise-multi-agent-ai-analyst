import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI Analyst", page_icon="📊", layout="wide")
st.title("📊 Enterprise Multi-Agent AI Analyst")
st.caption("Ask a business question. The supervisor plans a query, checks the data, and builds an evidence-backed answer.")
api_url = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

with st.sidebar:
    st.subheader("Data connection")
    try:
        health = requests.get(f"{api_url}/health", timeout=5).json()
        st.success(f"API {health['status']} · database {health['database']}")
        with st.expander("Available schema"):
            st.json(requests.get(f"{api_url}/schema", timeout=5).json())
    except requests.RequestException:
        st.error("Cannot connect to the API. Start the Docker services and refresh.")

examples = ["How did monthly revenue change?", "Which region has the most orders?", "Compare revenue by product category"]
question = st.text_input("Your question", placeholder="e.g. How did monthly revenue change?")
chosen = st.selectbox("Example questions", ["Choose an example…", *examples])
if chosen != "Choose an example…" and st.button("Use example"):
    question = chosen

if st.button("Analyze", type="primary"):
    if len(question.strip()) < 3:
        st.warning("Enter a question with at least 3 characters.")
    else:
        with st.spinner("Supervisor is coordinating the analysis…"):
            try:
                response = requests.post(f"{api_url}/analyze", json={"question": question}, timeout=120)
                response.raise_for_status()
                result = response.json()
                st.subheader("Answer")
                st.markdown(result.get("report", "No report was returned."))
                left, right = st.columns([3, 2])
                with left:
                    st.subheader("Query results")
                    rows = result.get("rows", [])
                    if rows:
                        st.dataframe(pd.DataFrame(rows), use_container_width=True)
                    else:
                        st.info("No rows returned.")
                with right:
                    st.subheader("Analysis summary")
                    st.json(result.get("stats", {}))
                with st.expander("SQL used"):
                    st.code(result.get("sql", ""), language="sql")
                if result.get("context"):
                    with st.expander("Retrieved metric definitions"):
                        for item in result["context"]:
                            st.write(item)
                if result.get("error"):
                    st.error(result["error"])
            except requests.RequestException as exc:
                st.error(f"Analysis request failed: {exc}")
