# app/core/integrated_rag_system.py
import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import uuid

# Import components
from .semantic_search import SemanticSearch
from .initialize_chroma_db import initialize_chroma_db

@dataclass
class SearchResponse:
    """Structured response from the semantic search system"""
    query_id: str
    query: str
    results: List[Dict[str, Any]]  # Search results with their scores and metadata
    processing_time: float
    metadata: Dict[str, Any]  # e.g., query_analysis, timings

class OptimizedSearchSystem:
    """Complete and optimized semantic search system."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self._initialize_components()
        self.is_initialized = False  # Should be set to True after successful DB init
        self.initialization_time = 0.0
        logging.info("OptimizedSearchSystem created. Call initialize_database() to prepare for queries.")
    
    def _initialize_components(self):
        try:
            self.search_engine = SemanticSearch(api_key=self.api_key, chroma_path="./chroma_db")
            logging.info("Core component (SearchEngine) initialized.")
        except Exception as e:
            logging.error(f"Error initializing core component: {e}", exc_info=True)
            raise
    
    def initialize_database(self, reset_collections: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        try:
            initialize_chroma_db(reset_collections=reset_collections)
            
            # Reload collections in search engine to reflect any changes
            self.search_engine._load_collections() 
            
            self.initialization_time = time.time() - start_time
            self.is_initialized = True
            
            stats = {
                "initialization_time": self.initialization_time,
                "collections_loaded": len(self.search_engine.collections),
                "total_documents": sum(
                    collection.count() 
                    for collection_name, collection in self.search_engine.collections.items() if collection
                ),
                "query_analyzer_status": "Initialized in SearchEngine" if self.search_engine.query_analyzer else "Not initialized",
                "reset_performed": reset_collections
            }
            logging.info(f"Database initialization completed successfully: {stats}")
            return stats
        except Exception as e:
            self.is_initialized = False
            logging.error(f"Error initializing database: {e}", exc_info=True)
            raise
    
    def search(self, 
              query_text: str,
              top_k: int = 10) -> SearchResponse:
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize_database() first.")
        
        query_id = str(uuid.uuid4())
        processing_start_time = time.time()
        
        try:
            # Step 1: Analyze Query
            if not self.search_engine.query_analyzer:
                 raise RuntimeError("Query Analyzer not available in SearchEngine.")
            query_analysis = self.search_engine.query_analyzer.analyze_query(query_text)
            query_analysis["original_query"] = query_text

            # Step 2: Search for relevant documents
            search_start_time = time.time()
            search_results = self.search_engine.search(query_text, query_analysis, top_k=top_k)
            search_time = time.time() - search_start_time
            
            total_processing_time = time.time() - processing_start_time
            
            # Prepare results with detailed information
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "collection": result.get("collection", ""),
                    "relevance_score": round(result.get("relevance_score", 0.0), 3),
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "has_code_example": result.get("has_code_example", False),
                    "has_field_definition": result.get("has_field_definition", False),
                    "has_method_description": result.get("has_method_description", False)
                })
            
            return SearchResponse(
                query_id=query_id,
                query=query_text,
                results=formatted_results,
                processing_time=round(total_processing_time, 3),
                metadata={
                    "query_analysis": query_analysis,
                    "timings": {
                        "search_sec": round(search_time, 3),
                        "total_sec": round(total_processing_time, 3)
                    },
                    "num_results": len(search_results)
                }
            )
        except Exception as e:
            logging.error(f"Error processing query (ID: {query_id}): {e}", exc_info=True)
            return SearchResponse(
                query_id=query_id,
                query=query_text,
                results=[],
                processing_time=round(time.time() - processing_start_time, 3),
                metadata={
                    "error": str(e), 
                    "query_analysis": query_analysis if 'query_analysis' in locals() else {"error": "failed before analysis"}
                }
            )

def create_search_system(api_key: Optional[str] = None) -> OptimizedSearchSystem:
    """Factory function to create and initialize a search system."""
    system = OptimizedSearchSystem(api_key=api_key)
    return system

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Semantic Search System")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database")
    parser.add_argument("--reset", action="store_true", help="Reset collections before initialization")
    parser.add_argument("--query", type=str, help="Query to process")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return")
    
    args = parser.parse_args()
    
    try:
        system = create_search_system()
        
        if args.init_db:
            print("Initializing database...")
            stats = system.initialize_database(reset_collections=args.reset)
            print(f"Database initialized: {stats}")
        
        if args.query:
            if not system.is_initialized:
                print("System not initialized. Run with --init-db first.")
                sys.exit(1)
            
            print(f"Processing query: {args.query}")
            response = system.search(args.query, top_k=args.top_k)
            
            print("\nSearch Results:")
            print("=" * 80)
            for i, result in enumerate(response.results, 1):
                print(f"\nResult #{i}")
                print(f"Collection: {result['collection']}")
                print(f"Score: {result['relevance_score']:.4f}")
                print(f"Content: {result['content'][:200]}...")
                print("-" * 40)
            
            print(f"\nProcessing time: {response.processing_time:.2f} seconds")
            print(f"Query analysis: {response.metadata['query_analysis']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)