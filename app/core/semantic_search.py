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
from .config import setup_logging

logger = setup_logging(__name__, "logs/semantic_search.log")

class BasicQueryAnalyzer:
    """Analyzes the query to understand intents and expected output format."""
    def analyze_query(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        analysis = {
            "intents": [],
            "expected_output": "explanation",
            "complexity": "simple"
        }
        
        if any(term in query_lower for term in ["código", "script", "implementa", "implementar", "criar", "exemplo", "função"]):
            analysis["intents"].append("code_request")
            analysis["expected_output"] = "code"
        
        if any(term in query_lower for term in ["campos", "types", "propriedades", "definição de campo"]):
            analysis["intents"].append("field_query")
            analysis["expected_output"] = "structured_list"
        
        if any(term in query_lower for term in ["enum", "enums", "classificação", "tipos de"]):
            analysis["intents"].append("enum_query")
            analysis["expected_output"] = "structured_list"
        
        if any(term in query_lower for term in ["relatório", "report"]):
            analysis["intents"].append("report_query")
            analysis["expected_output"] = "code" 
        
        if any(term in query_lower for term in ["fonte de dados", "dados.", "fonte"]):
            analysis["intents"].append("data_source_query")

        if len(query_lower.split()) > 10 or "como funciona" in query_lower or "detalhes sobre" in query_lower:
            analysis["complexity"] = "complex"
            
        if "report_query" in analysis["intents"] and "code_request" not in analysis["intents"]:
            analysis["intents"].append("code_request")

        analysis["intents"] = list(set(analysis["intents"]))
        logger.info(f"Query analysis result: {analysis}")
        return analysis

class SemanticSearch:
    def __init__(self, api_key=None, chroma_path="./chroma_db"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.chroma_path = chroma_path
        
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self._load_collections()
        self._initialize_reranker()
        self._initialize_query_analyzer()
        
        self.max_results_per_collection = 100 
        self.min_relevance_score = 0.1
    
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
    
    def get_embedding(self, text: str) -> List[float]:
        try:
            max_tokens_for_embedding = 8000 
            if len(text) > max_tokens_for_embedding:
                text = text[:max_tokens_for_embedding]
                logger.warning(f"Text truncated to {max_tokens_for_embedding} characters for embedding")
            
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=512 
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding of length {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return np.random.rand(512).tolist() 
    
    def search_collection(self, collection_name: str, query_embedding: List[float], 
                         top_k_initial: int = 100) -> List[Dict]:
        collection = self.collections.get(collection_name)
        if not collection:
            logger.warning(f"Collection {collection_name} not available for search.")
            return []
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k_initial,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            if results and results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    # Score is based purely on distance
                    current_score = 1.0 - (distance / 2.0) 
                    
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    
                    if current_score < self.min_relevance_score:
                        continue
                    
                    final_relevance_score = min(current_score, 1.0)
                    
                    formatted_results.append({
                        "content": content,
                        "metadata": metadata,
                        "distance": distance,
                        "collection": collection_name,
                        "relevance_score": final_relevance_score,
                        "has_code_example": "Code Example:" in content or "```" in content,
                        "has_field_definition": "Types:" in content or "Fields:" in content,
                        "has_method_description": "Method:" in content or "Description:" in content
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching in collection {collection_name}: {str(e)}")
            return []
    
    def rerank_results(self, results: List[Dict], query: str, query_analysis: Dict[str, Any]) -> List[Dict]:
        if not results:
            return []
        
        # Simple sort by relevance score
        results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        
        # Remove duplicates
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content_hash = hash(result["content"])
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results
        
    def merge_and_rank_results(self, results_by_collection: Dict[str, List[Dict]], query: str, query_analysis: Dict[str, Any], top_k: int = 5) -> List[Dict]:
        all_results = []
        for res_list in results_by_collection.values():
            all_results.extend(res_list)
        
        # ================== IMPLEMENTAÇÃO DA CORREÇÃO ==================
        # Normaliza a query substituindo espaços por underscores para corresponder ao formato do título.
        query_normalized_for_title_check = query.lower().replace(" ", "_")

        for result in all_results:
            title = result.get("metadata", {}).get("title", "")
            if title and title.lower() in query_normalized_for_title_check:
                result["relevance_score"] = result.get("relevance_score", 0.0) + 1.0
                logging.info(f"Score impulsionado para o título correspondente: '{title}'")
        # ================== FIM DA CORREÇÃO ==================

        # Ordena os resultados com base no score (que agora pode estar impulsionado)
        all_results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        
        # Pega os resultados iniciais do topo para encontrar chunks relacionados
        initial_top_results = all_results[:top_k]
        
        related_chunks = set()
        for result in initial_top_results:
            metadata = result.get("metadata", {})
            chunk_key = metadata.get("chunk_key", "")
            
            # Extrai a chave base do chunk para agrupar todas as suas partes
            base_key = re.sub(r'_part\d+_\d+$', '', chunk_key)
            
            # Encontra todos os chunks relacionados nos resultados
            for other_result in all_results:
                other_metadata = other_result.get("metadata", {})
                other_chunk_key = other_metadata.get("chunk_key", "")
                other_base_key = re.sub(r'_part\d+_\d+$', '', other_chunk_key)
                
                if base_key == other_base_key:
                    related_chunks.add(other_chunk_key)
        
        # Coleta todos os chunks que foram marcados como relacionados
        final_results = []
        for result in all_results:
            metadata = result.get("metadata", {})
            chunk_key = metadata.get("chunk_key", "")
            
            if chunk_key in related_chunks:
                final_results.append(result)
        
        # Ordena os resultados finais pelo score de relevância novamente para garantir
        final_results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        
        # Remove duplicados baseados no conteúdo exato
        unique_final_results = []
        seen_content = set()
        for result in final_results:
            if result["content"] not in seen_content:
                unique_final_results.append(result)
                seen_content.add(result["content"])

        return unique_final_results[:top_k]
    
    def search(self, query: str, query_analysis: Dict[str, Any], top_k: int = 5) -> List[Dict]:
        try:
            query_embedding = self.get_embedding(query)
            
            results_by_collection = {}
            for collection_name in self.collections:
                if self.collections[collection_name]:
                    collection_results = self.search_collection(
                        collection_name, 
                        query_embedding,
                        top_k_initial=self.max_results_per_collection
                    )
                    results_by_collection[collection_name] = collection_results
            
            merged_results = self.merge_and_rank_results(results_by_collection, query, query_analysis, top_k)
            
            for result in merged_results:
                result["query_debug_original"] = query
                
            logger.info(f"Found {len(merged_results)} results for query: '{query}' after merging and reranking.")
            return merged_results
            
        except Exception as e:
            logger.error(f"Error in main search process: {str(e)}")
            return []

    def _initialize_reranker(self):
        self.reranker_config = {
            "is_fitted": True, 
            "type": "simple_sort"  # Reflects current simplified logic
        }
        logger.info("Reranker (simple_sort) initialized successfully")

    def _initialize_query_analyzer(self):
        try:
            self.query_analyzer = BasicQueryAnalyzer()
            logger.info("BasicQueryAnalyzer initialized successfully in SemanticSearch")
        except Exception as e:
            logger.error(f"Error initializing BasicQueryAnalyzer in SemanticSearch: {str(e)}")
            self.query_analyzer = None

    def get_document_context(self, query: str, query_analysis: Dict[str, Any], top_k: int = 5) -> Tuple[str, List[Dict]]:
        try:
            results = self.search(query, query_analysis, top_k)
            if not results:
                logger.warning(f"No results found for query: {query}")
                return "", []
            
            # Group results by base chunk_key
            grouped_results = {}
            for result in results:
                metadata = result.get("metadata", {})
                chunk_key = metadata.get("chunk_key", "")
                base_key = re.sub(r'_part\d+_\d+$', '', chunk_key)
                
                if base_key not in grouped_results:
                    grouped_results[base_key] = []
                grouped_results[base_key].append(result)
            
            context_parts = []
            expected_output = query_analysis.get("expected_output")
            
            # Add query information
            context_parts.append(f"## Query Information\n")
            context_parts.append(f"Original Query: {query}\n")
            context_parts.append(f"Expected Output Type: {expected_output}\n")
            context_parts.append(f"Query Intents: {', '.join(query_analysis.get('intents', []))}\n")
            
            # Process each group of related chunks
            for base_key, group in grouped_results.items():
                # Sort group by part number
                group.sort(key=lambda x: int(re.search(r'_part\d+_(\d+)$', x.get("metadata", {}).get("chunk_key", "")).group(1)) if re.search(r'_part\d+_(\d+)$', x.get("metadata", {}).get("chunk_key", "")) else 0)
                
                # Calculate average score for the group
                avg_score = sum(r.get("relevance_score", 0.0) for r in group) / len(group)
                
                # Add group header
                context_parts.append(f"\n## Related Information Group (Average Score: {avg_score:.4f})\n")
                
                # Add metadata information
                metadata = group[0].get("metadata", {})
                context_parts.append(f"Source: {group[0].get('collection', 'Unknown')}\n")
                if "file_path" in metadata:
                    context_parts.append(f"File: {metadata['file_path']}\n")
                if "title" in metadata:
                    context_parts.append(f"Title: {metadata['title']}\n")
                
                # Add content from all parts
                context_parts.append("\n### Content\n")
                for i, result in enumerate(group, 1):
                    part_num_match = re.search(r'_part\d+_(\d+)$', result.get("metadata", {}).get("chunk_key", ""))
                    part_num = part_num_match.group(1) if part_num_match else str(i)
                    context_parts.append(f"Part {part_num} (Score: {result['relevance_score']:.4f}):\n{result['content']}\n")
                
                # Add relevance indicators
                context_parts.append("\n### Relevance Indicators\n")
                indicators = []
                if any(r.get("has_code_example") for r in group):
                    indicators.append("Contains code examples")
                if any(r.get("has_field_definition") for r in group):
                    indicators.append("Contains field definitions")
                if any(r.get("has_method_description") for r in group):
                    indicators.append("Contains method descriptions")
                context_parts.append(", ".join(indicators) + "\n")
            
            context_str = "\n".join(context_parts)
            logger.info(f"Generated context with {len(results)} results, {len(context_str)} chars for query: {query}")
            return context_str, results

        except Exception as e:
            logger.error(f"Error getting document context: {str(e)}")
            return "", []