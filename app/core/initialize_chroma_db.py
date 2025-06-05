# initialize_chroma_db.py - Versão Otimizada
import os
import json
import chromadb
from chromadb.config import Settings
from pathlib import Path
from tqdm import tqdm
import logging
import ijson
from typing import List, Dict, Any, Optional, Set, Generator, Tuple
import uuid
import hashlib
import time
import numpy as np
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return
from dataclasses import dataclass
from collections import defaultdict
import chromadb.errors

# Configure logging
logger = setup_logging(__name__, "logs/chroma_initialization.log")

@dataclass
class DocumentMetadata:
    source_file: str
    collection_type: str
    content_hash: str
    content_length: int
    embedding_dimension: int
    processing_timestamp: float
    
@dataclass
class CollectionStats:
    name: str
    total_documents: int
    avg_embedding_dimension: float
    content_types: Dict[str, int]
    avg_relevance_score: float
    index_quality_score: float

class EmbeddingValidator:
    """Valida e normaliza embeddings para garantir qualidade"""
    
    def __init__(self, expected_dimension: int = 512):
        self.expected_dimension = expected_dimension
        self.validation_stats = {
            "total_processed": 0,
            "invalid_embeddings": 0,
            "normalized_embeddings": 0,
            "zero_embeddings": 0
        }
    
    def validate_and_normalize(self, embedding: List[float], content: str = "") -> Tuple[bool, List[float]]:
        """
        Valida e normaliza embedding, retornando (is_valid, normalized_embedding)
        """
        self.validation_stats["total_processed"] += 1
        
        if not embedding or len(embedding) != self.expected_dimension:
            self.validation_stats["invalid_embeddings"] += 1
            logger.warning(f"Invalid embedding dimension: {len(embedding) if embedding else 0}, expected {self.expected_dimension}")
            return False, []
        
        # Convert to numpy array for processing
        emb_array = np.array(embedding, dtype=np.float32)
        
        # Check for NaN or infinite values
        if np.isnan(emb_array).any() or np.isinf(emb_array).any():
            self.validation_stats["invalid_embeddings"] += 1
            logger.warning("Embedding contains NaN or infinite values")
            return False, []
        
        # Check for zero embeddings
        if np.allclose(emb_array, 0.0):
            self.validation_stats["zero_embeddings"] += 1
            logger.warning("Embedding is all zeros")
            return False, []
        
        # Normalize embedding (L2 normalization for cosine similarity)
        norm = np.linalg.norm(emb_array)
        if norm > 0:
            normalized = emb_array / norm
            self.validation_stats["normalized_embeddings"] += 1
            return True, normalized.tolist()
        else:
            self.validation_stats["invalid_embeddings"] += 1
            return False, []
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        stats = self.validation_stats.copy()
        if stats["total_processed"] > 0:
            stats["success_rate"] = (stats["normalized_embeddings"] / stats["total_processed"]) * 100
        else:
            stats["success_rate"] = 0.0
        return stats

