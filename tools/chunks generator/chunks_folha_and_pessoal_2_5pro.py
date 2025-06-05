import json
import re # Added for new code block extraction
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

"""
Esse script serve tanto pro folha quanto pro pessoal.
Basta alterar o input_file para o arquivo que se deseja usar.
O output_dir é onde os chunks serão salvos.
O MAX_TOKENS é o número máximo de tokens que cada chunk pode ter.

Melhorias implementadas:
1.  Uso aprimorado de Langchain (MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter).
2.  Estratégia de Chunking Mais Inteligente:
    - Usa MarkdownHeaderTextSplitter para divisão semântica baseada em cabeçalhos gerados.
    - Preservação robusta de blocos de código durante a divisão.
    - RecursiveCharacterTextSplitter para divisão fina por tokens.
3.  Melhor Estrutura de Metadados:
    - Dataclass Chunk enriquecida com ID, document_id, metadados detalhados.
    - Geração de um arquivo _summary_metadata.json com informações de todos os chunks.
4.  Estratégia de Overlap Melhorada: O overlap é gerenciado pelo RecursiveCharacterTextSplitter
    e pode ser configurado.
5.  Pré-processamento para RAG:
    - Texto de saída limpo e estruturado.
    - Metadados ricos para auxiliar na recuperação.
6.  Validação e Qualidade:
    - Pula chunks vazios.
    - Tratamento de erro aprimorado por seção.
7.  Pipeline Completo Otimizado:
    - Estrutura de código mais clara e modular.
    - Pathing aprimorado com pathlib.
"""

@dataclass
class Chunk:
    id: str
    document_id: str
    original_section_name: str # Top-level section name from JSON for overall context
    content_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: Optional[int] = None

