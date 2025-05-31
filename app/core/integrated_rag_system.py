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
from .rag_monitoring import (
    RAGMonitor, track_query, track_component_operation, create_monitoring_setup
)

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
    
    def __init__(self, 
                
                 enable_monitoring: bool = True,
                 api_key: Optional[str] = None):
        """
        Initialize the optimized RAG system
        
        Args:
            enable_monitoring: Whether to enable performance monitoring
            api_key: OpenAI API key
        """
  
        # Setup monitoring
        self.monitoring_enabled = enable_monitoring
        if self.monitoring_enabled:
            self.monitor = create_monitoring_setup("logs/rag_system.log")
        else:
            self.monitor = None
        
        # API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize components
        self._initialize_components()
        
        # System state
        self.is_initialized = False
        self.initialization_time = 0.0
        
        # Performance cache
        self._query_cache = {}
        self._cache_enabled = self.config.performance.enable_query_caching
        self._cache_ttl = self.config.performance.cache_ttl_seconds
        
        logging.info("OptimizedRAGSystem initialized successfully")
    
    def _initialize_components(self):
        """Initialize core components with configuration"""
        
        try:
            # Initialize semantic search with configuration
            self.search_engine = SemanticSearch(
                api_key=self.api_key,
                chroma_path="./chroma_db"
            )
            
            # Apply search configuration
            search_config = self.config.get_search_strategy_config("balanced")
            self.search_engine.max_results_per_collection = search_config["max_results_per_collection"]
            self.search_engine.final_top_k = search_config["final_top_k"]
            self.search_engine.collection_authority = search_config["collection_weights"]
            
            # Initialize response generator with configuration
            self.response_generator = ResponseGenerator(api_key=self.api_key)
            
            # Apply context configuration
            context_config = self.config.get_context_optimization_config(self.config.context.max_context_tokens)
            self.response_generator.context_optimizer.max_context_tokens = context_config["max_context_tokens"]
            
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
        
        # Check cache if enabled
        if self._cache_enabled:
            cache_key = self._generate_cache_key(query_text, conversation_history)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logging.info(f"Cache hit for query: {query_text[:50]}...")
                return cached_response
        
        # Start monitoring if enabled
        if self.monitoring_enabled:
            monitor_context = track_query(self.monitor, query_text)
        else:
            monitor_context = None
        
        try:
            with monitor_context if monitor_context else self._null_context():
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
                              conversation_history: Optional[List[Tuple[str, str]]],
                              user_context: Optional[Dict[str, Any]]) -> RAGResponse:
        """Internal query processing with detailed monitoring"""
        
        start_time = time.time()
        
        # Analyze query for optimization
        query_analysis = self.search_engine.query_analyzer.analyze_query(query_text)
        
        # Step 1: Search for relevant documents
        search_start = time.time()
        
        if self.monitoring_enabled:
            with track_component_operation(self.monitor, "search", "search", {"query_complexity": query_analysis.get("complexity")}):
                search_results = self.search_engine.search(
                    query_text, 
                    top_k=self.config.search.final_top_k
                )
        else:
            search_results = self.search_engine.search(
                query_text,
                top_k=self.config.search.final_top_k
            )
        
        search_time = time.time() - search_start
        
        # Update search metrics
        if self.monitoring_enabled and search_results:
            avg_relevance = sum(r.get("relevance_score", 0) for r in search_results) / len(search_results)
            collections_searched = list(set(r.get("collection", "") for r in search_results))
            
            self.monitor.update_search_metrics(
                query_id, search_time, len(search_results), avg_relevance, collections_searched
            )
        
        # Step 2: Generate response with optimized context
        generation_start = time.time()
        
        if self.monitoring_enabled:
            with track_component_operation(self.monitor, "generation", "generation", {"model": self.config.prompt.default_model}):
                response_text = self.response_generator.generate_response(
                    query_text, search_results, conversation_history
                )
        else:
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
        
        # Update generation metrics
        if self.monitoring_enabled:
            self.monitor.update_generation_metrics(
                query_id,
                generation_time,
                len(response_text),
                self.response_generator.count_tokens(response_text),
                self.config.prompt.default_model,
                self.config.prompt.explanation_temperature
            )
            
            self.monitor.update_quality_metrics(
                query_id,
                query_analysis.get("complexity", "unknown"),
                query_analysis.get("intents", []),
                len(response_text) > 20  # Basic validation
            )
        
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
                "num_sources": len(search_results),
                "config_preset": getattr(self.config, 'preset', 'custom')
            }
        )
        
        # Cache response if enabled
        if self._cache_enabled:
            cache_key = self._generate_cache_key(query_text, conversation_history)
            self._cache_response(cache_key, rag_response)
        
        return rag_response
    
    def _generate_cache_key(self, query: str, history: Optional[List[Tuple[str, str]]]) -> str:
        """Generate cache key for query and history"""
        import hashlib
        
        # Include query and recent history in cache key
        cache_input = query
        if history:
            # Include last 2 turns of history
            recent_history = history[-2:] if len(history) > 2 else history
            cache_input += "|".join(f"{q}:{r[:100]}" for q, r in recent_history)
        
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[RAGResponse]:
        """Get cached response if available and not expired"""
        if cache_key not in self._query_cache:
            return None
        
        cached_data = self._query_cache[cache_key]
        if time.time() - cached_data["timestamp"] > self._cache_ttl:
            del self._query_cache[cache_key]
            return None
        
        return cached_data["response"]
    
    def _cache_response(self, cache_key: str, response: RAGResponse):
        """Cache response with timestamp"""
        self._query_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Clean old cache entries if too many
        if len(self._query_cache) > self.config.performance.max_cache_entries:
            # Remove oldest entries
            sorted_items = sorted(
                self._query_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            
            # Keep newest 80% of entries
            keep_count = int(self.config.performance.max_cache_entries * 0.8)
            for key, _ in sorted_items[:-keep_count]:
                del self._query_cache[key]
    
    def _null_context(self):
        """Null context manager for when monitoring is disabled"""
        class NullContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return NullContext()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        
        status = {
            "system_initialized": self.is_initialized,
            "initialization_time": self.initialization_time,
            "config_environment": self.config.environment,
            "monitoring_enabled": self.monitoring_enabled,
            "cache_enabled": self._cache_enabled,
            "cache_entries": len(self._query_cache) if self._cache_enabled else 0
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
        
        # Add monitoring data if available
        if self.monitoring_enabled and self.monitor:
            status["monitoring"] = self.monitor.get_real_time_dashboard_data()
        
        return status
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        if not self.monitoring_enabled:
            return {"error": "Monitoring not enabled"}
        
        return self.monitor.generate_performance_report(hours)
    
    def optimize_for_workload(self, workload_type: str):
        """Optimize system configuration for specific workload types"""
        
        optimization_configs = {
            "high_throughput": {
                "search": {
                    "max_results_per_collection": 25,
                    "final_top_k": 8,
                    "enable_hybrid_rerank": True  # Faster but less accurate
                },
                "context": {
                    "max_context_tokens": 10000,
                    "enable_context_optimization": True
                },
                "performance": {
                    "batch_size": 100,
                    "enable_query_caching": True
                }
            },
            
            "high_accuracy": {
                "search": {
                    "max_results_per_collection": 75,
                    "final_top_k": 20,
                    "enable_hybrid_rerank": True
                },
                "context": {
                    "max_context_tokens": 16000,
                    "enable_context_optimization": True
                }
            },
            
            "memory_optimized": {
                "search": {
                    "max_results_per_collection": 20,
                    "final_top_k": 5
                },
                "context": {
                    "max_context_tokens": 8000
                },
                "performance": {
                    "batch_size": 25,
                    "max_cache_entries": 100
                }
            }
        }
        
        if workload_type not in optimization_configs:
            raise ValueError(f"Unknown workload type: {workload_type}")
        
        # Apply optimizations
        optimization = optimization_configs[workload_type]
        
        # Update search engine configuration
        if "search" in optimization:
            search_config = optimization["search"]
            for key, value in search_config.items():
                if hasattr(self.search_engine, key):
                    setattr(self.search_engine, key, value)
        
        # Update response generator configuration  
        if "context" in optimization:
            context_config = optimization["context"]
            for key, value in context_config.items():
                if hasattr(self.response_generator.context_optimizer, key):
                    setattr(self.response_generator.context_optimizer, key, value)
        
        # Update performance configuration
        if "performance" in optimization:
            perf_config = optimization["performance"]
            for key, value in perf_config.items():
                if key == "max_cache_entries":
                    self.config.performance.max_cache_entries = value
                elif key == "enable_query_caching":
                    self._cache_enabled = value
        
        logging.info(f"System optimized for {workload_type} workload")

# Factory function for easy initialization
def create_rag_system(preset: str = "balanced",
                     environment: str = "development", 
                     enable_monitoring: bool = True,
                     api_key: Optional[str] = None,
                     custom_config: Optional[Dict[str, Any]] = None) -> OptimizedRAGSystem:
    """
    Factory function to create optimized RAG system
    
    Args:
        preset: Configuration preset (balanced, high_performance, high_accuracy, development)
        environment: Environment (development, production, testing)
        enable_monitoring: Whether to enable performance monitoring
        api_key: OpenAI API key
        custom_config: Custom configuration overrides
        
    Returns:
        Configured OptimizedRAGSystem instance
    """
    
    # Load configuration with preset and custom overrides
    config = load_config(
        preset=preset,
        environment=environment,
        custom_overrides=custom_config
    )
    
    # Create and return system
    return OptimizedRAGSystem(
        config=config,
        enable_monitoring=enable_monitoring,
        api_key=api_key
    )

# Usage example and testing utilities
def run_system_benchmark(system: OptimizedRAGSystem, 
                        test_queries: List[str],
                        iterations: int = 1) -> Dict[str, Any]:
    """
    Run benchmark tests on the RAG system
    
    Args:
        system: RAG system instance
        test_queries: List of test queries
        iterations: Number of iterations per query
        
    Returns:
        Benchmark results
    """
    
    if not system.is_initialized:
        raise RuntimeError("System must be initialized before benchmarking")
    
    results = {
        "benchmark_start": time.time(),
        "test_queries": len(test_queries),
        "iterations": iterations,
        "query_results": [],
        "aggregate_metrics": {}
    }
    
    all_response_times = []
    all_relevance_scores = []
    successful_queries = 0
    
    logging.info(f"Starting benchmark with {len(test_queries)} queries, {iterations} iterations each")
    
    for query_idx, query in enumerate(test_queries):
        query_metrics = {
            "query": query,
            "query_index": query_idx,
            "iterations": [],
            "avg_response_time": 0.0,
            "avg_relevance_score": 0.0,
            "success_rate": 0.0
        }
        
        iteration_times = []
        iteration_relevances = []
        iteration_successes = []
        
        for iteration in range(iterations):
            try:
                start_time = time.time()
                response = system.query(query)
                end_time = time.time()
                
                response_time = end_time - start_time
                iteration_times.append(response_time)
                iteration_relevances.append(response.relevance_score)
                iteration_successes.append(1 if len(response.response) > 20 else 0)
                
                all_response_times.append(response_time)
                all_relevance_scores.append(response.relevance_score)
                
                if len(response.response) > 20:
                    successful_queries += 1
                
                iteration_result = {
                    "iteration": iteration,
                    "response_time": response_time,
                    "relevance_score": response.relevance_score,
                    "response_length": len(response.response),
                    "num_sources": len(response.sources),
                    "success": len(response.response) > 20
                }
                
                query_metrics["iterations"].append(iteration_result)
                
            except Exception as e:
                logging.error(f"Benchmark query {query_idx}, iteration {iteration} failed: {e}")
                iteration_successes.append(0)
                
                query_metrics["iterations"].append({
                    "iteration": iteration,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate query-level metrics
        if iteration_times:
            query_metrics["avg_response_time"] = sum(iteration_times) / len(iteration_times)
            query_metrics["min_response_time"] = min(iteration_times)
            query_metrics["max_response_time"] = max(iteration_times)
        
        if iteration_relevances:
            query_metrics["avg_relevance_score"] = sum(iteration_relevances) / len(iteration_relevances)
        
        query_metrics["success_rate"] = sum(iteration_successes) / len(iteration_successes) * 100
        
        results["query_results"].append(query_metrics)
        
        logging.info(f"Query {query_idx + 1}/{len(test_queries)} completed - "
                    f"Avg time: {query_metrics['avg_response_time']:.3f}s, "
                    f"Success rate: {query_metrics['success_rate']:.1f}%")
    
    # Calculate aggregate metrics
    if all_response_times:
        results["aggregate_metrics"] = {
            "total_queries_tested": len(test_queries) * iterations,
            "successful_queries": successful_queries,
            "overall_success_rate": (successful_queries / (len(test_queries) * iterations)) * 100,
            "avg_response_time": sum(all_response_times) / len(all_response_times),
            "min_response_time": min(all_response_times),
            "max_response_time": max(all_response_times),
            "p95_response_time": sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0,
            "avg_relevance_score": sum(all_relevance_scores) / len(all_relevance_scores) if all_relevance_scores else 0,
            "benchmark_duration": time.time() - results["benchmark_start"]
        }
    
    logging.info(f"Benchmark completed: {results['aggregate_metrics']}")
    return results

def create_test_queries() -> List[str]:
    """Create a set of test queries for benchmarking"""
    return [
        "Como criar um relatório de funcionários usando BFC-Script?",
        "Quais são os campos disponíveis na fonte Dados.pessoal.v2.funcionario?",
        "Exemplo de código para buscar rubricas de um funcionário específico",
        "Como filtrar funcionários por departamento usando expressões?",
        "Quais enums estão disponíveis para classificação de funcionários?",
        "Criar script para calcular folha de pagamento",
        "Como acessar dados históricos de um funcionário?",
        "Implementar busca de funcionários por cargo",
        "Exemplo de uso da fonte Dados.folha.v2 para eventos",
        "Como fazer ordenação de resultados por nome do funcionário?"
    ]

# CLI interface for system management
def main():
    """Main CLI interface for the RAG system"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Optimized RAG System CLI")
    parser.add_argument("--preset", default="balanced", 
                       choices=["balanced", "high_performance", "high_accuracy", "development"],
                       help="Configuration preset")
    parser.add_argument("--environment", default="development",
                       choices=["development", "production", "testing"],
                       help="Environment configuration")
    parser.add_argument("--init-db", action="store_true",
                       help="Initialize ChromaDB")
    parser.add_argument("--reset-db", action="store_true", 
                       help="Reset ChromaDB collections")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run system benchmark")
    parser.add_argument("--query", type=str,
                       help="Process a single query")
    parser.add_argument("--status", action="store_true",
                       help="Show system status")
    parser.add_argument("--report", type=int, metavar="HOURS", default=24,
                       help="Generate performance report for last N hours")
    parser.add_argument("--optimize", type=str,
                       choices=["high_throughput", "high_accuracy", "memory_optimized"],
                       help="Optimize for specific workload")
    parser.add_argument("--no-monitoring", action="store_true",
                       help="Disable performance monitoring")
    
    args = parser.parse_args()
    
    # Create system
    try:
        system = create_rag_system(
            preset=args.preset,
            environment=args.environment,
            enable_monitoring=not args.no_monitoring
        )
        print(f"RAG System created with preset: {args.preset}, environment: {args.environment}")
        
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
    
    # Apply optimization if requested
    if args.optimize:
        try:
            system.optimize_for_workload(args.optimize)
            print(f"System optimized for {args.optimize} workload")
        except Exception as e:
            print(f"Error applying optimization: {e}")
    
    # Show status if requested
    if args.status:
        try:
            status = system.get_system_status()
        except Exception as e:
            print(f"Error getting system status: {e}")
    
    # Generate report if requested
    if args.report and not args.query and not args.benchmark:
        try:
            if not system.monitoring_enabled:
                print("Monitoring not enabled, cannot generate report")
            else:
                report = system.generate_performance_report(args.report)
                print(f"Performance Report (last {args.report} hours):")
                print(json.dumps(report, indent=2))
        except Exception as e:
            print(f"Error generating report: {e}")
    
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
    
    # Run benchmark if requested
    if args.benchmark:
        try:
            if not system.is_initialized:
                print("System not initialized. Run with --init-db first.")
                sys.exit(1)
                
            print("Running system benchmark...")
            test_queries = create_test_queries()
            benchmark_results = run_system_benchmark(system, test_queries, iterations=2)
            
            print("\nBenchmark Results:")
            print("-" * 50)
            metrics = benchmark_results["aggregate_metrics"]
            print(f"Total Queries: {metrics['total_queries_tested']}")
            print(f"Success Rate: {metrics['overall_success_rate']:.1f}%")
            print(f"Average Response Time: {metrics['avg_response_time']:.3f}s")
            print(f"P95 Response Time: {metrics['p95_response_time']:.3f}s")
            print(f"Average Relevance Score: {metrics['avg_relevance_score']:.3f}")
            print(f"Benchmark Duration: {metrics['benchmark_duration']:.1f}s")
            
        except Exception as e:
            print(f"Error running benchmark: {e}")

if __name__ == "__main__":
    main()

# Export main classes and functions
__all__ = [
    "OptimizedRAGSystem",
    "RAGResponse", 
    "create_rag_system",
    "run_system_benchmark",
    "create_test_queries"
]