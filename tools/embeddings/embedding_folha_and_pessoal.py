import json
import os
import openai
from tqdm import tqdm
import time
from pathlib import Path
import glob
import tiktoken
from typing import Dict, List, Any, Optional
import logging
import sys
import argparse

"""
Script atualizado para gerar embeddings a partir da nova estrutura de chunks v2.

Este script processa os chunks gerados pelo novo sistema que usa:
- MarkdownHeaderTextSplitter do Langchain
- RecursiveCharacterTextSplitter
- Metadados enriquecidos
- Estrutura de arquivos .txt + _summary_metadata.json

Principais melhorias:
1. Compatibilidade com a nova estrutura de chunks v2
2. Uso dos metadados enriquecidos do _summary_metadata.json
3. Preservação de toda a informação de hierarquia semântica
4. Melhor tratamento de código e estruturas complexas
5. Validação robusta de tokens e embeddings
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_generation_v2.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("OPENAI_API_KEY environment variable not set. Please set it before running this script.")
    sys.exit(1)

# Maximum tokens for text-embedding-3-small model
MAX_TOKENS = 7500  # Slightly below 8192 limit for safety, matching chunking script
EMBEDDING_DIMENSIONS = 512  # Using 512 dimensions for efficiency

def count_tokens(text: str) -> int:
    """Count tokens using the same encoding as the chunking script."""
    try:
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def validate_chunk_content(content: str, chunk_id: str) -> bool:
    """Validate chunk content before sending to embedding API."""
    if not content or not content.strip():
        logger.warning(f"Empty content for chunk {chunk_id}")
        return False
    
    token_count = count_tokens(content)
    if token_count > MAX_TOKENS:
        logger.error(f"Chunk {chunk_id} has {token_count} tokens, exceeds limit of {MAX_TOKENS}")
        return False
    
    if token_count < 10:  # Very short content might not be meaningful
        logger.warning(f"Very short content ({token_count} tokens) for chunk {chunk_id}")
    
    return True

def get_embedding_with_retry(text: str, chunk_id: str, retries: int = 5) -> Optional[List[float]]:
    """Generate embedding with exponential backoff retry logic."""
    for attempt in range(retries):
        try:
            # Final validation before API call
            if not validate_chunk_content(text, chunk_id):
                return None
            
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                dimensions=EMBEDDING_DIMENSIONS,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Validate embedding
            if len(embedding) != EMBEDDING_DIMENSIONS:
                logger.error(f"Unexpected embedding dimension for {chunk_id}: {len(embedding)}")
                return None
            
            return embedding
            
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < retries - 1:
                wait_time = (2 ** attempt) * 1  # Exponential backoff starting with 1 second
                logger.warning(f"Rate limit hit for {chunk_id}, waiting {wait_time}s... (Attempt {attempt+1}/{retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Error generating embedding for {chunk_id}: {str(e)}")
                if attempt == retries - 1:
                    return None
    
    return None

def load_chunks_metadata(chunks_base_dir: Path, input_name: str) -> Optional[Dict[str, Any]]:
    """Load the metadata summary file from the base chunks directory."""
    # The metadata file is in the base directory with a specific naming pattern
    metadata_file = chunks_base_dir / f"chunks_enchanced{input_name}_summary_metadata.json"
    
    if not metadata_file.exists():
        logger.error(f"Metadata file not found: {metadata_file}")
        logger.info(f"Expected file: chunks_enchanced{input_name}_summary_metadata.json")
        return None
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        logger.info(f"Loaded metadata for {len(metadata)} chunks from {metadata_file}")
        return metadata
    except Exception as e:
        logger.error(f"Error loading metadata file: {str(e)}")
        return None

def process_chunks_v2(chunks_base_dir: Path, input_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """Process chunks using the new v2 structure with enhanced metadata."""
    
    # Load metadata from the base directory
    chunks_metadata = load_chunks_metadata(chunks_base_dir, input_name)
    if not chunks_metadata:
        logger.error("Cannot proceed without metadata file")
        return {}
    
    # The actual chunks are in a subdirectory
    chunks_dir = chunks_base_dir / input_name
    
    if not chunks_dir.exists():
        logger.error(f"Chunks subdirectory not found: {chunks_dir}")
        return {}
    
    # Group chunks by original section name for compatibility with existing structure
    sections = {}
    
    # Process each chunk
    for chunk_meta in tqdm(chunks_metadata, desc=f"Processing {input_name} chunks v2"):
        chunk_id = chunk_meta["chunk_id"]
        file_path = chunk_meta["file_path"]
        token_count = chunk_meta["token_count"]
        metadata = chunk_meta["metadata"]
        
        # The file_path in metadata is relative to chunks_enhanced_v2/
        # So we need to construct the full path from chunks_base_dir
        full_file_path = chunks_base_dir / file_path
        
        # Alternative: if file_path is just the filename, look in the subdirectory
        if not full_file_path.exists():
            # Try looking in the subdirectory
            filename = Path(file_path).name
            full_file_path = chunks_dir / filename
        
        if not full_file_path.exists():
            logger.warning(f"Chunk file not found: {full_file_path}")
            logger.warning(f"Tried: {chunks_base_dir / file_path} and {chunks_dir / filename}")
            continue
        
        # Read chunk content
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading chunk file {full_file_path}: {str(e)}")
            continue
        
        # Validate content token count matches metadata
        actual_token_count = count_tokens(content)
        if abs(actual_token_count - token_count) > 10:  # Allow small variance
            logger.warning(f"Token count mismatch for {chunk_id}: metadata={token_count}, actual={actual_token_count}")
        
        # Generate embedding
        embedding = get_embedding_with_retry(content, chunk_id)
        if embedding is None:
            logger.error(f"Failed to generate embedding for {chunk_id}")
            continue
        
        # Extract section name for grouping
        original_section_name = metadata.get("original_section_name", "unknown_section")
        
        # Prepare chunk data with enhanced metadata
        chunk_data = {
            "chunk_key": chunk_id,  # Unique identifier
            "content": content,
            "embedding": embedding,
            
            # Original metadata from chunking process
            "source_document_id": metadata.get("source_document_id"),
            "original_section_name": original_section_name,
            "langchain_doc_index": metadata.get("langchain_doc_index"),
            "chunk_index_in_lc_doc": metadata.get("chunk_index_in_lc_doc"),
            "total_chunks_in_lc_doc": metadata.get("total_chunks_in_lc_doc"),
            "extracted_headers": metadata.get("extracted_headers", {}),
            "title": metadata.get("title"),
            "code_block_count": metadata.get("code_block_count", 0),
            "keywords": metadata.get("keywords", []),
            
            # Token information
            "token_count": actual_token_count,
            "embedding_dimensions": len(embedding),
            
            # Processing metadata
            "chunk_file_path": str(file_path),
            "processing_timestamp": time.time(),
            
            # Content classification
            "has_code": metadata.get("code_block_count", 0) > 0,
            "content_type": classify_content_type(content, metadata),
            "semantic_level": determine_semantic_level(metadata.get("extracted_headers", {}))
        }
        
        # Add part number if available (for compatibility)
        if "chunk_index_in_lc_doc" in metadata:
            chunk_data["part_number"] = metadata["chunk_index_in_lc_doc"]
        
        # Group by section name
        if original_section_name not in sections:
            sections[original_section_name] = []
        sections[original_section_name].append(chunk_data)
    
    # Sort chunks within each section by hierarchical order
    for section_name in sections:
        sections[section_name] = sorted(
            sections[section_name],
            key=lambda x: (
                x.get("langchain_doc_index", 0),  # Document order from markdown splitter
                x.get("chunk_index_in_lc_doc", 0)  # Chunk order within document
            )
        )
    
    return sections

def classify_content_type(content: str, metadata: Dict[str, Any]) -> str:
    """Classify content type based on content and metadata."""
    content_lower = content.lower()
    headers = metadata.get("extracted_headers", {})
    
    # Check for code examples
    if "```" in content or "code example" in content_lower:
        return "code_example"
    
    # Check for type definitions
    if "types:" in content_lower or "type:" in content_lower:
        return "type_definition"
    
    # Check for expressions/filters
    if "expressions:" in content_lower or "expression" in content_lower:
        return "expression_definition"
    
    # Check for method descriptions
    if "method:" in content_lower and "description" in content_lower:
        return "method_documentation"
    
    # Check header information
    if "h3" in headers and ("type" in headers["h3"].lower() or "method" in headers["h3"].lower()):
        return "api_documentation"
    
    # Default classification
    return "general_documentation"

def determine_semantic_level(headers: Dict[str, str]) -> str:
    """Determine semantic level based on extracted headers."""
    if "h3" in headers:
        return "detailed"
    elif "h2" in headers:
        return "section"
    elif "h1" in headers:
        return "overview"
    else:
        return "fragment"

def validate_sections_data(sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Validate the processed sections data and return statistics."""
    stats = {
        "total_sections": len(sections),
        "total_chunks": 0,
        "total_embeddings": 0,
        "content_types": {},
        "semantic_levels": {},
        "has_code_chunks": 0,
        "avg_token_count": 0,
        "token_distribution": {"min": float('inf'), "max": 0},
        "embedding_dimensions_consistent": True,
        "errors": []
    }
    
    all_token_counts = []
    expected_dims = EMBEDDING_DIMENSIONS
    
    for section_name, chunks in sections.items():
        stats["total_chunks"] += len(chunks)
        
        for chunk in chunks:
            # Count embeddings
            if chunk.get("embedding"):
                stats["total_embeddings"] += 1
                
                # Check embedding dimensions
                if len(chunk["embedding"]) != expected_dims:
                    stats["embedding_dimensions_consistent"] = False
                    stats["errors"].append(f"Dimension mismatch in {chunk.get('chunk_key', 'unknown')}")
            
            # Content type statistics
            content_type = chunk.get("content_type", "unknown")
            stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1
            
            # Semantic level statistics
            semantic_level = chunk.get("semantic_level", "unknown")
            stats["semantic_levels"][semantic_level] = stats["semantic_levels"].get(semantic_level, 0) + 1
            
            # Code statistics
            if chunk.get("has_code", False):
                stats["has_code_chunks"] += 1
            
            # Token statistics
            token_count = chunk.get("token_count", 0)
            if token_count > 0:
                all_token_counts.append(token_count)
                stats["token_distribution"]["min"] = min(stats["token_distribution"]["min"], token_count)
                stats["token_distribution"]["max"] = max(stats["token_distribution"]["max"], token_count)
    
    # Calculate averages
    if all_token_counts:
        stats["avg_token_count"] = sum(all_token_counts) / len(all_token_counts)
        stats["token_distribution"]["avg"] = stats["avg_token_count"]
    
    if stats["token_distribution"]["min"] == float('inf'):
        stats["token_distribution"]["min"] = 0
    
    return stats

