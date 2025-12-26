import os

class Config:
    # Paths - Standardized for Docker
    DATA_DIR = "/app/data"
    DB_DIR = "/app/db"
    MODEL_CACHE = "/app/models"
    
    # Models
    LLM_MODEL = "llama3.2"       
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    
    # Retrieval Hyperparameters
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RETRIEVAL = 4
    CONFIDENCE_THRESHOLD = 1.25  # Distance threshold (lower is better)

    MIN_CHUNK_LENGTH = 50       # Ignore chunks shorter than 50 chars (noise)
    ALPHANUMERIC_RATIO = 0.4    # At least 40% of the chunk must be letters/numbers
    MAX_REPETITION_RATIO = 0.3