class ContentDeduplicator:
    """Remove duplicatas baseado em hash de conteúdo"""
    
    def __init__(self):
        self.content_hashes = set()
        self.duplicate_count = 0
        self.unique_count = 0
    
    def is_duplicate(self, content: str) -> bool:
        """Verifica se o conteúdo é duplicado baseado em hash"""
        # Create content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        if content_hash in self.content_hashes:
            self.duplicate_count += 1
            return True
        else:
            self.content_hashes.add(content_hash)
            self.unique_count += 1
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas de deduplicação"""
        return {
            "unique_documents": self.unique_count,
            "duplicate_documents": self.duplicate_count,
            "total_processed": self.unique_count + self.duplicate_count
        }

class OptimizedBatchProcessor:
    """Processador otimizado para inserção em lotes"""
    
    def __init__(self, collection, batch_size: int = 100):
        self.collection = collection
        self.batch_size = batch_size
        self.current_batch = {
            "ids": [],
            "documents": [],
            "embeddings": [],
            "metadatas": []
        }
        self.total_added = 0
        self.batch_count = 0
        
    def add_document(self, doc_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]):
        """Adiciona documento ao batch atual"""
        self.current_batch["ids"].append(doc_id)
        self.current_batch["documents"].append(content)
        self.current_batch["embeddings"].append(embedding)
        self.current_batch["metadatas"].append(metadata)
        
        # Flush batch if full
        if len(self.current_batch["ids"]) >= self.batch_size:
            self.flush_batch()
    
    def flush_batch(self):
        """Processa o batch atual"""
        if not self.current_batch["ids"]:
            return
        
        try:
            self.collection.add(
                ids=self.current_batch["ids"],
                documents=self.current_batch["documents"],
                embeddings=self.current_batch["embeddings"],
                metadatas=self.current_batch["metadatas"]
            )
            
            batch_size = len(self.current_batch["ids"])
            self.total_added += batch_size
            self.batch_count += 1
            
            logger.info(f"Batch {self.batch_count} processed: {batch_size} documents")
            
            # Clear batch
            self.current_batch = {
                "ids": [],
                "documents": [],
                "embeddings": [],
                "metadatas": []
            }
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            # Try to add documents one by one to identify problematic ones
            self._process_batch_individually()
    
    def _process_batch_individually(self):
        """Processa documentos individualmente quando batch falha"""
        logger.info("Processing batch individually to identify issues...")
        
        for i in range(len(self.current_batch["ids"])):
            try:
                self.collection.add(
                    ids=[self.current_batch["ids"][i]],
                    documents=[self.current_batch["documents"][i]],
                    embeddings=[self.current_batch["embeddings"][i]],
                    metadatas=[self.current_batch["metadatas"][i]]
                )
                self.total_added += 1
            except Exception as e:
                logger.error(f"Failed to add document {self.current_batch['ids'][i]}: {str(e)}")
        
        # Clear batch after individual processing
        self.current_batch = {
            "ids": [],
            "documents": [],
            "embeddings": [],
            "metadatas": []
        }
    
    def finalize(self):
        """Processa batch final e retorna estatísticas"""
        self.flush_batch()
        return {
            "total_added": self.total_added,
            "batch_count": self.batch_count,
            "avg_batch_size": self.total_added / self.batch_count if self.batch_count > 0 else 0
        }

class CollectionManager:
    """Gerencia criação e configuração otimizada de collections"""
    
    def __init__(self, client):
        self.client = client
        self.collection_configs = {
            "docs": {
                "distance_metric": "cosine",
                "description": "BFC-Script documentation and general content",
                "expected_content_types": ["documentation", "examples", "guides"]
            },
            "enums": {
                "distance_metric": "cosine", 
                "description": "Enum definitions and classifications",
                "expected_content_types": ["enum_definition", "classification"]
            },
            "folha": {
                "distance_metric": "cosine",
                "description": "Folha domain functions and data sources",
                "expected_content_types": ["function_definition", "data_source", "code_example"]
            },
            "pessoal": {
                "distance_metric": "cosine",
                "description": "Pessoal domain functions and data sources", 
                "expected_content_types": ["function_definition", "data_source", "code_example"]
            }
        }
    
    def create_or_reset_collection(self, collection_name: str, reset: bool = False) -> chromadb.Collection:
        """Cria ou reseta collection com configuração otimizada"""
        
        # Delete existing collection if reset requested
        if reset:
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except (ValueError, chromadb.errors.NotFoundError):
                pass  # Collection doesn't exist
        
        # Get configuration
        config = self.collection_configs.get(collection_name, {})
        
        # Create collection with optimized settings
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": config.get("distance_metric", "cosine"),
                "hnsw:construction_ef": 200,  # Changed from ef_construction
                "hnsw:search_ef": 10,  # Changed from ef
                "hnsw:M": 16,
                "description": config.get("description", ""),
                "created_timestamp": time.time(),
                "content_types": ",".join(config.get("expected_content_types", []))
            }
        )
        
        logger.info(f"Created/retrieved collection '{collection_name}' with optimized HNSW settings")
        return collection
    
    def get_collection_stats(self, collection_name: str) -> Optional[CollectionStats]:
        """Obtém estatísticas detalhadas da collection"""
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            
            if count == 0:
                return CollectionStats(
                    name=collection_name,
                    total_documents=0,
                    avg_embedding_dimension=0.0,
                    content_types={},
                    avg_relevance_score=0.0,
                    index_quality_score=0.0
                )
            
            # Sample documents to analyze
            sample_size = min(100, count)
            sample_data = collection.get(
                limit=sample_size,
                include=["documents", "metadatas", "embeddings"]
            )
            
            # Calculate statistics
            content_types = defaultdict(int)
            embedding_dims = []
            
            if sample_data["metadatas"]:
                for metadata in sample_data["metadatas"]:
                    content_type = metadata.get("content_type", "unknown")
                    content_types[content_type] += 1
            
            if sample_data["embeddings"]:
                for embedding in sample_data["embeddings"]:
                    if embedding:
                        embedding_dims.append(len(embedding))
            
            avg_dimension = sum(embedding_dims) / len(embedding_dims) if embedding_dims else 0.0
            
            # Calculate index quality score (based on embedding consistency and metadata completeness)
            index_quality = 0.0
            if embedding_dims:
                dim_consistency = len(set(embedding_dims)) == 1  # All same dimension
                metadata_completeness = sum(1 for m in sample_data["metadatas"] if m) / len(sample_data["metadatas"])
                index_quality = (0.7 if dim_consistency else 0.3) + (0.3 * metadata_completeness)
            
            return CollectionStats(
                name=collection_name,
                total_documents=count,
                avg_embedding_dimension=avg_dimension,
                content_types=dict(content_types),
                avg_relevance_score=0.0,  # Would need calculation based on search results
                index_quality_score=index_quality
            )
            
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {e}")
            return None

class DocumentProcessor:
    """Processa diferentes tipos de documentos com estratégias específicas"""
    
    def __init__(self, validator: EmbeddingValidator, deduplicator: ContentDeduplicator):
        self.validator = validator
        self.deduplicator = deduplicator
        self.processing_stats = defaultdict(int)
    
    def process_docs_collection(self, data: List[Dict], collection_name: str) -> Generator[Tuple[str, str, List[float], Dict], None, None]:
        """Processa documentação geral"""
        for i, chunk in enumerate(data):
            try:
                content = chunk.get("content", "")
                embedding = chunk.get("embedding", [])
                
                if not content or not embedding:
                    self.processing_stats["skipped_empty"] += 1
                    continue
                
                # Check for duplicates
                if self.deduplicator.is_duplicate(content):
                    self.processing_stats["skipped_duplicate"] += 1
                    continue
                
                # Validate embedding
                is_valid, normalized_embedding = self.validator.validate_and_normalize(embedding, content)
                if not is_valid:
                    self.processing_stats["skipped_invalid_embedding"] += 1
                    continue
                
                # Enhanced metadata
                metadata = {
                    'collection': collection_name,
                    'document': chunk.get("document", ""),
                    'section': chunk.get("section", ""),
                    'subsection': chunk.get("subsection", ""),
                    'contains_code': chunk.get("contains_code", False),
                    'content_type': self._classify_content_type(content),
                    'content_length': len(content),
                    'processing_timestamp': time.time(),
                    'chunk_index': i
                }
                
                # Generate deterministic ID
                doc_id = self._generate_document_id(collection_name, content, metadata)
                
                self.processing_stats["processed_successfully"] += 1
                yield doc_id, content, normalized_embedding, metadata
                
            except Exception as e:
                logger.error(f"Error processing docs chunk {i}: {e}")
                self.processing_stats["processing_errors"] += 1
    
    def process_enums_collection(self, data: Dict[str, List], collection_name: str) -> Generator[Tuple[str, str, List[float], Dict], None, None]:
        """Processa enums com estrutura específica"""
        for enum_name, enum_chunks in data.items():
            for chunk_idx, chunk in enumerate(enum_chunks):
                try:
                    content = chunk.get("content", "")
                    embedding = chunk.get("embedding", [])
                    
                    if not content or not embedding:
                        self.processing_stats["skipped_empty"] += 1
                        continue
                    
                    # Check for duplicates
                    if self.deduplicator.is_duplicate(content):
                        self.processing_stats["skipped_duplicate"] += 1
                        continue
                    
                    # Validate embedding
                    is_valid, normalized_embedding = self.validator.validate_and_normalize(embedding, content)
                    if not is_valid:
                        self.processing_stats["skipped_invalid_embedding"] += 1
                        continue
                    
                    # Enhanced metadata for enums
                    metadata = {
                        'collection': collection_name,
                        'enum_name': enum_name,
                        'chunk_key': chunk.get("chunk_key", ""),
                        'content_type': 'enum_definition',
                        'content_length': len(content),
                        'processing_timestamp': time.time(),
                        'chunk_index': chunk_idx
                    }
                    
                    # Add part number if available
                    part_number = chunk.get("part_number")
                    if part_number is not None:
                        metadata['part_number'] = part_number
                    
                    # Generate deterministic ID
                    doc_id = self._generate_document_id(collection_name, content, metadata)
                    
                    self.processing_stats["processed_successfully"] += 1
                    yield doc_id, content, normalized_embedding, metadata
                    
                except Exception as e:
                    logger.error(f"Error processing enum {enum_name} chunk {chunk_idx}: {e}")
                    self.processing_stats["processing_errors"] += 1
    
    def process_function_collection(self, data: Dict[str, List], collection_name: str) -> Generator[Tuple[str, str, List[float], Dict], None, None]:
        """Processa coleções de funções (folha/pessoal) com o novo formato"""
        for function_name, function_chunks in data.items():
            for chunk in function_chunks:
                try:
                    content = chunk.get("content", "")
                    embedding = chunk.get("embedding", [])
                    
                    if not content or not embedding:
                        self.processing_stats["skipped_empty"] += 1
                        continue
                    
                    # Check for duplicates
                    if self.deduplicator.is_duplicate(content):
                        self.processing_stats["skipped_duplicate"] += 1
                        continue
                    
                    # Validate embedding
                    is_valid, normalized_embedding = self.validator.validate_and_normalize(embedding, content)
                    if not is_valid:
                        self.processing_stats["skipped_invalid_embedding"] += 1
                        continue
                    
                    # Convert extracted_headers to string if it's a dictionary
                    extracted_headers = chunk.get("extracted_headers", {})
                    if isinstance(extracted_headers, dict):
                        extracted_headers = json.dumps(extracted_headers)
                    
                    # Convert keywords list to string if it's a list
                    keywords = chunk.get("keywords", [])
                    if isinstance(keywords, list):
                        keywords = json.dumps(keywords)
                    
                    # Enhanced metadata for functions with new format
                    metadata = {
                        'collection': collection_name,
                        'function_name': function_name,
                        'chunk_key': chunk.get("chunk_key", ""),
                        'source_document_id': chunk.get("source_document_id", ""),
                        'original_section_name': chunk.get("original_section_name", ""),
                        'langchain_doc_index': chunk.get("langchain_doc_index", 0),
                        'chunk_index_in_lc_doc': chunk.get("chunk_index_in_lc_doc", 0),
                        'total_chunks_in_lc_doc': chunk.get("total_chunks_in_lc_doc", 0),
                        'extracted_headers': extracted_headers,
                        'title': chunk.get("title", ""),
                        'code_block_count': chunk.get("code_block_count", 0),
                        'keywords': keywords,
                        'token_count': chunk.get("token_count", 0),
                        'embedding_dimensions': chunk.get("embedding_dimensions", 512),
                        'chunk_file_path': chunk.get("chunk_file_path", ""),
                        'processing_timestamp': chunk.get("processing_timestamp", time.time()),
                        'has_code': chunk.get("has_code", False),
                        'content_type': chunk.get("content_type", "code_example"),
                        'semantic_level': chunk.get("semantic_level", "fragment"),
                        'part_number': chunk.get("part_number", 0),
                        'content_length': len(content),
                        'domain': collection_name  # folha or pessoal
                    }
                    
                    # Generate deterministic ID using chunk_key if available
                    doc_id = chunk.get("chunk_key", self._generate_document_id(collection_name, content, metadata))
                    
                    self.processing_stats["processed_successfully"] += 1
                    yield doc_id, content, normalized_embedding, metadata
                    
                except Exception as e:
                    logger.error(f"Error processing function {function_name}: {e}")
                    self.processing_stats["processing_errors"] += 1
    
    def _classify_content_type(self, content: str) -> str:
        """Classifica tipo de conteúdo baseado em padrões"""
        content_lower = content.lower()
        
        if "```" in content or "code example:" in content_lower:
            return "code_example"
        elif "types:" in content_lower:
            return "field_definition"
        elif "expressions:" in content_lower:
            return "filter_definition"
        elif content.startswith("# ") and ("description:" in content_lower or "method:" in content_lower):
            return "api_documentation"
        else:
            return "general_documentation"
    
    def _classify_function_content_type(self, content: str) -> str:
        """Classifica tipo de conteúdo para funções"""
        content_lower = content.lower()
        
        if "```" in content or "code example:" in content_lower:
            return "code_example"
        elif "types:" in content_lower:
            return "field_definition"
        elif "expressions:" in content_lower:
            return "filter_definition"
        elif "method:" in content_lower:
            return "function_definition"
        else:
            return "data_source"
    
    def _generate_document_id(self, collection_name: str, content: str, metadata: Dict) -> str:
        """Gera ID determinístico para o documento"""
        # Create a unique identifier based on content and key metadata
        id_components = [
            collection_name,
            metadata.get("function_name", ""),
            metadata.get("enum_name", ""),
            metadata.get("document", ""),
            metadata.get("section", ""),
            str(metadata.get("chunk_index", 0))
        ]
        
        # Create hash from content and components
        id_string = "|".join(str(comp) for comp in id_components) + "|" + content[:100]
        doc_hash = hashlib.md5(id_string.encode('utf-8')).hexdigest()
        
        return f"{collection_name}_{doc_hash}"
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Retorna estatísticas de processamento"""
        return dict(self.processing_stats)

