# integrated_rag_system.py - Sistema RAG integrado com todas as otimizações
import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import uuid

# Import components
from .semantic_search import SemanticSearch
from .response_generator import ResponseGenerator  
from .initialize_chroma_db import initialize_chroma_db

@dataclass
class RAGResponse:
    """Structured response from the RAG system"""
    query_id: str
    query: str
    response: str
    relevance_score: float
    sources: List[Dict[str, Any]]
    processing_time: float
    metadata: Dict[str, Any]

class OptimizedRAGSystem:
    """Sistema RAG completo e otimizado"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the optimized RAG system
        
        Args:
            api_key: OpenAI API key
        """
        # API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize components
        self._initialize_components()
        
        # System state
        self.is_initialized = False
        self.initialization_time = 0.0
        
        logging.info("OptimizedRAGSystem initialized successfully")
    
    def _initialize_components(self):
        """Initialize core components with configuration"""
        
        try:
            # Initialize semantic search with configuration
            self.search_engine = SemanticSearch(
                api_key=self.api_key,
                chroma_path="./chroma_db"
            )
            
            # Initialize response generator with configuration
            self.response_generator = ResponseGenerator(api_key=self.api_key)
            
            logging.info("Core components initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing components: {e}")
            raise
    
    def initialize_database(self, reset_collections: bool = False) -> Dict[str, Any]:
        """
        Initialize ChromaDB with optimizations
        
        Args:
            reset_collections: Whether to reset existing collections
            
        Returns:
            Initialization statistics
        """
        
        start_time = time.time()
        
        try:
            # Initialize ChromaDB with optimizations
            initialize_chroma_db(reset_collections=reset_collections)
            
            # Reload search engine collections
            self.search_engine._load_collections()
            self.search_engine._initialize_reranker()
            
            self.initialization_time = time.time() - start_time
            self.is_initialized = True
            
            # Get post-initialization statistics
            stats = {
                "initialization_time": self.initialization_time,
                "collections_loaded": len(self.search_engine.collections),
                "total_documents": sum(
                    collection.count() 
                    for collection in self.search_engine.collections.values()
                ),
                "reranker_fitted": self.search_engine.reranker.is_fitted,
                "reset_performed": reset_collections
            }
            
            logging.info(f"Database initialized successfully: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def query(self, 
              query_text: str,
              conversation_history: Optional[List[Tuple[str, str]]] = None,
              user_context: Optional[Dict[str, Any]] = None) -> RAGResponse:
        """
        Process a query through the optimized RAG pipeline
        
        Args:
            query_text: User query
            conversation_history: Previous conversation turns
            user_context: Additional user context
            
        Returns:
            Structured RAG response
        """
        
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize_database() first.")
        
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        try:
            return self._process_query_internal(
                query_id, query_text, conversation_history, user_context
            )
        except Exception as e:
            logging.error(f"Error processing query {query_id}: {e}")
            
            # Return error response
            return RAGResponse(
                query_id=query_id,
                query=query_text,
                response=f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                relevance_score=0.0,
                sources=[],
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _process_query_internal(self,
                              query_id: str,
                              query_text: str, 
                              conversation_history: Optional[List[Tuple[str, str]]]):
        """Internal query processing with detailed monitoring"""
        
        start_time = time.time()
        
        # Analyze query for optimization
        query_analysis = self.search_engine.query_analyzer.analyze_query(query_text)
        
        # Step 1: Search for relevant documents
        search_start = time.time()
        search_results = self.search_engine.search(
            query_text, 
            top_k=10  # Simplified fixed value
        )
        search_time = time.time() - search_start
        
        # Step 2: Generate response with optimized context
        generation_start = time.time()
        response_text = self.response_generator.generate_response(
            query_text, search_results, conversation_history
        )
        generation_time = time.time() - generation_start
        total_time = time.time() - start_time
        
        # Calculate overall relevance score
        overall_relevance = 0.0
        if search_results:
            overall_relevance = sum(r.get("relevance_score", 0) for r in search_results) / len(search_results)
        
        # Prepare sources information
        sources = []
        for result in search_results[:5]:  # Top 5 sources
            source_info = {
                "collection": result.get("collection", ""),
                "relevance_score": result.get("relevance_score", 0.0),
                "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "context_type": result.get("context_type", "")
            }
            sources.append(source_info)
        
        # Create response object
        rag_response = RAGResponse(
            query_id=query_id,
            query=query_text,
            response=response_text,
            relevance_score=overall_relevance,
            sources=sources,
            processing_time=total_time,
            metadata={
                "query_analysis": query_analysis,
                "search_time": search_time,
                "generation_time": generation_time,
                "num_sources": len(search_results)
            }
        )
        
        return rag_response
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        
        status = {
            "system_initialized": self.is_initialized,
            "initialization_time": self.initialization_time
        }
        
        # Add component status
        if hasattr(self, 'search_engine'):
            status["search_engine"] = {
                "collections_loaded": len(self.search_engine.collections),
                "reranker_fitted": getattr(self.search_engine.reranker, 'is_fitted', False),
                "total_documents": sum(
                    collection.count() 
                    for collection in self.search_engine.collections.values()
                ) if self.search_engine.collections else 0
            }
        
        return status

# Factory function for easy initialization
def create_rag_system(api_key: Optional[str] = None) -> OptimizedRAGSystem:
    """
    Factory function to create optimized RAG system
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Configured OptimizedRAGSystem instance
    """
    
    # Create and return system
    return OptimizedRAGSystem(api_key=api_key)

# CLI interface for system management
def main():
    """Main CLI interface for the RAG system"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Optimized RAG System CLI")
    parser.add_argument("--init-db", action="store_true",
                       help="Initialize ChromaDB")
    parser.add_argument("--reset-db", action="store_true", 
                       help="Reset ChromaDB collections")
    parser.add_argument("--query", type=str,
                       help="Process a single query")
    parser.add_argument("--status", action="store_true",
                       help="Show system status")
    
    args = parser.parse_args()
    
    # Create system
    try:
        system = create_rag_system()
        print("RAG System created successfully")
        
    except Exception as e:
        print(f"Error creating RAG system: {e}")
        sys.exit(1)
    
    # Initialize database if requested
    if args.init_db or args.reset_db:
        try:
            print("Initializing database...")
            stats = system.initialize_database(reset_collections=args.reset_db)
            print(f"Database initialization completed: {stats}")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)
    
    # Show status if requested
    if args.status:
        try:
            status = system.get_system_status()
        except Exception as e:
            print(f"Error getting system status: {e}")
    
    # Process single query if provided
    if args.query:
        try:
            if not system.is_initialized:
                print("System not initialized. Run with --init-db first.")
                sys.exit(1)
                
            print(f"Processing query: {args.query}")
            response = system.query(args.query)
            
            print("\nResponse:")
            print("-" * 50)
            print(response.response)
            print("-" * 50)
            print(f"Relevance Score: {response.relevance_score:.3f}")
            print(f"Processing Time: {response.processing_time:.3f}s")
            print(f"Sources Used: {len(response.sources)}")
            
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()

# Export main classes and functions
__all__ = [
    "OptimizedRAGSystem",
    "RAGResponse", 
    "create_rag_system"
]