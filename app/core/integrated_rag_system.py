# app/core/integrated_rag_system.py
import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import uuid

# Import components
from .semantic_search import SemanticSearch # Assuming BasicQueryAnalyzer is now in SemanticSearch
from .response_generator import ResponseGenerator  
from .initialize_chroma_db import initialize_chroma_db

@dataclass
class RAGResponse:
    """Structured response from the RAG system"""
    query_id: str
    query: str
    response: str
    relevance_score: float # Overall relevance of the response/sources
    sources: List[Dict[str, Any]] # Top N sources with their individual scores
    processing_time: float
    metadata: Dict[str, Any] # e.g., query_analysis, timings

class OptimizedRAGSystem:
    """Complete and optimized RAG system."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self._initialize_components()
        self.is_initialized = False # Should be set to True after successful DB init
        self.initialization_time = 0.0
        logging.info("OptimizedRAGSystem created. Call initialize_database() to prepare for queries.")
    
    def _initialize_components(self):
        try:
            self.search_engine = SemanticSearch(api_key=self.api_key, chroma_path="./chroma_db")
            self.response_generator = ResponseGenerator(api_key=self.api_key)
            logging.info("Core components (SearchEngine, ResponseGenerator) initialized.")
        except Exception as e:
            logging.error(f"Error initializing core components: {e}", exc_info=True)
            raise
    
    def initialize_database(self, reset_collections: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        try:
            initialize_chroma_db(reset_collections=reset_collections) # Assumes this sets up ChromaDB correctly
            
            # Reload collections in search engine to reflect any changes
            self.search_engine._load_collections() 
            # self.search_engine._initialize_reranker() # Already called in SemanticSearch init
            # self.search_engine._initialize_query_analyzer() # Already called in SemanticSearch init
            
            self.initialization_time = time.time() - start_time
            self.is_initialized = True
            
            stats = {
                "initialization_time": self.initialization_time,
                "collections_loaded": len(self.search_engine.collections),
                "total_documents": sum(
                    collection.count() 
                    for collection_name, collection in self.search_engine.collections.items() if collection
                ),
                "reranker_status": self.search_engine.reranker_config, # Using new attribute name
                "query_analyzer_status": "Initialized in SearchEngine" if self.search_engine.query_analyzer else "Not initialized",
                "reset_performed": reset_collections
            }
            logging.info(f"Database initialization completed successfully: {stats}")
            return stats
        except Exception as e:
            self.is_initialized = False
            logging.error(f"Error initializing database: {e}", exc_info=True)
            raise
    
    def query(self, 
              query_text: str,
              conversation_history: Optional[List[Tuple[str, str]]] = None,
              user_context: Optional[Dict[str, Any]] = None) -> RAGResponse: # user_context not used in current flow
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize_database() first.")
        
        query_id = str(uuid.uuid4())
        processing_start_time = time.time()
        
        try:
            # Step 1: Analyze Query (now done by SemanticSearch's analyzer)
            if not self.search_engine.query_analyzer:
                 raise RuntimeError("Query Analyzer not available in SearchEngine.")
            query_analysis = self.search_engine.query_analyzer.analyze_query(query_text)
            query_analysis["original_query"] = query_text # Store original query for reference

            # Step 2: Search for relevant documents
            search_start_time = time.time()
            # Pass query_analysis to search for more context-aware searching if SemanticSearch.search is adapted for it
            search_results = self.search_engine.search(query_text, query_analysis, top_k=10)
            search_time = time.time() - search_start_time
            
            # Step 3: Generate response
            generation_start_time = time.time()
            # Pass query_analysis to ResponseGenerator
            response_text = self.response_generator.generate_response(
                query_text, search_results, query_analysis, conversation_history
            )
            generation_time = time.time() - generation_start_time
            
            total_processing_time = time.time() - processing_start_time
            
            # Calculate overall relevance score from top sources (capped at 1.0)
            overall_relevance = 0.0
            if search_results:
                relevant_scores = [r.get("relevance_score", 0.0) for r in search_results[:5]] # Consider top 5 for overall score
                if relevant_scores:
                    overall_relevance = sum(relevant_scores) / len(relevant_scores)
            
            # Prepare sources for response (top 5)
            response_sources = []
            for result in search_results[:5]: 
                response_sources.append({
                    "collection": result.get("collection", ""),
                    "relevance_score": round(result.get("relevance_score", 0.0), 3), # Rounded for display
                    "content_preview": result.get("content", "")[:200] + "..." if result.get("content") else "",
                    "metadata": result.get("metadata", {}),
                    # context_type might be derived/standardized in ResponseGenerator's _convert_results_to_chunks
                    "context_type": result.get("metadata", {}).get("type", "general") 
                })
            
            return RAGResponse(
                query_id=query_id,
                query=query_text,
                response=response_text,
                relevance_score=round(overall_relevance, 3),
                sources=response_sources,
                processing_time=round(total_processing_time, 3),
                metadata={
                    "query_analysis": query_analysis, # Contains intents, expected_output, complexity
                    "timings": {
                        "search_sec": round(search_time, 3),
                        "generation_sec": round(generation_time, 3),
                        "total_sec": round(total_processing_time, 3)
                    },
                    "num_raw_search_results": len(search_results) # Number of results before limiting to top N for sources
                }
            )
        except Exception as e:
            logging.error(f"Error processing query (ID: {query_id}): {e}", exc_info=True)
            return RAGResponse(
                query_id=query_id,
                query=query_text,
                response=f"Desculpe, ocorreu um erro interno ao processar sua consulta: {str(e)}",
                relevance_score=0.0,
                sources=[],
                processing_time=round(time.time() - processing_start_time, 3),
                metadata={"error": str(e), "query_analysis": query_analysis if 'query_analysis' in locals() else {"error":"failed before analysis"}}
            )

    # get_system_status and factory function create_rag_system would remain largely the same
    # but their reported stats might change based on the new structure.
    # CLI (main function) would also remain structurally similar.

# ... (rest of the OptimizedRAGSystem class, create_rag_system, main, __all__)
# Ensure the main function correctly initializes and uses the system.
# For example, if running a query from CLI:
# if args.query:
#     try:
#         if not system.is_initialized:
#             print("System not initialized. Run with --init-db first.")
#             sys.exit(1)
#         print(f"Processing query: {args.query}")
#         # Query analysis happens inside system.query now
#         response = system.query(args.query) 
#         # ... print response details ...
#     except Exception as e:
#         print(f"Error processing query via CLI: {e}")