def initialize_chroma_db(reset_collections: bool = False):
    """
    Initialize ChromaDB with enhanced optimization and validation.
    """
    log_function_call(logger, "initialize_chroma_db", kwargs={"reset_collections": reset_collections})
    
    start_time = time.time()
    
    # Initialize ChromaDB client with optimized settings
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False,
            is_persistent=True,
        )
    )
    
    # Initialize components
    embedding_validator = EmbeddingValidator(expected_dimension=512)
    content_deduplicator = ContentDeduplicator()
    collection_manager = CollectionManager(client)
    document_processor = DocumentProcessor(embedding_validator, content_deduplicator)
    
    # Define collection configurations
    collection_files = {
        "docs": {
            "file_path": os.path.join(os.getcwd(), "docs", "bfc_documentation_embeddings_v2.json"),
            "processor_method": "process_docs_collection"
        },
        "enums": {
            "file_path": os.path.join(os.getcwd(), "docs", "enums_pessoal_and_folha_with_embeddings.json"),
            "processor_method": "process_enums_collection"
        },
        "folha": {
            "file_path": os.path.join(os.getcwd(), "docs", "folha_with_embeddings.json"),
            "processor_method": "process_function_collection"
        },
        "pessoal": {
            "file_path": os.path.join(os.getcwd(), "docs", "pessoal_with_embeddings.json"),
            "processor_method": "process_function_collection"
        }
    }
    
    # Process each collection
    total_stats = {
        "collections_processed": 0,
        "total_documents_added": 0,
        "total_duplicates_removed": 0,
        "total_invalid_embeddings": 0,
        "processing_time": 0.0
    }
    
    for collection_name, config in collection_files.items():
        logger.info(f"Processing collection: {collection_name}")
        collection_start_time = time.time()
        
        # Create or reset collection
        collection = collection_manager.create_or_reset_collection(collection_name, reset_collections)
        
        # Check if file exists
        file_path = config["file_path"]
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
        
        try:
            # Load data
            logger.info(f"Loading data from {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get existing IDs to avoid duplicates
            existing_ids = set()
            try:
                existing_data = collection.get()
                existing_ids = set(existing_data.get("ids", []))
                logger.info(f"Found {len(existing_ids)} existing documents in collection {collection_name}")
            except Exception as e:
                logger.warning(f"Could not retrieve existing IDs: {e}")
            
            # Initialize batch processor
            batch_processor = OptimizedBatchProcessor(collection, batch_size=50)
            
            # Process documents based on collection type
            processor_method = getattr(document_processor, config["processor_method"])
            document_generator = processor_method(data, collection_name)
            
            # Process documents with progress bar
            processed_count = 0
            skipped_existing = 0
            
            logger.info(f"Processing documents for collection {collection_name}...")
            
            for doc_id, content, embedding, metadata in tqdm(document_generator, desc=f"Processing {collection_name}"):
                # Skip if document already exists
                if doc_id in existing_ids:
                    skipped_existing += 1
                    continue
                
                # Add to batch
                batch_processor.add_document(doc_id, content, embedding, metadata)
                processed_count += 1
            
            # Finalize batch processing
            batch_stats = batch_processor.finalize()
            
            # Log collection statistics
            collection_time = time.time() - collection_start_time
            logger.info(f"Collection {collection_name} completed:")
            logger.info(f"  - Documents processed: {processed_count}")
            logger.info(f"  - Documents added: {batch_stats['total_added']}")
            logger.info(f"  - Existing documents skipped: {skipped_existing}")
            logger.info(f"  - Processing time: {collection_time:.2f}s")
            
            # Update total stats
            total_stats["collections_processed"] += 1
            total_stats["total_documents_added"] += batch_stats["total_added"]
            
        except Exception as e:
            logger.error(f"Error processing collection {collection_name}: {str(e)}")
            continue
    
    # Final statistics and validation
    total_time = time.time() - start_time
    total_stats["processing_time"] = total_time
    
    # Get validation stats
    validation_stats = embedding_validator.get_stats()
    deduplication_stats = content_deduplicator.get_stats()
    processing_stats = document_processor.get_processing_stats()
    
    # Log comprehensive summary
    logger.info("=" * 80)
    logger.info("CHROMADB INITIALIZATION COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Total collections processed: {total_stats['collections_processed']}")
    logger.info(f"Total documents added: {total_stats['total_documents_added']}")
    logger.info(f"Total processing time: {total_time:.2f}s")
    logger.info("")
    logger.info("VALIDATION STATISTICS:")
    logger.info(f"  - Embeddings processed: {validation_stats['total_processed']}")
    logger.info(f"  - Valid embeddings: {validation_stats['normalized_embeddings']}")
    logger.info(f"  - Invalid embeddings: {validation_stats['invalid_embeddings']}")
    logger.info(f"  - Success rate: {validation_stats['success_rate']:.1f}%")
    logger.info("")
    logger.info("DEDUPLICATION STATISTICS:")
    logger.info(f"  - Unique documents: {deduplication_stats['unique_documents']}")
    logger.info(f"  - Duplicate documents removed: {deduplication_stats['duplicate_documents']}")
    logger.info("")
    logger.info("PROCESSING STATISTICS:")
    for stat_name, stat_value in processing_stats.items():
        logger.info(f"  - {stat_name}: {stat_value}")
    
    # Generate collection health report
    logger.info("")
    logger.info("COLLECTION HEALTH REPORT:")
    for collection_name in collection_files.keys():
        stats = collection_manager.get_collection_stats(collection_name)
        if stats:
            logger.info(f"  {collection_name}:")
            logger.info(f"    - Documents: {stats.total_documents}")
            logger.info(f"    - Avg embedding dimension: {stats.avg_embedding_dimension:.1f}")
            logger.info(f"    - Index quality score: {stats.index_quality_score:.2f}")
            logger.info(f"    - Content types: {stats.content_types}")
    
    logger.info("=" * 80)
    
    log_function_return(logger, "initialize_chroma_db", None)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize ChromaDB with optimized embeddings")
    parser.add_argument("--reset", action="store_true", help="Reset collections before adding documents")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing collections without adding new documents")
    args = parser.parse_args()
    
    if args.validate_only:
        # Only run validation and health check
        client = chromadb.PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))
        collection_manager = CollectionManager(client)
        
        logger.info("COLLECTION VALIDATION REPORT:")
        for collection_name in ["docs", "enums", "folha", "pessoal"]:
            stats = collection_manager.get_collection_stats(collection_name)
            if stats:
                logger.info(f"{collection_name}: {stats.total_documents} docs, quality: {stats.index_quality_score:.2f}")
            else:
                logger.info(f"{collection_name}: Not found or error")
    else:
        initialize_chroma_db(reset_collections=args.reset)