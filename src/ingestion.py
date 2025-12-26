import os
import glob
import hashlib
import json
import re
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

from langchain_community.document_loaders import (
    PyPDFLoader, 
    UnstructuredFileLoader, 
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Absolute imports for package consistency
from src.vector_store import VectorDB
from src.config import Config

class IngestionEngine:
    def __init__(self):
        """Initializes the engine with a centralized VectorDB instance."""
        self.vector_db = VectorDB()
        self.manifest_path = os.path.join(Config.DB_DIR, "ingested_files.json")
        self.chunk_registry_path = os.path.join(Config.DB_DIR, "chunk_registry.json")

    def get_file_hash(self, file_path):
        """Generates an MD5 hash of a file to track changes."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def ocr_pdf(self, file_path):
        """Converts scanned PDF pages to images and performs OCR."""
        pages = convert_from_path(file_path)
        return "".join([pytesseract.image_to_string(p) for p in pages])

    def _is_high_quality(self, text):
        """
        Requirement 4: Chunk quality checks.
        Filters out noise, boilerplate, and low-signal data.
        """
        # 1. Length check
        if len(text) < 50:  # Minimum 50 chars
            return False
            
        # 2. Alphanumeric ratio check (prevents garbled OCR text)
        alnum_count = sum(1 for char in text if char.isalnum())
        if (alnum_count / len(text)) < 0.4:
            return False
            
        # 3. Boilerplate filtering
        boilerplate_patterns = [r"Page \d+ of \d+", r"All rights reserved", r"Confidential"]
        if any(re.search(pattern, text, re.I) for pattern in boilerplate_patterns):
            return False
            
        return True

    def ingest(self):
        """Main pipeline for parsing, chunking, and deduplication."""
        # Load File Manifest (to skip already processed files)
        file_log = {}
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r') as f:
                file_log = json.load(f)

        # Load Chunk Registry (for content-level deduplication)
        processed_chunk_hashes = set()
        if os.path.exists(self.chunk_registry_path):
            with open(self.chunk_registry_path, 'r') as f:
                processed_chunk_hashes = set(json.load(f))

        documents = []
        for file_path in glob.glob(os.path.join(Config.DATA_DIR, "*")):
            if os.path.isdir(file_path): 
                continue
            
            # File-level Deduplication
            f_hash = self.get_file_hash(file_path)
            if file_log.get(file_path) == f_hash: 
                continue 

            ext = os.path.splitext(file_path)[1].lower()
            try:
                if ext in [".png", ".jpg", ".jpeg"]:
                    content = pytesseract.image_to_string(Image.open(file_path))
                    current_docs = [Document(page_content=content, metadata={"source": file_path})]
                elif ext == ".pdf":
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    # Trigger OCR if the PDF is scanned (low text content)
                    content = "".join([d.page_content for d in docs]).strip()
                    if len(content) < 150:
                        content = self.ocr_pdf(file_path)
                    current_docs = [Document(page_content=content, metadata={"source": file_path})]
                else:
                    # Handles .docx, .txt, .md via unstructured/text loaders
                    loader = UnstructuredFileLoader(file_path)
                    current_docs = loader.load()

                documents.extend(current_docs)
                file_log[file_path] = f_hash
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        # Processing Chunks
        new_chunks_added = 0
        if documents:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE, 
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            raw_chunks = splitter.split_documents(documents)
            
            final_chunks = []
            for chunk in raw_chunks:
                # Content-Level Deduplication
                content_hash = hashlib.sha256(chunk.page_content.encode()).hexdigest()
                
                if content_hash not in processed_chunk_hashes:
                    if self._is_high_quality(chunk.page_content):
                        final_chunks.append(chunk)
                        processed_chunk_hashes.add(content_hash)
            
            if final_chunks:
                self.vector_db.add_documents(final_chunks)
                new_chunks_added = len(final_chunks)
                
                # Update persistent logs
                with open(self.manifest_path, 'w') as f:
                    json.dump(file_log, f)
                with open(self.chunk_registry_path, 'w') as f:
                    json.dump(list(processed_chunk_hashes), f)
                    
        return {
            "status": "Success",
            "files_processed": len(documents),
            "new_chunks_added": new_chunks_added
        }