# RAG: Test/Use Case Generator
**A production-ready RAG system designed for Senior QA Engineers to generate grounded test cases from requirement documents.**

This application leverages a specialized Retrieval-Augmented Generation (RAG) pipeline to ingest complex software requirements and generate structured, high-quality test cases using **Ollama (Llama 3.2)** and a **Hybrid Retrieval** engine.

---

## Architecture
The system follows a modular architecture designed for local deployment and high precision:
* **Orchestration**: Built with **LangChain** to manage the flow between data ingestion, vector storage, and the LLM.
* **Execution Environment**: Fully containerized using **Docker** to ensure consistency across development and production environments.
* **Domain Focus**: The system includes a **Task Classification Layer** that restricts generation strictly to **Test Cases** or **Use Cases**, rejecting non-QA queries.



---

## Ingestion
The ingestion layer is designed to handle diverse documentation formats while maintaining data integrity:
* **Multi-Modal Support**: Processes `.txt`, `.md`, `.pdf`, and `.docx` files.
* **OCR Pipeline**: Integrated **Tesseract OCR** for extracting text from scanned documents and requirement screenshots.
* **Advanced Deduplication**: Uses **MD5** file hashing and **SHA-256** chunk hashing to prevent redundant data from entering the knowledge base.
* **Chunking Strategy**: Utilizes `RecursiveCharacterTextSplitter` to maintain semantic relationships within technical specifications.

---

## Retrieval
To satisfy the requirement for high-precision matching of functional IDs, the system employs a **Hybrid Retrieval** strategy:
* **Ensemble Engine**: Combines **Semantic Vector Search** (via ChromaDB) with **Keyword-based Retrieval** (via BM25).
* **Weighted Scoring**: Uses a weighted split to ensure exact matches for requirement IDs like `FR-FF-01` while maintaining semantic context.
* **Embeddings**: Powered by local **HuggingFace Sentence Transformers**.

---

## Generation
The generation layer is optimized for deterministic and grounded output:
* **Model**: Utilizes **Llama 3.2** via Ollama for private, local generation.
* **Structured Output**: Enforces a strict **JSON schema** for all outputs, providing clear fields for *Steps*, *Expected Results*, and *Negative Scenarios*.
* **Contextual Supremacy**: Prompt engineering ensures the LLM prioritizes retrieved document chunks over its internal pre-trained knowledge.

---

## Safety Guardrails
To ensure reliability in a professional QA workflow, several safeguards are implemented:
* **Evidence Threshold**: Blocks responses if the retrieval confidence score exceeds **1.25**, preventing hallucinations when data is missing.
* **Task Gatekeeping**: Uses a validation filter to ensure the system only responds to professional QA tasks like Test Case or Use Case generation.
* **Out-of-Scope Detection**: Explicitly identifies requirements marked as "Out of Scope" in the source text and prevents the generation of positive test cases for those features.



---

## Storage Architecture
The application uses two distinct storage methods for reliability and ease of use:
1.  **Document Source (Bind Mount)**: Linked to your local `./data` folder. Any files (PDF, DOCX, Images) placed here are immediately available for ingestion.
2.  **Vector Database (Named Volume)**: Database files are stored in a Docker-managed volume named `rag_storage` to keep them persistent yet separate from source code.

---

## Setup & Installation

### **Prerequisites**
* **Docker** & **Docker Compose** installed.
* **Ollama** running on your host machine with the `llama3.2` model pulled (`ollama pull llama3.2`).

### **1. Build and Run**
```powershell
# Build the image
docker build -t rag-app-final .

# Run the container
docker run -d -p 8501:8501 --name tender_borg `
  -v ${PWD}/data:/app/data `
  -v rag_storage:/app/db `
  --add-host=host.docker.internal:host-gateway `
  rag-app-final