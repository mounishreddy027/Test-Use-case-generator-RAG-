import streamlit as st
import os, shutil
from src.ingestion import IngestionEngine
from src.generator import Generator
from src.vector_store import VectorDB
from src.config import Config

st.set_page_config(page_title="QA RAG Generator", layout="wide")

with st.sidebar:
    st.title("Management")
    if st.button("Ingest Files"):
        with st.spinner("Ingesting..."):
            st.success(f"Done: {IngestionEngine().ingest()}")
    if st.button("🗑️ Reset DB"):
        with st.spinner("Clearing all data..."):
            # 1. Reset the Vector Database
            VectorDB().reset_database()
            
            # 2. Path to the persistent tracking files
            manifest_path = os.path.join(Config.DB_DIR, "ingested_files.json")
            registry_path = os.path.join(Config.DB_DIR, "chunk_registry.json")
            
            # 3. Explicitly delete the JSON registries to "forget" old files
            for path in [manifest_path, registry_path]:
                if os.path.exists(path):
                    os.remove(path)
                    
            st.success("🔥 System Reset: Vector DB and Hash Registries cleared.")
            st.rerun()

st.title("Test/Use case Generator")
query = st.text_input("Enter Request:", key="user_query")

if st.button("Generate", type="primary") and query:
    with st.spinner("Thinking............."):
        response = Generator().generate(query)
        if "error" in response: st.warning(f"⚠️ {response['error']}: {response.get('reason', '')}")
        else: st.json(response)