# Maximum tokens for text-embedding-3-small model
MAX_TOKENS = 7500  # Setting slightly below the 8192 limit for safety. Adjust as needed for your RAG strategy.
TOKEN_OVERLAP = 200 # Default overlap, configurable in main.

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text using the tiktoken library.
    """
    try:
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    except Exception:
        # Fallback if the specific model encoding is not found (e.g., offline or tiktoken version)
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from the specified file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_full_code_blocks(text: str) -> List[str]:
    """
    Extracts full code blocks (including ``` markers) from text.
    Handles various forms of code blocks.
    """
    # Regex to find code blocks: ``` optionally followed by a language, then content, then ```
    # It handles blocks on the same line or multiple lines. Non-greedy match for content.
    # re.DOTALL allows . to match newlines within the code block.
    pattern = re.compile(r"```(?:[a-zA-Z0-9_.-]*)?\n.*?\n```|```.*?```", re.DOTALL)
    return pattern.findall(text)

def convert_to_text(data: Dict[str, Any], section_name: str) -> str:
    """
    Convert a JSON object to a readable text format using Markdown-like headers.
    This structure aids semantic chunking with MarkdownHeaderTextSplitter.
    """
    text_parts = [f"# {section_name}"] # Main section as H1

    if "description" in data:
        text_parts.append(f"## Description\n{data['description']}") # Subsection as H2
    
    if "method" in data:
        method = data["method"]
        text_parts.append(f"## Method: {method.get('name', 'N/A')} ({method.get('verb', 'N/A')})")
        if "description" in method:
            text_parts.append(f"### Method Description\n{method['description']}") # Sub-subsection as H3
    
    if "representation" in data:
        rep = data["representation"]
        text_parts.append(f"## Representation\nType: {rep.get('type', 'N/A')}")
    
    if "expressions" in data and data["expressions"]:
        text_parts.append("## Expressions")
        for key, value in data["expressions"].items():
            if isinstance(value, dict):
                desc = value.get("description", "")
                type_info = value.get("type", "")
                text_parts.append(f"- **{key}**: {desc} (Type: {type_info})")
            else:
                text_parts.append(f"- **{key}**")
    
    if "types" in data and data["types"]:
        text_parts.append("## Types")
        for type_name, type_data in data["types"].items():
            text_parts.append(f"### Type: {type_name}") # Type name as H3
            for field, field_data in type_data.items():
                if isinstance(field_data, dict):
                    desc = field_data.get("description", "")
                    type_info = field_data.get("type", "")
                    text_parts.append(f"- **{field}**: {desc} (Type: {type_info})")
                else:
                    text_parts.append(f"- **{field}**")
    
    if "codeExample" in data:
        text_parts.append("## Code Example")
        text_parts.append("```") # Assuming generic code block, add language if known
        text_parts.append(data["codeExample"])
        text_parts.append("```")
    
    return "\n\n".join(text_parts) # Add more spacing for clarity

def process_section_into_chunks(
    document_id: str,
    original_section_name: str,
    section_data: Dict[str, Any],
    max_tokens_per_chunk: int,
    chunk_overlap_tokens: int
) -> List[Chunk]:
    """
    Processes a single section from the JSON data, converting it to text,
    and then splitting it into manageable chunks using a hierarchical approach.
    """
    
    full_section_text = convert_to_text(section_data, original_section_name)
    
    headers_to_split_on = [
        ("# ", "h1"),
        ("## ", "h2"),
        ("### ", "h3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False # Keep headers in content
    )
    # Langchain's MarkdownHeaderTextSplitter returns Document objects
    # Each Document has page_content and metadata (with extracted headers)
    langchain_docs = markdown_splitter.split_text(full_section_text)
    
    final_chunks: List[Chunk] = []
    # Ensure unique chunk IDs across the entire document processing
    # This counter should ideally be managed at a higher level if processing multiple input files
    # or be based on a hash for true uniqueness. For simplicity here, it's per-section.
    # A UUID approach for chunk.id would be more robust.
    # For now, constructing a descriptive ID.
    
    chunk_counter_for_section = 0

    for lc_doc_idx, lc_doc in enumerate(langchain_docs):
        content_to_split = lc_doc.page_content
        # Preserve code blocks before further splitting
        code_blocks = extract_full_code_blocks(content_to_split)
        placeholders = {}
        
        for i, block_str in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_PLACEHOLDER_{i}_{lc_doc_idx}__" # Make placeholder unique per lc_doc
            placeholders[placeholder] = block_str
            content_to_split = content_to_split.replace(block_str, placeholder, 1)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens_per_chunk,
            chunk_overlap=chunk_overlap_tokens,
            separators=["\n\n", "\n", ". ", " ", ""], # Common separators
            length_function=count_tokens,
            add_start_index=False, # We are not using start index directly here
        )
        
        split_texts = text_splitter.split_text(content_to_split)
        
        for part_idx, text_part in enumerate(split_texts):
            # Restore code blocks
            final_content_part = text_part
            for placeholder, block_str_restored in placeholders.items():
                if placeholder in final_content_part:
                    final_content_part = final_content_part.replace(placeholder, block_str_restored)

            current_token_count = count_tokens(final_content_part)
            if current_token_count == 0 or not final_content_part.strip():
                continue # Skip empty or whitespace-only chunks

            chunk_counter_for_section += 1
            # Create a more descriptive chunk ID
            header_suffix = "_".join(str(v) for v in lc_doc.metadata.values()).replace(" ", "_").replace("#","").strip()
            if not header_suffix:
                 header_suffix = f"part{lc_doc_idx}"

            chunk_id = f"{document_id}_{original_section_name.replace(' ', '_')}_{header_suffix}_{part_idx+1}"
            # Sanitize chunk_id for filesystem
            chunk_id = re.sub(r'[^\w\-_.]', '_', chunk_id)


            chunk_metadata = {
                "source_document_id": document_id,
                "original_section_name": original_section_name,
                "langchain_doc_index": lc_doc_idx, # Index from MarkdownHeaderTextSplitter
                "chunk_index_in_lc_doc": part_idx + 1,
                "total_chunks_in_lc_doc": len(split_texts),
                "extracted_headers": lc_doc.metadata, # Headers from MarkdownHeaderTextSplitter
                "title": lc_doc.metadata.get("h3") or lc_doc.metadata.get("h2") or lc_doc.metadata.get("h1") or original_section_name,
                "code_block_count": len(extract_full_code_blocks(final_content_part)), # Count code blocks in the final chunk
                 # Future: Add keywords, summary
                "keywords": [], 
                "summary_placeholder": ""
            }
            
            final_chunks.append(Chunk(
                id=chunk_id,
                document_id=document_id,
                original_section_name=original_section_name,
                content_text=final_content_part,
                metadata=chunk_metadata,
                token_count=current_token_count
            ))
            
    return final_chunks

def create_document_chunks(
    json_data: Dict[str, Any],
    document_id: str,
    max_tokens_per_chunk: int,
    chunk_overlap_tokens: int
) -> List[Chunk]:
    """
    Iterates over sections in the loaded JSON data and processes each into chunks.
    """
    all_chunks: List[Chunk] = []
    for section_key, section_data_value in json_data.items():
        if not isinstance(section_data_value, dict):
            print(f"Warning: Skipping section '{section_key}' in '{document_id}' as its value is not a dictionary (type: {type(section_data_value)}).")
            continue
        try:
            print(f"Processing section: {section_key}...")
            section_chunks = process_section_into_chunks(
                document_id=document_id,
                original_section_name=section_key,
                section_data=section_data_value,
                max_tokens_per_chunk=max_tokens_per_chunk,
                chunk_overlap_tokens=chunk_overlap_tokens
            )
            all_chunks.extend(section_chunks)
            print(f"  Generated {len(section_chunks)} chunks for section '{section_key}'.")
        except Exception as e:
            print(f"Error processing section {section_key} for document {document_id}: {str(e)}")
            # Optionally, re-raise or handle more gracefully depending on requirements
    return all_chunks

def save_chunks_to_files(chunks: List[Chunk], output_directory: Path):
    """
    Saves each chunk's content_text to a .txt file and compiles all metadata
    into a single _summary_metadata.json file.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    
    all_metadata_for_summary = []

    for chunk in chunks:
        # Use the chunk.id for the filename (it's already somewhat sanitized)
        chunk_file_path = output_directory / f"{chunk.id}.txt"
        
        # For RAG, the .txt file should ideally contain only the clean text to be embedded.
        # Metadata is best kept separate or in a system like ChromaDB.
        # For inspection, a header can be added, but for programmatic use, it's often cleaner without.
        # Here, we save clean text.
        with open(chunk_file_path, 'w', encoding='utf-8') as f:
            f.write(chunk.content_text)
            
        # Prepare metadata for the summary file
        # Store relative path for portability
        relative_chunk_path = chunk_file_path.relative_to(output_directory.parent) # Relative to chunks_enhanced/
        all_metadata_for_summary.append({
            "chunk_id": chunk.id,
            "file_path": str(relative_chunk_path),
            "token_count": chunk.token_count,
            "metadata": chunk.metadata,
        })

    summary_file_path = output_directory / "_summary_metadata.json"
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata_for_summary, f, indent=4, ensure_ascii=False)

    print(f"\nSaved {len(chunks)} chunk text files to: {output_directory}")
    print(f"Master metadata summary saved to: {summary_file_path}")


def main():
    # --- Configuration ---
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent # Assumes script is in project_root/chunks_generator/
    
    # Choose the input file: "pessoal.json" or "folha.json"
    # Consider using command-line arguments (e.g., argparse) for flexibility
    input_file_name = "pessoal.json" 
    
    # Location of input JSON files (e.g., project_root/data_sources/pessoal.json)
    # For this example, assuming input JSON is directly in project_root for simplicity
    # Adjust if your JSON files are elsewhere (e.g., a 'data/' or 'docs/' subdirectory)
    input_file_path = project_root / input_file_name 

    # Base directory for all enhanced chunk outputs
    output_base_dir = project_root / "chunks_enhanced_v2" # Using a new versioned folder
    # Specific output directory for this input file's chunks
    output_file_specific_dir = output_base_dir / Path(input_file_name).stem # e.g., "pessoal"
    
    # Global MAX_TOKENS and TOKEN_OVERLAP are used from top of the script
    # These can also be passed as arguments to main or configured here if needed.

    print(f"--- Starting Chunking Process ---")
    print(f"Input JSON file: {input_file_path}")
    print(f"Output directory for chunks: {output_file_specific_dir}")
    print(f"Max tokens per chunk: {MAX_TOKENS}")
    print(f"Token overlap: {TOKEN_OVERLAP}")

    if not input_file_path.exists():
        print(f"Error: Input file not found at {input_file_path}")
        return

    json_content = load_json_data(str(input_file_path))
    
    print(f"\nStarting chunk generation for: {input_file_name}...")
    document_chunks = create_document_chunks(
        json_data=json_content,
        document_id=Path(input_file_name).stem, # Use file stem as document id (e.g., "pessoal")
        max_tokens_per_chunk=MAX_TOKENS,
        chunk_overlap_tokens=TOKEN_OVERLAP
    )
    
    if document_chunks:
        save_chunks_to_files(document_chunks, output_file_specific_dir)
        print(f"\nSuccessfully generated and saved {len(document_chunks)} chunks for {input_file_name}.")
    else:
        print("\nNo chunks were generated from the input file.")
    
    print(f"--- Chunking Process Finished ---")

if __name__ == "__main__":
    main()