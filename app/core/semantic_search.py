# app/core/semantic_search.py
import os
import time
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
import re
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging #, is_dev_mode, log_debug, log_function_call, log_function_return # Assuming these are not strictly needed for this modification snippet
# import gradio as gr # Gradio UI parts are not directly modified by the request

# Configure logging
logger = setup_logging(__name__, "logs/semantic_search.log")

# Moved BasicQueryAnalyzer here
class BasicQueryAnalyzer:
    """Analyzes the query to understand intents and expected output format."""
    def analyze_query(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        analysis = {
            "intents": [],
            "expected_output": "explanation",
            "complexity": "simple" # Default complexity
        }
        
        # Detect intents and expected output
        if any(term in query_lower for term in ["código", "script", "implementa", "implementar", "criar", "exemplo", "função"]): # Added "função"
            analysis["intents"].append("code_request")
            analysis["expected_output"] = "code"
        
        if any(term in query_lower for term in ["campos", "types", "propriedades", "definição de campo"]): # Added "definição de campo"
            analysis["intents"].append("field_query")
            analysis["expected_output"] = "structured_list"
        
        if any(term in query_lower for term in ["enum", "enums", "classificação", "tipos de"]):
            analysis["intents"].append("enum_query")
            analysis["expected_output"] = "structured_list"
        
        if any(term in query_lower for term in ["relatório", "report"]):
            analysis["intents"].append("report_query")
            analysis["expected_output"] = "code" # Reports often involve code/scripts
        
        if any(term in query_lower for term in ["fonte de dados", "dados.", "fonte"]):
            analysis["intents"].append("data_source_query")

        # Basic complexity assessment (can be expanded)
        if len(query_lower.split()) > 10 or "como funciona" in query_lower or "detalhes sobre" in query_lower:
            analysis["complexity"] = "complex"
            
        # Ensure "code_request" is present if "report_query" is, as reports imply code
        if "report_query" in analysis["intents"] and "code_request" not in analysis["intents"]:
            analysis["intents"].append("code_request")

        # Remove duplicate intents
        analysis["intents"] = list(set(analysis["intents"]))

        logger.info(f"Query analysis result: {analysis}")
        return analysis

class SemanticSearch:
    def __init__(self, api_key=None, chroma_path="./chroma_db"):
        """
        Initialize SemanticSearch with OpenAI API key and ChromaDB client.
        
        Args:
            api_key: OpenAI API key
            chroma_path: Path to ChromaDB
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.chroma_path = chroma_path
        
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        self._load_collections()
        self._initialize_reranker()
        self._initialize_query_analyzer() # Now initializes BasicQueryAnalyzer
        
        self.max_results_per_collection = 10 
        self.min_relevance_score = 0.0  # Keep this to allow lower scores to be considered by reranker
        
        self.collection_weights = {
            "docs": 0.7,
            "enums": 0.7,
            "folha": 1.0,
            "pessoal": 1.0
        }
        
        # Domain patterns (can be used by query_analyzer if it's enhanced further, or for other purposes)
        self.domain_patterns = {
            "fonte_de_dados": [r"fonte\s+de\s+dados", r"Dados\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+", r"fonte"],
            "codigo_exemplo": [r"exemplo", r"código", r"script", r"criar", r"implementar", r"code example"],
            "filtros": [r"filtro", r"condição", r"types", r"expressions"],
            "campo": [r"campo", r"atributo", r"propriedade", r"field", r"Campos"],
            "enum": [r"enum", r"classificacao", r"tipo"]
        }
        
        self.source_type_weights = { # These seem specific and could be part of a more advanced reranking or boosting
            "folha": 1.2,
            "pessoal": 1.2,
            "historico": 0.8,
            "relatorio": 0.8
        }
    
    def _load_collections(self):
        try:
            collections_list = self.chroma_client.list_collections()
            self.collections = {}
            for collection_obj in collections_list:
                collection_name = collection_obj.name
                self.collections[collection_name] = self.chroma_client.get_collection(collection_name)
                count = self.collections[collection_name].count()
                logger.info(f"Loaded collection: {collection_name} with {count} documents")
            logger.info(f"Loaded {len(self.collections)} collections")
        except Exception as e:
            logger.error(f"Error loading collections: {str(e)}")
            self.collections = {}

    # enhance_query method is removed
    
    def detect_content_type(self, query: str) -> Dict[str, float]:
        """
        Detect the type of content potentially relevant to the query to adjust collection search preference.
        Args:
            query: User query
        Returns:
            Dictionary of collection preference weights
        """
        query_lower = query.lower()
        weights = self.collection_weights.copy() # Start with base weights
        
        # Adjust weights based on query content indicating preference for code/data examples
        if any(term in query_lower for term in ["código", "script", "busca", "implementar", "criar", "relatório"]):
            weights["folha"] = weights.get("folha", 1.0) * 1.1  # Boost for code-heavy collections
            weights["pessoal"] = weights.get("pessoal", 1.0) * 1.1
            weights["enums"] = weights.get("enums", 0.7) * 0.9 # Slightly deprioritize if focused on code
            weights["docs"] = weights.get("docs", 0.7) * 0.8   # Deprioritize general docs if code is likely needed
            
        elif any(term in query_lower for term in ["enum", "enums", "tipo"]): # Enum specific
            weights["enums"] = weights.get("enums", 0.7) * 1.2
            weights["docs"] = weights.get("docs", 0.7) * 0.9
            weights["folha"] = weights.get("folha", 1.0) * 0.8
            weights["pessoal"] = weights.get("pessoal", 1.0) * 0.8
            
        elif any(term in query_lower for term in ["documentação", "conceito", "o que é", "explica"]): # Documentation focus
            weights["docs"] = weights.get("docs", 0.7) * 1.2
            weights["enums"] = weights.get("enums", 0.7) * 0.9
            weights["folha"] = weights.get("folha", 1.0) * 0.7
            weights["pessoal"] = weights.get("pessoal", 1.0) * 0.7
        
        # Source-specific keywords can also fine-tune preferences
        if "folha" in query_lower and "pessoal" not in query_lower: # Explicitly mentions "folha"
            weights["folha"] = weights.get("folha", 1.0) * self.source_type_weights.get("folha", 1.2)
            weights["pessoal"] = weights.get("pessoal", 1.0) * 0.6 # Deprioritize other if one is specified
        elif "pessoal" in query_lower and "folha" not in query_lower: # Explicitly mentions "pessoal"
            weights["pessoal"] = weights.get("pessoal", 1.0) * self.source_type_weights.get("pessoal", 1.2)
            weights["folha"] = weights.get("folha", 1.0) * 0.6
            
        logger.info(f"Content type detection weights: {weights}")
        return weights
    
    def get_embedding(self, text: str) -> List[float]:
        try:
            max_tokens_for_embedding = 8000 # OpenAI's limit for some models, ensure text fits
            if len(text) > max_tokens_for_embedding: # Simple character count, not exact tokens
                text = text[:max_tokens_for_embedding]
                logger.warning(f"Text truncated to {max_tokens_for_embedding} characters for embedding")
            
            response = self.client.embeddings.create(
                model="text-embedding-3-small", # Ensure this matches your embedding generation
                input=text,
                dimensions=512 
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding of length {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Fallback to a random embedding if API fails, though this is not ideal
            return np.random.rand(512).tolist() 
    
    def search_collection(self, collection_name: str, query_embedding: List[float], 
                         collection_preference_weights: Dict[str, float], top_k_initial: int = 100) -> List[Dict]:
        collection = self.collections.get(collection_name)
        if not collection:
            logger.warning(f"Collection {collection_name} not available for search.")
            return []
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k_initial, # Fetch more initially for reranking
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            if results and results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    # Base relevance from cosine distance (0=identical, 1=orthogonal, 2=opposite)
                    # Score: 1 for identical, 0.5 for orthogonal, 0 for opposite
                    base_relevance_score = 1.0 - (distance / 2.0)
                    
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    
                    current_score = base_relevance_score
                    
                    # Apply content-specific boosts (multiplicative)
                    content_boost_factor = 1.0
                    if "Code Example:" in content or "```" in content:
                        content_boost_factor *= 1.45  # Boost for code examples
                    if any(ds_mention in content for ds_mention in ["Dados.folha", "Dados.pessoal"]):
                        content_boost_factor *= 1.3   # Boost for data source references
                    current_score *= content_boost_factor

                    # Apply collection preference weight
                    collection_pref = collection_preference_weights.get(collection_name, 1.0) # Default to 1.0 if not specified
                    current_score *= collection_pref
                    
                    # Cap the relevance score to a max of 1.0 for easier interpretation downstream
                    # This ensures boosts enhance ranking but don't push scores beyond a "perfect match" concept.
                    final_relevance_score = min(current_score, 1.0) 
                                        
                    formatted_results.append({
                        "content": content,
                        "metadata": metadata,
                        "distance": distance, # Original distance for reference
                        "collection": collection_name,
                        "relevance_score": final_relevance_score, # Capped score
                        "has_code_example": "Code Example:" in content or "```" in content
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching in collection {collection_name}: {str(e)}")
            return []
    
    def rerank_results(self, results: List[Dict], query: str, query_analysis: Dict[str, Any]) -> List[Dict]:
        if not results:
            return []
        
        # Use query_analysis intents for more targeted reranking
        intents = query_analysis.get("intents", [])
        expected_output = query_analysis.get("expected_output", "explanation")

        for result in results:
            # Start with the relevance score from search_collection (already capped at 1.0)
            score = result["relevance_score"] 
            content_lower = result["content"].lower()
            
            boost_factor = 1.0
            if ("code_request" in intents or expected_output == "code") and result.get("has_code_example", False):
                boost_factor *= 1.3  # Prioritize code examples if code is expected/requested
            
            if "data_source_query" in intents and any(term in content_lower for term in ["fonte", "dados."]):
                boost_factor *= 1.25 # Prioritize docs mentioning data sources
                
            if "field_query" in intents and any(term in content_lower for term in ["fields:", "campos:", "propriedades:"]):
                boost_factor *= 1.2  # Prioritize field definitions
            
            if "enum_query" in intents and result.get("collection") == "enums": # Specific boost for enums collection if enums are queried
                 boost_factor *= 1.15

            result["relevance_score"] = min(score * boost_factor, 1.0) # Apply boost and re-cap at 1.0

        results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        return results
        
    def merge_and_rank_results(self, results_by_collection: Dict[str, List[Dict]], query: str, query_analysis: Dict[str, Any], top_k: int = 10) -> List[Dict]:
        all_results = []
        for res_list in results_by_collection.values():
            all_results.extend(res_list)
        
        # Initial sort before reranking (optional, but good if scores are already somewhat comparable)
        all_results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        
        # Rerank based on deeper query understanding
        reranked_results = self.rerank_results(all_results, query, query_analysis)
        
        return reranked_results[:top_k] # Return the final top_k results
    
    def search(self, query: str, query_analysis: Dict[str, Any], top_k: int = 10) -> List[Dict]:
        """
        Perform semantic search across all collections.
        Now takes query_analysis as an argument.
        """
        try:
            # Query enhancement is removed. Original query is used.
            
            # Detect content type preferences to adjust collection search
            collection_preference_weights = self.detect_content_type(query) # Based on original query
            
            query_embedding = self.get_embedding(query) # Embedding of original query
            
            results_by_collection = {}
            for collection_name in self.collections:
                if self.collections[collection_name]: # Check if collection loaded properly
                    collection_results = self.search_collection(
                        collection_name, 
                        query_embedding,
                        collection_preference_weights, # Pass preferences
                        top_k_initial=self.max_results_per_collection # Fetch more for better reranking pool
                    )
                    results_by_collection[collection_name] = collection_results
            
            # Merge and rank results, now also passing query_analysis for smarter reranking
            merged_results = self.merge_and_rank_results(results_by_collection, query, query_analysis, top_k)
            
            # Add original query metadata to each result for context
            for result in merged_results:
                result["query_debug_original"] = query # Keep track of the original query for this result set
                
            logger.info(f"Found {len(merged_results)} results for query: '{query}' after merging and reranking.")
            return merged_results
            
        except Exception as e:
            logger.error(f"Error in main search process: {str(e)}")
            return []

    def _initialize_reranker(self):
        """Initialize the reranker component (currently conceptual)."""
        self.reranker_config = { # Changed to reranker_config to avoid confusion with a callable reranker
            "is_fitted": True, 
            "type": "heuristic_boost" # Reflects current rerank_results logic
        }
        logger.info("Reranker (heuristic boosting) initialized successfully")

    def _initialize_query_analyzer(self):
        """Initialize the BasicQueryAnalyzer."""
        try:
            self.query_analyzer = BasicQueryAnalyzer() # Instantiate the analyzer
            logger.info("BasicQueryAnalyzer initialized successfully in SemanticSearch")
        except Exception as e:
            logger.error(f"Error initializing BasicQueryAnalyzer in SemanticSearch: {str(e)}")
            # Fallback or error state for query_analyzer
            self.query_analyzer = None # Or a dummy analyzer that returns default analysis

    # get_document_context and create_interface remain but are not directly modified by this request's core logic
    # They would consume the results from the modified search pipeline.
    def get_document_context(self, query: str, query_analysis: Dict[str, Any], top_k: int = 10) -> Tuple[str, List[Dict]]:
        try:
            results = self.search(query, query_analysis, top_k) # Pass query_analysis
            # ... rest of the method for building context string based on results
            # This part would benefit from using the 'query_analysis' too, e.g., to prioritize code examples in context string
            if not results:
                logger.warning(f"No results found for query: {query}")
                return "", []
            
            # Simplified context building for brevity
            context_parts = []
            expected_output = query_analysis.get("expected_output")
            
            if expected_output == "code" and any(r.get("has_code_example") for r in results):
                context_parts.append("## Exemplos de Código Relevantes\n")
                for r in results:
                    if r.get("has_code_example"):
                         context_parts.append(f"[Score: {r['relevance_score']:.2f}, Fonte: {r['collection']}]\n{r['content']}\n")
            
            context_parts.append("## Contexto Adicional\n")
            for r in results:
                # Avoid duplicating if already shown as code example, or show non-code part
                if not (expected_output == "code" and r.get("has_code_example")):
                    context_parts.append(f"[Score: {r['relevance_score']:.2f}, Fonte: {r['collection']}]\n{r['content']}\n")

            context_str = "\n".join(context_parts)
            logger.info(f"Generated context with {len(results)} results, {len(context_str)} chars for query: {query}")
            return context_str, results

        except Exception as e:
            logger.error(f"Error getting document context: {str(e)}")
            return "", []
