import os, json, re, time
from langchain_community.llms import Ollama
from src.vector_store import VectorDB
from src.config import Config

class Generator:
    def __init__(self):
        self.vector_db = VectorDB()
        self.llm = Ollama(
            model=Config.LLM_MODEL, 
            base_url=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"), 
            temperature=0, format="json"
        )

    def is_valid_qa_query(self, query):
        keywords = ["test", "case", "scenario", "verify", "check", "qa", "use case", "requirement"]
        return any(w in query.lower() for w in keywords)

    def generate(self, query):
        if not self.is_valid_qa_query(query):
            return {"error": "Access Denied.", "reason": "Restricted to QA tasks."}

        # 1. Check Evidence Threshold
        results = self.vector_db.db.similarity_search_with_score(query, k=1)
        if not results or results[0][1] > Config.CONFIDENCE_THRESHOLD:
            return {"error": "Insufficient Context", "reason": "No high-confidence evidence found."}

        # 2. Hybrid Retrieval
        retriever = self.vector_db.get_hybrid_retriever()
        valid_chunks = retriever.invoke(query)
        context_text = "\n\n".join([f"Content: {d.page_content}" for d in valid_chunks])
        filenames = list(set([d.metadata.get('source', 'unknown') for d in valid_chunks]))

        # YOUR SYSTEM PROMPT (UNCHANGED)
        system_prompt = f"""
[LAYER 1: IDENTITY & FORMAT]
You are a Senior QA Engineer. Return ONLY valid JSON. 
No prose, no markdown code blocks (```json).

[LAYER 2: ABSOLUTE CONSTRAINTS]
1. CONTEXTUAL SUPREMACY: Use ONLY the provided [LAYER 4] knowledge.
2. NO HALLUCINATION: If a requirement is not in the context, list it in 'missing_info'. NEVER guess.
3. CONTRADICTION RULE: If the user query says "5 seconds" but the context says "500ms", you MUST use "500ms".
4. SCOPE GUARDRAIL: If the user asks for a feature in an 'Out of Scope' section, create a Negative Case only.
5. CITATION MANDATE: Every field (Steps, Expected Result, etc.) MUST end with the source name in brackets, e.g.,.

[LAYER 3: TASK CLASSIFICATION]
- Use 'Test Case' for technical verification/steps.
- Use 'Use Case' for high-level user goals/flows.

[LAYER 4: RETRIEVED KNOWLEDGE (The Ground Truth)]
{context_text}

[LAYER 5: USER REQUEST]
{query}

[LAYER 6: DYNAMIC OUTPUT TEMPLATE]
{{
  "type": "Test Case OR Use Case",
  "feature": "Name",
  "objective": "Grounded goal",
  "preconditions": "System state",
  "steps": ["Step 1: Action", "Step 2: Action"],
  "expected_result": "Detailed response citing specific metrics from text",
  "negative_cases": [{{"scenario": "Invalid action", "expected": "Error behavior"}}],
  "boundary_cases": [{{"scenario": "Limit test", "expected": "Threshold behavior"}}],
  "missing_info": [],
  "assumptions": [],
  "source_metadata": {{ "ingested_files": {json.dumps(filenames)}, "chunks_retrieved": {len(valid_chunks)} }}
}}
"""
        response = self.llm.invoke(system_prompt)
        return self._parse_json(response)

    def _parse_json(self, text):
        try:
            text = re.sub(r'```json\s*|\s*```', '', text).strip()
            match = re.search(r'\{.*\}', text, re.DOTALL)
            return json.loads(match.group(0)) if match else json.loads(text)
        except Exception: return {"error": "Parsing failed"}