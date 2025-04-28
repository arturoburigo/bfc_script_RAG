# semantic_search.py
import os
import time
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return

# Configure logging
logger = setup_logging(__name__, "logs/semantic_search.log")

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
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Load collections
        self._load_collections()
        
        # Configure search parameters
        self.max_results_per_collection = 10  # Increased from 5 to get more results
        self.min_relevance_score = 0.3  # Lowered from 0.5 to include more results
    
    def _load_collections(self):
        """
        Load collections from ChromaDB.
        """
        try:
            # Get all collections
            collections = self.chroma_client.list_collections()
            
            # Initialize collections dictionary
            self.collections = {}
            
            # Load each collection
            for collection in collections:
                collection_name = collection.name
                self.collections[collection_name] = collection
                logger.info(f"Loaded collection: {collection_name}")
            
            # Check if we have the expected collections
            expected_collections = ["docs", "enums", "folha", "pessoal"]
            for collection_name in expected_collections:
                if collection_name not in self.collections:
                    logger.warning(f"Expected collection {collection_name} not found")
            
            logger.info(f"Loaded {len(self.collections)} collections")
        except Exception as e:
            logger.error(f"Error loading collections: {str(e)}")
            self.collections = {}
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Truncate text if too long
            max_tokens = 8000
            if len(text) > max_tokens:
                text = text[:max_tokens]
            
            # Get embedding
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Return a random embedding as fallback
            return np.random.rand(1536).tolist()
    
    def search_collection(self, collection_name: str, query_embedding: List[float], top_k: int = 10, 
                         filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search in a specific collection.
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters for the query
            
        Returns:
            List of search results
        """
        collection = self.collections.get(collection_name)
        if not collection:
            logger.warning(f"Collection {collection_name} not available")
            return []
        
        try:
            # Prepare query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k
            }
            
            if filters:
                query_params["where"] = filters
            
            # Execute query
            print(query_params)
            results = collection.query(**query_params)
            print(results)
            
            # Format results
            formatted_results = []
            if results and 'documents' in results and results['documents']:
                for i in range(len(results['documents'][0])):
                    # Only include results with high relevance
                    distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 1.0
                    relevance_score = 1.0 - distance  # Convert distance to relevance score
                    
                    if relevance_score >= self.min_relevance_score:
                        formatted_results.append({
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'] else {},
                            "distance": distance,
                            "collection": collection_name,
                            "relevance_score": relevance_score
                        })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching in collection {collection_name}: {str(e)}")
            return []
    
    def merge_and_rank_results(self, results_by_collection: Dict[str, List[Dict]], top_k: int = 10) -> List[Dict]:
        """
        Merge and rank results from multiple collections.
        
        Args:
            results_by_collection: Dictionary of results by collection
            top_k: Number of results to return
            
        Returns:
            Merged and ranked results
        """
        # Flatten results
        all_results = []
        for collection_name, results in results_by_collection.items():
            all_results.extend(results)
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Return top k results
        return all_results[:top_k]
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from the query to improve search.
        
        Args:
            query: User query
            
        Returns:
            List of keywords
        """
        # Common BFC-Script keywords related to data sources and functions
        bfc_keywords = [
            "cargo", "funcionario", "folha", "pessoal", "salario", "contrato", 
            "evento", "rubrica", "lancamento", "historico", "movimento", 
            "filtro", "campos", "ordenacao", "percorrer", "dados", "fonte"
        ]
        
        # Extract keywords from query
        keywords = []
        query_lower = query.lower()
        
        for keyword in bfc_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        return keywords
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Perform semantic search across all collections.
        
        Args:
            query: User query
            top_k: Number of results to return
            
        Returns:
            Search results
        """
        try:
            # Extract keywords from query
            keywords = self.extract_keywords(query)
            
            # Clean query and expand for better semantic search
            expanded_query = f"{query}, procure em todas as collections"
            
            # Add keywords to expanded query
            if keywords:
                expanded_query += " " + " ".join(keywords)
            
            # Get embedding for query
            query_embedding = self.get_embedding(expanded_query)
            
            # Search in all collections
            results_by_collection = {}
            for collection_name in self.collections:
                if self.collections[collection_name]:
                    collection_results = self.search_collection(
                        collection_name, 
                        query_embedding, 
                        top_k=self.max_results_per_collection
                    )
                    results_by_collection[collection_name] = collection_results
            
            # If no results found, try with just the keywords
            if not any(results for results in results_by_collection.values()) and keywords:
                logger.info(f"No results found with full query, trying with keywords: {keywords}")
                keyword_query = " ".join(keywords)
                keyword_embedding = self.get_embedding(keyword_query)
                
                for collection_name in self.collections:
                    if self.collections[collection_name]:
                        collection_results = self.search_collection(
                            collection_name, 
                            keyword_embedding, 
                            top_k=self.max_results_per_collection
                        )
                        results_by_collection[collection_name] = collection_results
            
            # Merge and rank results
            merged_results = self.merge_and_rank_results(results_by_collection, top_k)
            
            # Add search metadata
            for result in merged_results:
                result["query"] = query
            
            # Log search results
            logger.info(f"Search for '{query}' returned {len(merged_results)} results")
            
            return merged_results
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return []
    
    def get_document_context(self, query: str, top_k: int = 10) -> Tuple[str, List[Dict]]:
        """
        Get context from documents based on the query.
        
        Args:
            query: User query
            top_k: Number of results to return
            
        Returns:
            Context string and search results
        """
        try:
            # Get search results
            results = self.search(query, top_k)
            if not results:
                logger.warning(f"No results found for query: {query}")
                return "", []
            
            # Build context with source information
            context_parts = []
            for i, r in enumerate(results):
                metadata = r.get("metadata", {})
                source_info = []
                
                # Add collection-specific metadata
                if r.get("collection") == "docs":
                    if metadata.get("document"):
                        source_info.append(f"Documento: {metadata['document']}")
                    if metadata.get("section"):
                        source_info.append(f"Seção: {metadata['section']}")
                elif r.get("collection") == "enums":
                    if metadata.get("enum_name"):
                        source_info.append(f"Enum: {metadata['enum_name']}")
                elif r.get("collection") in ["folha", "pessoal"]:
                    if metadata.get("function_name"):
                        source_info.append(f"Função: {metadata['function_name']}")
                    if metadata.get("filename"):
                        source_info.append(f"Arquivo: {metadata['filename']}")
                
                # Build context entry with relevance score
                source_str = " | ".join(source_info)
                relevance = r.get("relevance_score", 0.0)
                context_parts.append(f"[{i+1}] Relevância: {relevance:.2f}\n{r['content']}\nFonte: {source_str}\n")
            
            context = "\n".join(context_parts)
            logger.info(f"Generated context with {len(results)} results for query: {query}")
            return context, results
        except Exception as e:
            logger.error(f"Error getting document context: {str(e)}")
            return "", []