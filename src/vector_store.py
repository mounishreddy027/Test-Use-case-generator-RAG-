import os
import chromadb
from chromadb.config import Settings  # FIX: Explicitly import Settings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document

# Absolute import for config
from src.config import Config 

class VectorDB:
    def __init__(self):
        # 1. Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            cache_folder=Config.MODEL_CACHE,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 2. Initialize the Persistent Client with Reset permissions
        self.client = chromadb.PersistentClient(
            path=Config.DB_DIR,
            settings=Settings(allow_reset=True) # Now Settings is defined
        )
        
        # 3. Connect Chroma to the client
        self.db = Chroma(
            client=self.client,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        """Adds processed chunks to the vector store."""
        if not documents:
            return
        self.db.add_documents(documents)

    def reset_database(self):
        """Safely clears all collections in the mounted volume."""
        self.client.reset()

    def get_hybrid_retriever(self):
        """Requirement 2: Ensemble Vector + Keyword retrieval."""
        # Semantic Retriever
        vector_retriever = self.db.as_retriever(
            search_kwargs={"k": Config.TOP_K_RETRIEVAL}
        )
        
        # Keyword Retriever (BM25)
        docs_data = self.db.get()
        if not docs_data["documents"]:
            return vector_retriever
            
        obj_docs = [
            Document(page_content=text, metadata=meta) 
            for text, meta in zip(docs_data["documents"], docs_data["metadatas"])
        ]
        
        bm25_retriever = BM25Retriever.from_documents(obj_docs)
        bm25_retriever.k = Config.TOP_K_RETRIEVAL

        # Ensemble: 60% Vector, 40% Keyword
        return EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.6, 0.4]
        )