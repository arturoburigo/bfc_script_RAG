import json
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EnumChunk:
    enum_name: str
    content: Dict[str, Any]
    parent_enum: str = None
    continuation_index: int = None

def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from the specified file path
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_value_description(value: Dict[str, Any]) -> str:
    """
    Safely extract description from a value, handling different JSON structures
    """
    description = value.get('description', '')
    if not description:
        # If no description, try to get it from the key
        description = value.get('key', '').replace('_', ' ').title()
    
    key = value.get('key', '')
    val = value.get('value', '')
    
    return f"- {description} (Key: {key}, Value: {val})"

def convert_enum_to_text(enum_name: str, enum_data: Dict[str, Any]) -> str:
    """
    Convert an enum object to a readable text format
    """
    text_parts = [f"Enum: {enum_name}"]
    
    if "values" in enum_data:
        for value in enum_data["values"]:
            try:
                text_parts.append(get_value_description(value))
            except Exception as e:
                print(f"Warning: Could not process value in enum {enum_name}: {value}")
                text_parts.append(f"- Value: {str(value)}")
    
    return "\n".join(text_parts)

def split_large_enum(enum_name: str, enum_data: Dict[str, Any], max_values_per_chunk: int = 20) -> List[EnumChunk]:
    """
    Split a large enum into multiple chunks while maintaining context
    """
    chunks = []
    values = enum_data.get("values", [])
    
    for i in range(0, len(values), max_values_per_chunk):
        chunk_values = values[i:i + max_values_per_chunk]
        chunk_data = {"values": chunk_values}
        
        continuation_index = (i // max_values_per_chunk) + 1 if i > 0 else None
        chunks.append(EnumChunk(
            enum_name=enum_name,
            content=chunk_data,
            continuation_index=continuation_index
        ))
    
    return chunks

def create_chunks_from_json(json_data: Dict[str, Any], max_values_per_chunk: int = 20) -> List[EnumChunk]:
    """
    Create chunks from JSON data while maintaining enum integrity
    """
    chunks = []
    
    for enum_name, enum_data in json_data.items():
        try:
            # Count the number of values in this enum
            num_values = len(enum_data.get("values", []))
            
            if num_values > max_values_per_chunk:
                # If enum is too large, split it into multiple chunks
                enum_chunks = split_large_enum(enum_name, enum_data, max_values_per_chunk)
                chunks.extend(enum_chunks)
            else:
                # Keep small enums as single chunks
                chunks.append(EnumChunk(enum_name=enum_name, content=enum_data))
        except Exception as e:
            print(f"Warning: Could not process enum {enum_name}: {str(e)}")
    
    return chunks

def save_chunks(chunks: List[EnumChunk], output_dir: str):
    """
    Save chunks as text files with context preservation
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for i, chunk in enumerate(chunks):
        try:
            # Create filename
            base_filename = chunk.enum_name
            if chunk.continuation_index is not None:
                base_filename += f"_part_{chunk.continuation_index}"
            
            chunk_file = output_path / f"{base_filename}.txt"
            
            # Create the text content with context
            content_lines = [f"# {chunk.enum_name}"]
            if chunk.continuation_index is not None:
                content_lines.append(f"# Part {chunk.continuation_index}")
                content_lines.append(f"# This is a continuation of the {chunk.enum_name} enum")
            
            # Convert enum data to text
            enum_text = convert_enum_to_text(chunk.enum_name, chunk.content)
            content_lines.append(enum_text)
            
            # Save the file
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content_lines))
        except Exception as e:
            print(f"Warning: Could not save chunk for {chunk.enum_name}: {str(e)}")

def main():
    # Define paths
    current_dir = Path(__file__).parent.parent.parent
    input_file = current_dir / "docs" / "enums_pessoal_and_folha.json"
    output_dir = current_dir / "chunks" / "enums_pessoal_and_folha"
    
    print(f"Reading enums from: {input_file}")
    
    # Load JSON data
    json_data = load_json_data(input_file)
    
    # Create chunks
    chunks = create_chunks_from_json(json_data)
    
    # Save chunks
    save_chunks(chunks, output_dir)
    print(f"Created {len(chunks)} chunks in {output_dir}")

if __name__ == "__main__":
    main()
