# ✈️ QA RAG: Test/Use Case Generator
**A production-ready RAG system designed for Senior QA Engineers to generate grounded test cases from requirement documents.**

This application uses a Retrieval-Augmented Generation (RAG) pipeline to ingest complex software requirements and generate structured, high-quality test cases using **Ollama (Llama 3.2)** and a **Hybrid Retrieval** engine.

---

## 🛠️ Key Technical Features
* **Multi-Modal Ingestion**: Supports `.txt`, `.md`, `.pdf`, and `.docx`. Includes **OCR** (Tesseract) for scanned documents and images.
* **Hybrid Retrieval (Requirement 2)**: Combines semantic Vector search (**ChromaDB**) with keyword-based retrieval (**BM25**) to ensure exact match for requirement IDs like `FR-FF-01`.
* **Safety Guardrails (Requirement 4)**: 
    * **Evidence Threshold**: Blocks responses if the retrieval confidence score exceeds **1.25** to prevent hallucinations.
    * **Deduplication**: Uses **MD5** file hashing and **SHA-256** chunk hashing to prevent redundant data.
* **Observability (Requirement 5)**: Real-time dashboard displays retrieval latency, source chunk counts, and the exact context provided to the LLM.



---

## 💾 Storage Architecture

The application uses two distinct storage methods for reliability and ease of use:

1. **Document Source (Bind Mount)**: 
   - Linked to your local `./data` folder. 
   - Any files (PDF, DOCX, Images) placed here are immediately available for ingestion.
2. **Vector Database (Named Volume)**: 
   - The database files are stored in a Docker-managed volume named `rag_storage`. 
   - This keeps the database separate from your source code for Git cleanliness.

### 🛠️ Commands to Manage Storage
- **To Clear the Database**: 
  If you need to completely wipe the knowledge base, run:
  ```powershell
  docker rm -f tender_borg
  docker volume rm rag_storage
---

## 🚀 Setup & Installation

### **Prerequisites**
* **Docker** & **Docker Compose** installed.
* **Ollama** running on your host machine with the `llama3.2` model pulled (`ollama pull llama3.2`).

### **1. Build the Application**
```powershell
docker build -t rag-app-final .