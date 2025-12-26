import argparse
import os
import json
import sys
from src.ingestion import IngestionEngine
from src.generator import Generator

def main():
    parser = argparse.ArgumentParser(description="Local RAG QA System - Test Case Generator")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents from the data folder")
    parser.add_argument("--query", type=str, help="The test case or use case query to generate")
    args = parser.parse_args()

    if args.ingest:
        # REQUIREMENT 5: Clear logs for the ingestion phase
        print("\n" + "="*60)
        print("🚀 [PHASE 1: INGESTION] Building Local Knowledge Base...")
        print("="*60)
        try:
            engine = IngestionEngine()
            engine.ingest()
            print("\n✨ SUCCESS: Vector database is built and persisted in /app/db.")
        except Exception as e:
            print(f"\n❌ INGESTION ERROR: {str(e)}")
            sys.exit(1)

    elif args.query:
        # REQUIREMENT 5: Logs for the retrieval and generation phase
        print("\n" + "="*60)
        print(f"🔍 [PHASE 2: RETRIEVAL & GENERATION]")
        print(f"User Request: {args.query}")
        print("="*60)
        
        try:
            # The Generator class now manages its own DB connection and debug logs internally
            generator = Generator()
            response = generator.generate(args.query)
            
            # REQUIREMENT 4 & 5: Distinguish between Guardrail blocks and successful generation
            if isinstance(response, dict) and "error" in response:
                print("\n⚠️  REQUEST RESTRICTED OR INSUFFICIENT INFO:")
                print(json.dumps(response, indent=2))
            else:
                # REQUIREMENT 3: Final proper structured JSON output
                print("\n✅ VALID JSON GENERATED:")
                print(json.dumps(response, indent=2))
                
        except Exception as e:
            print(f"\n❌ GENERATION ERROR: {str(e)}")
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()