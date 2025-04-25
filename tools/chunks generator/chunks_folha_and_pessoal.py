import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import tiktoken

"""
Esse script serve tanto pro folha quanto pro pessoal.

Basta alterar o input_file para o arquivo que se deseja usar.

O output_dir é onde os chunks serão salvos.

O MAX_TOKENS é o número máximo de tokens que cada chunk pode ter.


"""

@dataclass
class Chunk:
    section_name: str
    content: Dict[str, Any]
    chunk_index: Optional[int] = None
    parent_section: Optional[str] = None

# Maximum tokens for text-embedding-3-large model
MAX_TOKENS = 7500  # Setting slightly below the 8192 limit for safety

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text using the tiktoken library
    """
    encoding = tiktoken.encoding_for_model("text-embedding-3-large")
    return len(encoding.encode(text))

def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from the specified file path
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def format_code_example(code_example: str, max_length: int = 1000) -> List[str]:
    """
    Format a code example into multiple chunks if it's too long
    """
    if not code_example or len(code_example) <= max_length:
        return [code_example]
    
    # Split by newlines to preserve code structure
    lines = code_example.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_length = len(line) + 1  # +1 for the newline character
        
        if current_length + line_length > max_length and current_chunk:
            # Current chunk is full, save it and start a new one
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            # Add line to current chunk
            current_chunk.append(line)
            current_length += line_length
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def convert_to_text(data: Dict[str, Any], section_name: str) -> str:
    """
    Convert a JSON object to a readable text format
    """
    text_parts = [f"# {section_name}"]
    
    # Add description if available
    if "description" in data:
        text_parts.append(f"Description: {data['description']}")
    
    # Add method information if available
    if "method" in data:
        method = data["method"]
        text_parts.append(f"Method: {method.get('name', 'N/A')} ({method.get('verb', 'N/A')})")
        if "description" in method:
            text_parts.append(f"Method Description: {method['description']}")
    
    # Add representation if available
    if "representation" in data:
        rep = data["representation"]
        text_parts.append(f"Representation Type: {rep.get('type', 'N/A')}")
    
    # Add expressions if available
    if "expressions" in data and data["expressions"]:
        text_parts.append("Expressions:")
        for key, value in data["expressions"].items():
            if isinstance(value, dict):
                desc = value.get("description", "")
                type_info = value.get("type", "")
                text_parts.append(f"- {key}: {desc} (Type: {type_info})")
            else:
                text_parts.append(f"- {key}")
    
    # Add types if available
    if "types" in data and data["types"]:
        text_parts.append("Types:")
        for type_name, type_data in data["types"].items():
            text_parts.append(f"## {type_name}")
            for field, field_data in type_data.items():
                if isinstance(field_data, dict):
                    desc = field_data.get("description", "")
                    type_info = field_data.get("type", "")
                    text_parts.append(f"- {field}: {desc} (Type: {type_info})")
                else:
                    text_parts.append(f"- {field}")
    
    # Add code example if available
    if "codeExample" in data:
        text_parts.append("Code Example:")
        code_chunks = format_code_example(data["codeExample"])
        for i, chunk in enumerate(code_chunks):
            if len(code_chunks) > 1:
                text_parts.append(f"### Part {i+1}")
            text_parts.append("```")
            text_parts.append(chunk)
            text_parts.append("```")
    
    return "\n".join(text_parts)
def split_text_by_tokens(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    """
    Split text into chunks based on token count while preserving structure.
    Guarantees that no chunk will exceed max_tokens.
    """
    if count_tokens(text) <= max_tokens:
        return [text]
    
    # Split by paragraphs first
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
                
                # If a single sentence is too large, split it by force
                if sentence_tokens > max_tokens:
                    print(f"Warning: Found a very large sentence ({sentence_tokens} tokens). Forcing split.")
                    # Force split by tokens using the encoding directly
                    encoding = tiktoken.encoding_for_model("text-embedding-3-large")
                    sentence_tokens_list = encoding.encode(sentence)
                    
                    # Split tokens into smaller chunks
                    for i in range(0, len(sentence_tokens_list), max_tokens - 100):  # 100 token buffer
                        chunk_tokens = sentence_tokens_list[i:i + max_tokens - 100]
                        chunk_text = encoding.decode(chunk_tokens)
                        if current_chunk:
                            chunks.append('\n\n'.join(current_chunk))
                            current_chunk = []
                            current_token_count = 0
                        chunks.append(chunk_text)
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
    
    # Final verification - this is critical to ensure no chunk exceeds the limit
    verified_chunks = []
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)
        if chunk_tokens > max_tokens:
            print(f"Warning: Chunk still has {chunk_tokens} tokens after splitting. Forcing hard split.")
            # Force split using token encoding as a last resort
            encoding = tiktoken.encoding_for_model("text-embedding-3-large")
            chunk_tokens_list = encoding.encode(chunk)
            for i in range(0, len(chunk_tokens_list), max_tokens - 100):  # 100 token buffer
                sub_chunk_tokens = chunk_tokens_list[i:i + max_tokens - 100]
                sub_chunk = encoding.decode(sub_chunk_tokens)
                verified_chunks.append(sub_chunk)
        else:
            verified_chunks.append(chunk)
    
    return verified_chunks

def split_large_section(section_name: str, section_data: Dict[str, Any], max_chunk_size: int = 10000) -> List[Chunk]:
    """
    Split a large section into multiple chunks while maintaining context
    """
    chunks = []
    
    # Convert the section to text to check token count
    section_text = convert_to_text(section_data, section_name)
    token_count = count_tokens(section_text)
    
    # If the section is too large, split it by tokens
    if token_count > MAX_TOKENS:
        print(f"Splitting large section {section_name} with {token_count} tokens")
        
        # Split the text into smaller chunks
        text_chunks = split_text_by_tokens(section_text)
        
        # Create chunks for each text chunk
        for i, text_chunk in enumerate(text_chunks):
            # Create a simplified content object for this chunk
            chunk_content = {
                "description": section_data.get("description", ""),
                "name": section_data.get("name", ""),
                "content": text_chunk
            }
            
            chunks.append(Chunk(
                section_name=section_name,
                content=chunk_content,
                chunk_index=i+1
            ))
    # Check if the section has a code example that needs special handling
    elif "codeExample" in section_data and len(section_data["codeExample"]) > max_chunk_size:
        # Create a base chunk without the code example
        base_data = section_data.copy()
        base_data.pop("codeExample")
        
        # Add the base chunk
        chunks.append(Chunk(
            section_name=section_name,
            content=base_data
        ))
        
        # Create separate chunks for the code example
        code_chunks = format_code_example(section_data["codeExample"])
        for i, code_chunk in enumerate(code_chunks):
            code_data = {"codeExample": code_chunk}
            chunks.append(Chunk(
                section_name=f"{section_name}_code",
                content=code_data,
                chunk_index=i+1,
                parent_section=section_name
            ))
    else:
        # If the section is not too large, keep it as a single chunk
        chunks.append(Chunk(
            section_name=section_name,
            content=section_data
        ))
    
    return chunks

def create_chunks_from_json(json_data: Dict[str, Any], max_chunk_size: int = 10000) -> List[Chunk]:
    """
    Create chunks from JSON data while maintaining section integrity
    """
    chunks = []
    
    for section_name, section_data in json_data.items():
        try:
            # Convert the section to text to estimate its size
            section_text = convert_to_text(section_data, section_name)
            
            if len(section_text) > max_chunk_size:
                # If section is too large, split it
                section_chunks = split_large_section(section_name, section_data, max_chunk_size)
                chunks.extend(section_chunks)
            else:
                # Keep small sections as single chunks
                chunks.append(Chunk(section_name=section_name, content=section_data))
        except Exception as e:
            print(f"Warning: Could not process section {section_name}: {str(e)}")
    
    return chunks

def save_chunks(chunks: List[Chunk], output_dir: str):
    """
    Save chunks as text files with context preservation
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for i, chunk in enumerate(chunks):
        try:
            # Create filename
            base_filename = chunk.section_name
            if chunk.chunk_index is not None:
                base_filename += f"_parts_{chunk.chunk_index}"
            
            chunk_file = output_path / f"{base_filename}.txt"
            
            # Create the text content with context
            if "content" in chunk.content:
                # For chunks that were split by token count
                content_text = chunk.content["content"]
            else:
                # For regular chunks
                content_text = convert_to_text(chunk.content, chunk.section_name)
            
            # Add context information if this is a continuation
            if chunk.chunk_index is not None:
                context_lines = [
                    f"# Part {chunk.chunk_index}",
                    f"# This is a continuation of the {chunk.section_name} section"
                ]
                if chunk.parent_section:
                    context_lines.append(f"# Parent section: {chunk.parent_section}")
                
                # Insert context at the beginning
                content_lines = content_text.split('\n')
                content_lines = context_lines + content_lines
                content_text = '\n'.join(content_lines)
            
            # Save the file
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(content_text)
        except Exception as e:
            print(f"Warning: Could not save chunk for {chunk.section_name}: {str(e)}")

def main():
    # Define paths
    current_dir = Path(__file__).parent.parent.parent
    input_file = current_dir / "docs" / "folha.json"
    output_dir = current_dir / "chunks" / "folha"
    
    print(f"Reading content from: {input_file}")
    
    # Load JSON data
    json_data = load_json_data(input_file)
    
    # Create chunks
    chunks = create_chunks_from_json(json_data)
    
    # Save chunks
    save_chunks(chunks, output_dir)
    print(f"Created {len(chunks)} chunks in {output_dir}")

if __name__ == "__main__":
    main() 