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

"""
Esse script serve tanto pro folha quanto pro pessoal.

Basta alterar o input_file para o arquivo que se deseja usar.

O output_dir é onde os chunks serão salvos.

O MAX_TOKENS é o número máximo de tokens que cada chunk pode ter.

"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_generation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("OPENAI_API_KEY environment variable not set. Please set it before running this script.")
    sys.exit(1)

# Define paths
current_dir = Path(__file__).parent.parent.parent
chunks_dir = current_dir / "chunks" / "folha"
output_file = current_dir / "embeddings" / "folha_with_embeddings.json"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Maximum tokens for text-embedding-3-small model
MAX_TOKENS = 8000  # Setting slightly below the 8192 limit for safety

# Function to count tokens
def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    return len(encoding.encode(text))

# Function to split text into smaller chunks if it exceeds token limit
def split_text_if_needed(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    """
    Split text into smaller chunks if it exceeds the token limit.
    This function is more aggressive in splitting to ensure we never exceed the token limit.
    """
    if count_tokens(text) <= max_tokens:
        return [text]
    
    # First try splitting by paragraphs
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        
        # If a single paragraph is too large, split it by sentences
        if paragraph_tokens > max_tokens:
            sentences = paragraph.split('. ')
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)
                
                # If a single sentence is too large, split it by words
                if sentence_tokens > max_tokens:
                    words = sentence.split(' ')
                    current_word_chunk = []
                    current_word_token_count = 0
                    
                    for word in words:
                        word_tokens = count_tokens(word)
                        
                        if current_word_token_count + word_tokens > max_tokens and current_word_chunk:
                            chunks.append(' '.join(current_word_chunk))
                            current_word_chunk = [word]
                            current_word_token_count = word_tokens
                        else:
                            current_word_chunk.append(word)
                            current_word_token_count += word_tokens
                    
                    # Add the last word chunk if it exists
                    if current_word_chunk:
                        chunks.append(' '.join(current_word_chunk))
                # If adding this sentence would exceed the limit, start a new chunk
                elif current_token_count + sentence_tokens > max_tokens and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_token_count = sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_token_count += sentence_tokens
        # If adding this paragraph would exceed the limit, start a new chunk
        elif current_token_count + paragraph_tokens > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_token_count = paragraph_tokens
        else:
            current_chunk.append(paragraph)
            current_token_count += paragraph_tokens
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    # Double-check that all chunks are within the token limit
    final_chunks = []
    for chunk in chunks:
        token_count = count_tokens(chunk)
        if token_count > max_tokens:
            # If any chunk is still too large, split it into smaller pieces
            logger.warning(f"Chunk still has {token_count} tokens, splitting further")
            # Split by characters as a last resort
            char_chunks = []
            current_char_chunk = ""
            current_char_token_count = 0
            
            for char in chunk:
                char_tokens = count_tokens(char)
                if current_char_token_count + char_tokens > max_tokens:
                    char_chunks.append(current_char_chunk)
                    current_char_chunk = char
                    current_char_token_count = char_tokens
                else:
                    current_char_chunk += char
                    current_char_token_count += char_tokens
            
            if current_char_chunk:
                char_chunks.append(current_char_chunk)
            
            final_chunks.extend(char_chunks)
        else:
            final_chunks.append(chunk)
    
    return final_chunks

# Function to create embedding with rate limit handling
def get_embedding(text: str, retries: int = 5, delay: int = 1) -> List[float]:
    for attempt in range(retries):
        try:
            # Double-check token count before sending to API
            token_count = count_tokens(text)
            if token_count > MAX_TOKENS:
                raise ValueError(f"Text has {token_count} tokens, which exceeds the maximum of {MAX_TOKENS}")
                
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                dimensions=512,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds... (Attempt {attempt+1}/{retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Error generating embedding: {str(e)}")
                raise e

# Function to parse chunk filename to extract section name and part number
def parse_chunk_filename(filename: str) -> Dict[str, Any]:
    base_name = os.path.basename(filename)
    
    # Handle type definition files
    if "_type_" in base_name:
        name_parts = base_name.replace(".txt", "").split("_type_")
        section_name = name_parts[0]
        type_name = name_parts[1]
        return {
            "section_name": section_name,
            "type_name": type_name,
            "is_type_definition": True
        }
    
    # Handle regular chunk files
    name_parts = base_name.replace(".txt", "").split("_parts_")
    
    section_name = name_parts[0]
    part_number = int(name_parts[1]) if len(name_parts) > 1 else None
    
    return {
        "section_name": section_name,
        "part_number": part_number,
        "is_type_definition": False
    }

# Function to read and process chunk files
def process_chunk_files() -> Dict[str, List[Dict[str, Any]]]:
    chunk_files = glob.glob(str(chunks_dir / "*.txt"))
    logger.info(f"Found {len(chunk_files)} chunk files")
    
    # Group chunks by section name
    sections = {}
    
    # Use tqdm for progress tracking
    for chunk_file in tqdm(chunk_files, desc="Processing chunks"):
        filename = os.path.basename(chunk_file)
        parsed = parse_chunk_filename(filename)
        section_name = parsed["section_name"]
        
        # Read the chunk content
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            continue
        
        # Check if the chunk is too large and split if needed
        token_count = count_tokens(content)
        if token_count > MAX_TOKENS:
            logger.info(f"Splitting large chunk {filename} with {token_count} tokens")
            sub_chunks = split_text_if_needed(content)
            
            for i, sub_chunk in enumerate(sub_chunks):
                sub_token_count = count_tokens(sub_chunk)
                logger.info(f"  Sub-chunk {i+1}/{len(sub_chunks)}: {sub_token_count} tokens")
                
                # Verify the sub-chunk is within the token limit
                if sub_token_count > MAX_TOKENS:
                    logger.warning(f"  Warning: Sub-chunk {i+1} still has {sub_token_count} tokens, skipping")
                    continue
                
                try:
                    embedding = get_embedding(sub_chunk)
                    chunk_data = {
                        "filename": f"{filename}_sub_{i+1}",
                        "content": sub_chunk,
                        "embedding": embedding,
                        "is_sub_chunk": True,
                        "parent_chunk": filename,
                        "sub_chunk_index": i+1
                    }
                    
                    # Add part number if it exists
                    if "part_number" in parsed:
                        chunk_data["part_number"] = parsed["part_number"]
                    
                    # Add type information if it's a type definition
                    if parsed.get("is_type_definition", False):
                        chunk_data["type_name"] = parsed["type_name"]
                        chunk_data["is_type_definition"] = True
                    
                    sections[section_name] = sections.get(section_name, []) + [chunk_data]
                except Exception as e:
                    logger.error(f"Error generating embedding for sub-chunk {i+1} of {filename}: {str(e)}")
        else:
            try:
                embedding = get_embedding(content)
                chunk_data = {
                    "filename": filename,
                    "content": content,
                    "embedding": embedding
                }
                
                # Add part number if it exists
                if "part_number" in parsed:
                    chunk_data["part_number"] = parsed["part_number"]
                
                # Add type information if it's a type definition
                if parsed.get("is_type_definition", False):
                    chunk_data["type_name"] = parsed["type_name"]
                    chunk_data["is_type_definition"] = True
                
                sections[section_name] = sections.get(section_name, []) + [chunk_data]
            except Exception as e:
                logger.error(f"Error generating embedding for {filename}: {str(e)}")
    
    # Sort chunks by part number within each section
    for section_name in sections:
        sections[section_name] = sorted(
            sections[section_name],
            key=lambda x: (
                x.get("is_type_definition", False),  # Type definitions first
                x.get("part_number", float('inf')),  # Then by part number
                x.get("sub_chunk_index", 0)  # Then by sub-chunk index
            )
        )
    
    return sections

# Main function
def main():
    logger.info("Starting embedding generation process...")
    
    # Check if output file already exists
    if output_file.exists():
        logger.warning(f"Output file {output_file} already exists. It will be overwritten.")
    
    # Process chunks and generate embeddings
    logger.info("Loading chunk files...")
    sections = process_chunk_files()
    
    logger.info("Generating embeddings with OpenAI's text-embedding-3-small model...")
    
    # Save the JSON with embeddings
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(sections, file, indent=4, ensure_ascii=False)
        logger.info(f"Embeddings generated and saved to {output_file}!")
    except Exception as e:
        logger.error(f"Error saving embeddings: {e}")
    
    logger.info(f"Total sections processed: {len(sections)}")
    
    # Print summary
    total_chunks = sum(len(chunks) for chunks in sections.values())
    logger.info(f"Total chunks processed: {total_chunks}")
    
    # Count type definitions
    type_definitions = sum(1 for section in sections.values() 
                          for chunk in section if chunk.get("is_type_definition", False))
    logger.info(f"Type definitions: {type_definitions}")
    
    # Count sub-chunks
    sub_chunks = sum(1 for section in sections.values() 
                    for chunk in section if chunk.get("is_sub_chunk", False))
    logger.info(f"Sub-chunks: {sub_chunks}")

if __name__ == "__main__":
    main() 