# chroma_initialization.py
import os
import json
import chromadb
from chromadb.config import Settings
from pathlib import Path
from tqdm import tqdm
import logging
import ijson
from typing import List, Dict, Any, Optional, Set, Generator
import uuid
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return

# Configure logging
logger = setup_logging(__name__, "logs/chroma_initialization.log")

def safe_metadata_value(value, default=""):
    """
    Convert a value to a safe metadata value that ChromaDB accepts.
    Returns default value for None values.
    """
    log_function_call(logger, "safe_metadata_value", args=(value, default))
    if value is None:
        result = default
    else:
        result = str(value)
    log_function_return(logger, "safe_metadata_value", result)
    return result

def validate_embedding(embedding: List[float]) -> bool:
    """
    Validate that an embedding is a proper vector of floats.
    
    Args:
        embedding: The embedding vector to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    log_function_call(logger, "validate_embedding", args=(embedding,))
    
    if len(embedding) == 0:
        log_debug(logger, "Embedding is empty")
        result = False
    else:
        result = all(isinstance(x, (int, float)) for x in embedding)
        if not result:
            log_debug(logger, f"Embedding contains non-numeric values: {[type(x) for x in embedding[:5]]}")
    
    log_function_return(logger, "validate_embedding", result)
    return result

def process_batch(collection, documents, embeddings, metadatas, ids):
    """
    Process a batch of documents and add them to the collection.
    
    Args:
        collection: ChromaDB collection
        documents: List of document contents
        embeddings: List of embeddings
        metadatas: List of metadata dictionaries
        ids: List of document IDs
        
    Returns:
        int: Number of documents added
    """
    log_function_call(logger, "process_batch", kwargs={
        "collection": collection.name if hasattr(collection, 'name') else str(collection),
        "documents_count": len(documents),
        "embeddings_count": len(embeddings),
        "metadatas_count": len(metadatas),
        "ids_count": len(ids)
    })
    
    if not documents:
        log_debug(logger, "No documents to process")
        return 0
    
    try:
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        result = len(documents)
        log_debug(logger, f"Successfully added {result} documents to collection")
        log_function_return(logger, "process_batch", result)
        return result
    except Exception as e:
        logger.error(f"Error adding batch to collection: {str(e)}")
        # Try adding documents one by one to identify problematic entries
        added = 0
        for i in range(len(documents)):
            try:
                collection.add(
                    documents=[documents[i]],
                    embeddings=[embeddings[i]],
                    metadatas=[metadatas[i]],
                    ids=[ids[i]]
                )
                added += 1
            except Exception as inner_e:
                logger.error(f"Error adding document {ids[i]}: {str(inner_e)}")
                if is_dev_mode():
                    logger.debug(f"Document content: {documents[i][:100]}...")
                    logger.debug(f"Metadata: {metadatas[i]}")
        
        log_function_return(logger, "process_batch", added)
        return added

def get_existing_ids(collection) -> Set[str]:
    """
    Get existing IDs from a collection to avoid duplicates.
    
    Args:
        collection: ChromaDB collection
        
    Returns:
        Set of existing IDs
    """
    log_function_call(logger, "get_existing_ids", kwargs={
        "collection": collection.name if hasattr(collection, 'name') else str(collection)
    })
    
    try:
        result = set(collection.get()['ids'])
        log_debug(logger, f"Found {len(result)} existing IDs in collection")
        log_function_return(logger, "get_existing_ids", result)
        return result
    except Exception as e:
        logger.warning(f"Error getting existing IDs: {str(e)}")
        log_function_return(logger, "get_existing_ids", set())
        return set()

def extract_code_example(content: str) -> str:
    """
    Extract code example from content.
    
    Args:
        content: Content to extract code example from
        
    Returns:
        Extracted code example or empty string if none found
    """
    log_function_call(logger, "extract_code_example", kwargs={"content_length": len(content) if content else 0})
    
    if not content:
        log_function_return(logger, "extract_code_example", "")
        return ""
    
    # Look for code blocks in markdown format with "Code Example:" prefix
    if "Code Example:" in content:
        parts = content.split("Code Example:")
        if len(parts) > 1:
            code_part = parts[1].strip()
            # Extract code between ``` markers
            if "```" in code_part:
                code_blocks = code_part.split("```")
                if len(code_blocks) > 1:
                    result = code_blocks[1].strip()
                    log_debug(logger, f"Found code example with 'Code Example:' prefix, length: {len(result)}")
                    log_function_return(logger, "extract_code_example", result)
                    return result
    
    # Look for code blocks in markdown format
    if "```" in content:
        code_blocks = content.split("```")
        if len(code_blocks) > 1:
            result = code_blocks[1].strip()
            log_debug(logger, f"Found code example with markdown format, length: {len(result)}")
            log_function_return(logger, "extract_code_example", result)
            return result
    
    # Look for code blocks in JSON format
    if '"code_example":' in content:
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "code_example" in data:
                result = data["code_example"]
                log_debug(logger, f"Found code example in JSON format, length: {len(result)}")
                log_function_return(logger, "extract_code_example", result)
                return result
        except json.JSONDecodeError:
            log_debug(logger, "Failed to parse JSON content")
    
    log_function_return(logger, "extract_code_example", "")
    return ""

def stream_json_data(file_path: str, collection_name: str) -> Generator[Dict[str, Any], None, None]:
    """
    Stream documents from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        collection_name: Name of the collection
        
    Yields:
        Dict containing document data and metadata
    """
    log_function_call(logger, "stream_json_data", args=(file_path, collection_name))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    log_debug(logger, f"Loaded JSON data from {file_path}, type: {type(data)}")
    
    for chunk in data:
        # Extract content from chunk
        content = chunk.get('content', '')
        if not content:
            # If no content field, try to extract from text field
            content = chunk.get('text', '')
            
        if not content:
            logging.warning(f"No content found in chunk from {file_path}")
            continue
            
        # Create metadata
        metadata = {
            'source': file_path,
            'collection': collection_name,
            'section': chunk.get('section', ''),
            'subsection': chunk.get('subsection', ''),
            'context': chunk.get('context', {})
        }
        
        # Generate unique ID
        doc_id = f"{collection_name}_{hash(content)}"
        
        result = {
            'id': doc_id,
            'content': content,
            'metadata': metadata
        }
        
        log_debug(logger, f"Yielding document with ID: {doc_id}")
        yield result

def initialize_chroma_db(reset_collections=False):
    """
    Initialize ChromaDB with documents from the docs directory.
    
    Args:
        reset_collections: If True, delete existing collections before initializing
    """
    log_function_call(logger, "initialize_chroma_db", kwargs={"reset_collections": reset_collections})
    
    # Initialize ChromaDB client with persistent storage
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    log_debug(logger, f"Initialized ChromaDB client with path: ./chroma_db")
    
    # Define the JSON files to load for each collection
    collection_files = {
        "docs": os.path.join(os.getcwd(), "docs", "bfc_documentation_embeddings_v2.json"),
        "enums": os.path.join(os.getcwd(), "docs", "enums_pessoal_and_folha_with_embeddings.json"),
        "folha": os.path.join(os.getcwd(), "docs", "folha_with_embeddings.json"),
        "pessoal": os.path.join(os.getcwd(), "docs", "pessoal_with_embeddings.json")
    }
    
    log_debug(logger, f"Collection files: {collection_files}")
    
    # Process each collection
    for collection_name, file_path in collection_files.items():
        logger.info(f"Processing collection: {collection_name}")
        
        # Create or get collection
        if reset_collections:
            try:
                client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            except ValueError:
                pass
        
        collection = client.get_or_create_collection(collection_name)
        
        # Get existing IDs to avoid duplicates
        existing_ids = get_existing_ids(collection)
        logger.info(f"Found {len(existing_ids)} existing documents in collection {collection_name}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
        
        try:
            # Load data from JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            log_debug(logger, f"Loaded data from {file_path}, type: {type(data)}")
            
            # Process data based on collection type
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            if collection_name == "docs":
                # Process documentation data - it's a list of objects
                for i, chunk in enumerate(data):
                    content = chunk.get("content", "")
                    embedding = chunk.get("embedding", [])
                    
                    if content and embedding:
                        # Create metadata
                        metadata = {
                            'collection': collection_name,
                            'document': chunk.get("document", ""),
                            'section': chunk.get("section", ""),
                            'contains_code': chunk.get("contains_code", False)
                        }
                        
                        # Generate unique ID using document, section, and index
                        doc_id = f"{collection_name}_{chunk.get('document', '')}_{chunk.get('section', '')}_{i}"
                        
                        # Skip if document already exists
                        if doc_id in existing_ids:
                            continue
                        
                        documents.append(content)
                        embeddings.append(embedding)
                        metadatas.append(metadata)
                        ids.append(doc_id)
                        
                        if is_dev_mode() and i % 100 == 0:
                            log_debug(logger, f"Processed {i} documents for collection {collection_name}")
            
            elif collection_name == "enums":
                # Process enums data - it's a dictionary with enum names as keys
                for enum_name, enum_chunks in data.items():
                    for chunk in enum_chunks:
                        content = chunk.get("content", "")
                        embedding = chunk.get("embedding", [])
                        
                        if content and embedding:
                            # Create metadata
                            metadata = {
                                'collection': collection_name,
                                'enum_name': enum_name,
                                'chunk_key': chunk.get("chunk_key", ""),
                            }
                            
                            # Só adiciona part_number se não for None
                            part_number = chunk.get("part_number")
                            if part_number is not None:
                                metadata['part_number'] = part_number
                            
                            # Generate unique ID
                            doc_id = f"{collection_name}_{enum_name}_{hash(content)}"
                            
                            # Skip if document already exists
                            if doc_id in existing_ids:
                                continue
                            
                            documents.append(content)
                            embeddings.append(embedding)
                            metadatas.append(metadata)
                            ids.append(doc_id)
            
            elif collection_name in ["folha", "pessoal"]:
                # Process folha and pessoal data - it's a dictionary with function names as keys
                for function_name, function_chunks in data.items():
                    for chunk in function_chunks:
                        content = chunk.get("content", "")
                        embedding = chunk.get("embedding", [])
                        
                        if content and embedding:
                            # Create metadata
                            metadata = {
                                'collection': collection_name,
                                'function_name': function_name,
                            }
                            
                            # Generate unique ID
                            doc_id = f"{collection_name}_{function_name}_{hash(content)}"
                            
                            # Skip if document already exists
                            if doc_id in existing_ids:
                                continue
                            
                            documents.append(content)
                            embeddings.append(embedding)
                            metadatas.append(metadata)
                            ids.append(doc_id)
            
            log_debug(logger, f"Found {len(documents)} new documents to add to collection {collection_name}")
            
            # Add documents to collection in batches
            if documents:
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_end = min(i + batch_size, len(documents))
                    batch_docs = documents[i:batch_end]
                    batch_embeddings = embeddings[i:batch_end]
                    batch_metadatas = metadatas[i:batch_end]
                    batch_ids = ids[i:batch_end]
                    
                    log_debug(logger, f"Adding batch {i//batch_size + 1} to collection {collection_name} ({len(batch_docs)} documents)")
                    
                    collection.add(
                        ids=batch_ids,
                        documents=batch_docs,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadatas
                    )
                
                logger.info(f"Added {len(documents)} new documents to collection {collection_name}")
            else:
                logger.info(f"No new documents to add to collection {collection_name}")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            # Log more details about the error
            if collection_name == "docs" and "duplicate" in str(e):
                duplicate_id = str(e).split("duplicates of: ")[1].split(" ")[0]
                logger.error(f"Duplicate ID found: {duplicate_id}")
                # Find documents with this ID
                matching_docs = [i for i, doc_id in enumerate(ids) if doc_id == duplicate_id]
                for idx in matching_docs:
                    logger.error(f"Document with duplicate ID: {metadatas[idx]}")
    
    logger.info("ChromaDB initialization completed successfully!")
    log_function_return(logger, "initialize_chroma_db", None)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize ChromaDB with embeddings")
    parser.add_argument("--reset", action="store_true", help="Reset collections before adding documents")
    args = parser.parse_args()
    
    initialize_chroma_db(reset_collections=args.reset)