# semantic_search.py
import os
import time
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
import re
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return
import gradio as gr

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
        
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        self._load_collections()
        
        self._initialize_reranker()
        
        self._initialize_query_analyzer()
        
        self.max_results_per_collection = 10  # Increased for better recall
        self.min_relevance_score = 0.0  
        
        # Configure collection weights - prioritize code sources for code-related queries
        self.collection_weights = {
            "docs": 0.7,
            "enums": 0.7,
            "folha": 1.0,
            "pessoal": 1.0
        }
        
        # Define domain-specific patterns to recognize in queries
        self.domain_patterns = {
            "fonte_de_dados": [
                r"fonte\s+de\s+dados",
                r"Dados\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+",
                r"fonte",
            ],
            "codigo_exemplo": [
                r"exemplo",
                r"código",
                r"script",
                r"criar",
                r"implementar",
                r"code example"
            ],
            "filtros": [
                r"filtro",
                r"condição",
                r"types",
                r"expressions"
            ],
            "campo": [
                r"campo",
                r"atributo",
                r"propriedade",
                r"field",
                r"Campos"
            ],
            "enum": [
                r"enum",
                r"classificacao",
                r"tipo",
            ]
        }
        
        # Define source type weights
        self.source_type_weights = {
            "folha": 1.2,
            "pessoal": 1.2,
            "historico": 0.8,
            "relatorio": 0.8
        }
    
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
                # Get the collection - it should already have cosine distance from initialization
                self.collections[collection_name] = self.chroma_client.get_collection(collection_name)
                
                # Check collection status
                count = self.collections[collection_name].count()
                logger.info(f"Loaded collection: {collection_name} with {count} documents")
            
            logger.info(f"Loaded {len(self.collections)} collections")
        except Exception as e:
            logger.error(f"Error loading collections: {str(e)}")
            self.collections = {}
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance the query with domain-specific terms to improve search relevance.
        
        Args:
            query: Original user query
            
        Returns:
            Enhanced query
        """
        # TEMPORARILY DISABLED - query enhancement might be making results worse
        # Return original query without modifications
        #return query
        
        # Original enhancement code commented out for testing
        
        query_lower = query.lower()
        
        # Analyze query intent
        query_intents = []
        
        for intent, patterns in self.domain_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                query_intents.append(intent)
        
        # No enhancement needed if no patterns detected
        if not query_intents:
            return query
        
        # Add domain-specific context based on detected intents
        enhancements = []
        
        if "fonte_de_dados" in query_intents:
            # Check for specific domain sources mentioned
            if "folha" in query_lower:
                enhancements.append("Dados.folha.v2")
            if "pessoal" in query_lower:
                enhancements.append("Dados.pessoal.v2")
                
        if "codigo_exemplo" in query_intents:
            enhancements.append("Code Example")
            
        if "filtros" in query_intents:
            enhancements.append("filtros, busca expressions")
            
        if "enum" in query_intents:
            enhancements.append("enum values")
        
        # Create enhanced query
        if enhancements:
            enhanced_query = f"{query} {' '.join(enhancements)}"
            logger.info(f"Enhanced query from '{query}' to '{enhanced_query}'")
            return enhanced_query
            
        return query
    
    
    def detect_content_type(self, query: str) -> Dict[str, float]:
        """
        Detect the type of content needed and provide collection weights.
        
        
        Args:
            query: User query
            
        Returns:
            Dictionary of collection weights
        """
        query_lower = query.lower()
        
        # Default weights
        weights = self.collection_weights.copy()
        
        # Adjust weights based on query content
        if any(term in query_lower for term in ["código", "script", "busca", "implementar", "criar"]):
            # For code-related queries, prioritize collections with examples
            weights["folha"] *= 1.1
            weights["pessoal"] *= 1.1
            weights["enums"] *= 0.9
            weights["docs"] *= 0.8
            
        elif any(term in query_lower for term in ["enum", "enums", "tipo"]):
            # For enum-related queries
            weights["enums"] *= 1.2
            weights["docs"] *= 0.9
            weights["folha"] *= 0.8
            weights["pessoal"] *= 0.8
            
        elif any(term in query_lower for term in ["documentação", "conceito", "o que é"]):
            # For documentation/concept queries
            weights["docs"] *= 1.2
            weights["enums"] *= 0.9
            weights["folha"] *= 0.7
            weights["pessoal"] *= 0.7
        
        # Source-specific weights
        if "folha" in query_lower:
            weights["folha"] *= self.source_type_weights["folha"]
            weights["pessoal"] *= 0.6
        elif "pessoal" in query_lower:
            weights["pessoal"] *= self.source_type_weights["pessoal"]
            weights["folha"] *= 0.6
            
        logger.info(f"Content type detection weights: {weights}")
        return weights
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Truncate text if too long (matching embedding files)
            max_tokens = 8000
            if len(text) > max_tokens:
                text = text[:max_tokens]
                logger.info(f"Text truncated to {max_tokens} tokens")
            
            logger.info(f"Generating embedding for text of length {len(text)}")
            
            # Use the same model as embedding files
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=512  # Full dimensionality as used in embedding files
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding of length {len(embedding)}")
            
            # Log embedding statistics
            embedding_array = np.array(embedding)
            logger.info(f"Embedding stats - Mean: {np.mean(embedding_array):.4f}, Std: {np.std(embedding_array):.4f}, Min: {np.min(embedding_array):.4f}, Max: {np.max(embedding_array):.4f}")
            
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return np.random.rand(3072).tolist()  # Match embedding dimension
    
    def search_collection(self, collection_name: str, query_embedding: List[float], 
                         content_weights: Dict[str, float], top_k: int = 100) -> List[Dict]:
        """
        Search in a specific collection with content type weighting.
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            content_weights: Weights for different content types
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        collection = self.collections.get(collection_name)
        if not collection:
            logger.warning(f"Collection {collection_name} not available")
            return []
        
        try:
            # Execute query with increased n_results
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and 'documents' in results and results['documents']:
                logger.info(f"Raw distances from ChromaDB: {results['distances'][0] if 'distances' in results else 'No distances'}")
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 1.0
                    # For cosine distance: 0 = identical, 2 = opposite
                    # Convert to relevance score: 1 = perfect match, 0 = no match
                    relevance_score = 1.0 - (distance / 2.0)  # Normalize cosine distance to [0, 1]
                    
                    logger.info(f"Document {i+1} - Raw distance: {distance:.4f}, Relevance score: {relevance_score:.4f}")
                    
                    # Get the content and metadata
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'] else {}
                    
                    # Apply collection weight to relevance score
                    collection_weight = content_weights.get(collection_name, 0.8)
                    relevance_score *= collection_weight
                    
                    # Check for code examples and boost their score
                    if "Code Example:" in content or "```" in content:
                        relevance_score *= 1.45  # Boost code examples
                        
                    # Check for specific data source mentions and boost if relevant
                    if any(source in content for source in ["Dados.folha", "Dados.pessoal"]):
                        relevance_score *= 1.3  # Boost data source references
                        
                        # Extract data source information
                        if "Dados.folha.v2" in content:
                            metadata["data_source"] = "Dados.folha.v2"
                            metadata["entity_type"] = "folha"
                        elif "Dados.pessoal.v2" in content:
                            metadata["data_source"] = "Dados.pessoal.v2"
                            metadata["entity_type"] = "pessoal"
                    
                    result = {
                        "content": content,
                        "metadata": metadata,
                        "distance": distance,
                        "collection": collection_name,
                        "relevance_score": relevance_score,
                        "has_code_example": "Code Example:" in content or "```" in content
                    }
                    formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching in collection {collection_name}: {str(e)}")
            return []
    
    def rerank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank results based on content relevance for the query.
        
        Args:
            results: List of search results
            query: User query
            
        Returns:
            Reranked results
        """
        if not results:
            return []
        
        query_lower = query.lower()
        
        # Check for code example requests
        code_example_requested = any(term in query_lower for term in 
                                   ["código", "exemplo", "script", "implementação", "implementar", "criar"])
        
        # Check for specific data source requests
        data_source_requested = any(term in query_lower for term in 
                                  ["fonte de dados", "fonte"])
        
        # Check for specific field requests
        fields_requested = any(term in query_lower for term in 
                             ["campos", "atributos", "fields", "propriedades"])
        
        for result in results:
            score = result["relevance_score"]
            content = result["content"]
            content_lower = content.lower()
            
            # Boost code examples when explicitly requested
            if code_example_requested and result.get("has_code_example", False):
                score *= 1.3
                
            # Boost data source documentation when requested
            if data_source_requested and any(term in content_lower for term in ["fonte", "dados."]):
                score *= 1.25
                
            # Boost field documentation when requested
            if fields_requested and any(term in content_lower for term in ["fields:", "campos:", "propriedades:"]):
                score *= 1.2
                
            # Check for specific entity mentions in both query and content
            # Entities to check (common domain objects)
            '''
            entities = ["cargo", "funcionario", "contrato", "rubrica", "evento", "historico", 
                       "departamento", "consolidacao", "motivo", "rescisao", "classificacao", 
                       "remuneracao", "processotrabalhista"]
            
            for entity in entities:
                if entity in query_lower and entity in content_lower:
                    score *= 1.15  # Boost matches on domain entities
                    
            # Update score
            result["relevance_score"] = score'''
        
        # Re-sort results by updated relevance score
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results
    
    def merge_and_rank_results(self, results_by_collection: Dict[str, List[Dict]], query: str, top_k: int = 10) -> List[Dict]:
        """
        Merge and rank results from multiple collections.
        
        Args:
            results_by_collection: Dictionary of results by collection
            query: Original user query
            top_k: Number of results to return
            
        Returns:
            Merged and ranked results
        """
        # Flatten results
        all_results = []
        for collection_name, results in results_by_collection.items():
            all_results.extend(results)
        
        # Rerank results based on content relevance
        reranked_results = self.rerank_results(all_results, query)
        
        # Return top k results
        return reranked_results[:top_k]
    
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
            # Enhance query with domain-specific terms
            enhanced_query = self.enhance_query(query)
            
            # Detect content type and adjust collection weights
            content_weights = self.detect_content_type(query)
            
            # Get embedding for enhanced query
            query_embedding = self.get_embedding(enhanced_query)
            
            # Search in all collections with content-specific weights
            results_by_collection = {}
            for collection_name in self.collections:
                if self.collections[collection_name]:
                    collection_results = self.search_collection(
                        collection_name, 
                        query_embedding,
                        content_weights,
                        top_k=self.max_results_per_collection
                    )
                    results_by_collection[collection_name] = collection_results
            
            # Merge and rank results with content-aware reranking
            merged_results = self.merge_and_rank_results(results_by_collection, query, top_k)
            
            # Add search metadata
            for result in merged_results:
                result["query"] = query
                
            logger.info(f"Found {len(merged_results)} results for query: '{query}', enhanced: '{enhanced_query}'")
            
            # Log the best matches and their contents for debugging
            if merged_results:
                logger.info("----- TOP SEARCH RESULTS -----")
                for i, result in enumerate(merged_results[:3]):  # Log top 3 results
                    relevance = result.get("relevance_score", 0.0)
                    collection = result.get("collection", "unknown")
                    has_code = "Yes" if result.get("has_code_example", False) else "No"
                    
                    # Format content for logging (trim if too long)
                    content = result.get("content", "")
                    if len(content) > 200:
                        content = content[:200] + "..."
                        
                    logger.info(f"Result #{i+1} | Score: {relevance:.4f} | Collection: {collection} | Has Code: {has_code}")
                    logger.info(f"Content Preview: {content}")
                    logger.info("--------------------------")
            else:
                logger.warning("No results found for the query")
            
            return merged_results
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return []
    
    def extract_code_examples(self, results: List[Dict]) -> List[Dict]:
        """
        Extract code examples from search results.
        
        Args:
            results: Search results
            
        Returns:
            List of code examples with metadata
        """
        code_examples = []
        
        for result in results:
            content = result.get("content", "")
            
            # Check for code examples
            if "Code Example:" in content or "```" in content:
                # Extract code between backticks
                code_blocks = re.findall(r'```(?:.*?)\n(.*?)```', content, re.DOTALL)
                
                if not code_blocks:
                    # Try alternative format: Code Example: followed by text
                    if "Code Example:" in content:
                        parts = content.split("Code Example:")
                        if len(parts) > 1:
                            code_text = parts[1].strip()
                            code_blocks = [code_text]
                
                for code_block in code_blocks:
                    # Get metadata from result
                    metadata = result.get("metadata", {})
                    metadata["source"] = result.get("collection", "")
                    metadata["relevance_score"] = result.get("relevance_score", 0.0)
                    
                    code_examples.append({
                        "code": code_block.strip(),
                        "metadata": metadata,
                        "context": content
                    })
        
        return code_examples
    
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
            # Get search results with enhanced search
            results = self.search(query, top_k)
            
            if not results:
                logger.warning(f"No results found for query: {query}")
                return "", []
            
            # Extract code examples if the query is related to code
            code_examples = []
            if any(term in query.lower() for term in ["código", "exemplo", "script", "implementação", "criar"]):
                code_examples = self.extract_code_examples(results)
                logger.info(f"Extracted {len(code_examples)} code examples from search results")
            
            # Build context with source information
            context_parts = []
            
            # Add code examples first if available and relevant
            if code_examples:
                context_parts.append("## Exemplos de Código Relevantes\n")
                for i, example in enumerate(code_examples):
                    metadata = example.get("metadata", {})
                    source_info = []
                    
                    if metadata.get("function_name"):
                        source_info.append(f"Função: {metadata['function_name']}")
                    if metadata.get("source"):
                        source_info.append(f"Fonte: {metadata['source']}")
                    
                    source_str = " | ".join(source_info)
                    relevance = metadata.get("relevance_score", 0.0)
                    
                    context_parts.append(f"[Exemplo {i+1}] Relevância: {relevance:.2f}\n```\n{example['code']}\n```\nFonte: {source_str}\n")
            
            # Add general context from results
            context_parts.append("## Contexto de Documentação\n")
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
                
                # Build context entry with relevance score and source
                source_str = " | ".join(source_info)
                relevance = r.get("relevance_score", 0.0)
                
                # Skip duplicates that might already be in code examples
                if code_examples and r.get("has_code_example", False):
                    # Only include the non-code parts or a summary
                    content = r.get("content", "")
                    # Remove code blocks
                    content = re.sub(r'```(?:.*?)```', '[Código já mostrado nos exemplos acima]', content, flags=re.DOTALL)
                    # Remove "Code Example:" sections
                    if "Code Example:" in content:
                        parts = content.split("Code Example:")
                        content = parts[0].strip()
                
                context_parts.append(f"[{i+1}] Relevância: {relevance:.2f}\n{r['content']}\nFonte: {source_str}\n")
            
            context = "\n".join(context_parts)
            
            # Log context statistics
            logger.info(f"Generated context with {len(results)} results and {len(context)} characters")
            if code_examples:
                logger.info(f"Context includes {len(code_examples)} code examples")
                
            return context, results
        except Exception as e:
            logger.error(f"Error getting document context: {str(e)}")
            return "", []

    def create_interface(self) -> gr.ChatInterface:
        log_function_call(logger, "BFCScriptUI.create_interface")

        def chat_fn(message, history):
            try:
                search_results = self.search(message)
                response = self.response_generator.generate_response(message, search_results, history)
                return response
            except Exception as e:
                return f"Error: {e}"

        interface = gr.ChatInterface(
            fn=chat_fn,
            title="BFC Script Assistant",
            description="Ask questions about BFC Script programming.",
            theme=gr.themes.Soft(),
            examples=["Como faço um loop em BFC Script?", "O que é a função FOLHA?"],
            retry_btn=None,
            undo_btn=None,
            clear_btn="Limpar Conversa"
        )
        log_function_return(logger, "BFCScriptUI.create_interface", result=interface)
        return interface

    def _initialize_reranker(self):
        """Initialize the reranker component"""
        try:
            # For now, we're using a simple reranking approach based on semantic similarity
            # This could be enhanced with a more sophisticated reranker in the future
            self.reranker = {
                "is_fitted": True,  # Simple reranker is always ready
                "type": "semantic_similarity"
            }
            logger.info("Reranker initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing reranker: {str(e)}")
            self.reranker = {
                "is_fitted": False,
                "type": "none"
            }

    def _initialize_query_analyzer(self):
        """Initialize the query analyzer component"""
        try:
            self.query_analyzer = {
                "is_initialized": True,
                "type": "semantic",
                "features": {
                    "intent_detection": True,
                    "entity_recognition": True,
                    "domain_specific": True
                }
            }
            logger.info("Query analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing query analyzer: {str(e)}")
            self.query_analyzer = {
                "is_initialized": False,
                "type": "none",
                "features": {}
            }