def save_embeddings_with_validation(sections: Dict[str, List[Dict[str, Any]]], output_file: Path):
    """Save embeddings with validation and backup."""
    
    # Validate data before saving
    stats = validate_sections_data(sections)
    
    logger.info("=== VALIDATION RESULTS ===")
    logger.info(f"Total sections: {stats['total_sections']}")
    logger.info(f"Total chunks: {stats['total_chunks']}")
    logger.info(f"Total embeddings: {stats['total_embeddings']}")
    logger.info(f"Average tokens per chunk: {stats['avg_token_count']:.1f}")
    logger.info(f"Token range: {stats['token_distribution']['min']} - {stats['token_distribution']['max']}")
    logger.info(f"Chunks with code: {stats['has_code_chunks']}")
    logger.info(f"Content types: {stats['content_types']}")
    logger.info(f"Semantic levels: {stats['semantic_levels']}")
    logger.info(f"Embedding dimensions consistent: {stats['embedding_dimensions_consistent']}")
    
    if stats["errors"]:
        logger.warning(f"Validation errors found: {len(stats['errors'])}")
        for error in stats["errors"][:5]:  # Show first 5 errors
            logger.warning(f"  - {error}")
    
    # Create backup if file exists
    if output_file.exists():
        backup_file = output_file.with_suffix(f".backup_{int(time.time())}.json")
        logger.info(f"Creating backup: {backup_file}")
        try:
            import shutil
            shutil.copy2(output_file, backup_file)
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
    
    # Save the main file
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(sections, file, indent=2, ensure_ascii=False)
        logger.info(f"Embeddings saved successfully to {output_file}")
        
        # Save validation stats separately
        stats_file = output_file.with_suffix(".stats.json")
        with open(stats_file, "w", encoding="utf-8") as file:
            json.dump(stats, file, indent=2, ensure_ascii=False)
        logger.info(f"Validation stats saved to {stats_file}")
        
    except Exception as e:
        logger.error(f"Error saving embeddings: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for enhanced chunks v2")
    parser.add_argument("--input", "-i", type=str, default="pessoal", 
                       help="Input folder name (pessoal or folha)")
    parser.add_argument("--chunks-base-dir", type=str, default=None,
                       help="Base directory for chunks (default: project_root/chunks_enhanced_v2)")
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Output directory for embeddings (default: project_root/embeddings_v2)")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force overwrite existing embeddings file")
    
    args = parser.parse_args()
    
    # Define paths
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # Adjust based on your project structure
    
    # Set default paths
    if args.chunks_base_dir:
        chunks_base_dir = Path(args.chunks_base_dir)
    else:
        chunks_base_dir = project_root / "chunks_enhanced_v2"
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "embeddings_v2"
    
    # Specific paths for this run
    chunks_subdir = chunks_base_dir / args.input  # The subfolder with actual chunk files
    output_file = output_dir / f"{args.input}_with_embeddings_v2.json"
    metadata_file = chunks_base_dir / f"chunks_enchanced{args.input}_summary_metadata.json"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=== EMBEDDING GENERATION V2 ===")
    logger.info(f"Chunks base directory: {chunks_base_dir}")
    logger.info(f"Chunks subdirectory: {chunks_subdir}")
    logger.info(f"Metadata file: {metadata_file}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Max tokens per chunk: {MAX_TOKENS}")
    logger.info(f"Embedding dimensions: {EMBEDDING_DIMENSIONS}")
    
    # Validate input directories and files
    if not chunks_base_dir.exists():
        logger.error(f"Chunks base directory not found: {chunks_base_dir}")
        sys.exit(1)
    
    if not chunks_subdir.exists():
        logger.error(f"Chunks subdirectory not found: {chunks_subdir}")
        logger.error(f"Expected structure: {chunks_base_dir}/{args.input}/")
        sys.exit(1)
    
    if not metadata_file.exists():
        logger.error(f"Metadata file not found: {metadata_file}")
        logger.error(f"Expected file: chunks_enchanced{args.input}_summary_metadata.json")
        sys.exit(1)
    
    # Check if output file exists
    if output_file.exists() and not args.force:
        response = input(f"Output file {output_file} exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            logger.info("Aborted by user")
            sys.exit(0)
    
    # Process chunks
    logger.info("Starting embedding generation...")
    start_time = time.time()
    
    try:
        sections = process_chunks_v2(chunks_base_dir, args.input)
        
        if not sections:
            logger.error("No sections were processed successfully")
            sys.exit(1)
        
        # Save results
        save_embeddings_with_validation(sections, output_file)
        
        # Final summary
        processing_time = time.time() - start_time
        total_chunks = sum(len(chunks) for chunks in sections.values())
        
        logger.info("=== PROCESSING COMPLETE ===")
        logger.info(f"Total processing time: {processing_time:.2f} seconds")
        logger.info(f"Total sections processed: {len(sections)}")
        logger.info(f"Total chunks processed: {total_chunks}")
        logger.info(f"Average time per chunk: {processing_time/total_chunks:.2f} seconds")
        logger.info(f"Output saved to: {output_file}")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()