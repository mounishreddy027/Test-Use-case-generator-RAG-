import streamlit as st
import pandas as pd

st.set_page_config(page_title="RAG Dashboard", layout="wide")

if "rag_logs" not in st.session_state:
    st.session_state.rag_logs = []

st.title("📊 Performance Dashboard")

if not st.session_state.rag_logs:
    st.warning("No query data found. Please run a query on the Main Page first.")
    st.stop() 

logs = st.session_state.rag_logs
latest = logs[0] 

c1, c2, c3 = st.columns(3)
c1.metric("Latest Latency", f"{latest.get('latency', 0)}s")
c2.metric("Chunks Retrieved", latest.get('chunks_count', 0))
c3.metric("Total History", len(logs))

st.divider()

st.subheader("🔍 Context Grounding")
with st.expander(f"View Retrieved Chunks for: {latest.get('query')}"):
    st.info(latest.get('context', "No context recorded."))

st.subheader("📜 History")
df = pd.DataFrame(logs)[["timestamp", "query", "latency", "chunks_count"]]
st.dataframe(df, use_container_width=True)