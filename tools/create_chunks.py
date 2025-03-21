import json
import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# Configurações automáticas
INPUT_FILES = [
    os.path.join("docs/BFC Doc", f) 
    for f in os.listdir("docs/BFC Doc") 
    if f.endswith('.md')
]
OUTPUT_JSON = "docs/documentation_chunks.json"
OUTPUT_DIR = "docs/chunks/"

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Splitter para preservar estrutura de títulos
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("### ", "section"),
        ("#### ", "subsection"),
        ("##### ", "subsubsection"),
    ]
)

# Padrão para detectar blocos de código numerados
code_block_pattern = r'(?:^\d+\.\s+.*(?:\n|$))+'

# Função para processar blocos de código numerados
def format_code_block(match):
    code_lines = match.group(0).split('\n')
    processed_lines = []
    
    for line in code_lines:
        if not line.strip():
            continue
        # Remove o número da linha
        clean_line = re.sub(r'^\d+\.\s+', '', line)
        processed_lines.append(clean_line)
    
    if processed_lines:
        return "```bfc-script\n" + "\n".join(processed_lines) + "\n```"
    return ""

# Função para pré-processar o conteúdo com blocos de código formatados
def preprocess_content(content):
    return re.sub(code_block_pattern, format_code_block, content, flags=re.MULTILINE)

# Função para extrair blocos de código formatados
def extract_code_blocks(text):
    # Encontrar todos os blocos de código com a linguagem bfc-script
    pattern = r'```bfc-script\n(.*?)\n```'
    return re.findall(pattern, text, re.DOTALL)

# Função para processar cada documento markdown
def process_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Pré-processar o conteúdo para ajustar os blocos de código
    processed_content = preprocess_content(content)
    
    sections = md_splitter.split_text(processed_content)
    processed_sections = [
        {
            "document": os.path.basename(file_path).replace(".md", ""),
            "section": sec.metadata.get("section", "Geral"),
            "subsection": sec.metadata.get("subsection", ""),
            "subsubsection": sec.metadata.get("subsubsection", ""),
            "content": sec.page_content,
            "metadata": {"source": file_path}
        }
        for sec in sections
    ]
    return processed_sections

# Processar todos os arquivos
all_sections = []
for file in INPUT_FILES:
    all_sections.extend(process_markdown(file))

# Função para criar chunks respeitando blocos de código
def create_chunks_with_code_preservation(sections, chunk_size=250, chunk_overlap=50):
    document_chunks = []
    
    for section in all_sections:
        content = section["content"]
        
        # Encontrar todos os blocos de código
        code_blocks = extract_code_blocks(content)
        
        # Se não há blocos de código, dividir normalmente
        if not code_blocks:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
            )
            chunks = text_splitter.split_text(content)
            
            for idx, chunk in enumerate(chunks, start=1):
                chunk_data = {
                    "document": section["document"],
                    "section": section["section"],
                    "subsection": section["subsection"],
                    "subsubsection": section["subsubsection"],
                    "content": chunk,
                    "metadata": section["metadata"],
                    "contains_code": False
                }
                document_chunks.append(chunk_data)
        else:
            # Substituir blocos de código por placeholders
            placeholders = {}
            for i, code in enumerate(code_blocks):
                placeholder = f"CODE_BLOCK_{i}"
                placeholders[placeholder] = f"```bfc-script\n{code}\n```"
                content = content.replace(f"```bfc-script\n{code}\n```", placeholder)
            
            # Dividir o texto com placeholders
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
            )
            chunks = text_splitter.split_text(content)
            
            # Processar cada chunk e restaurar os blocos de código
            for idx, chunk in enumerate(chunks, start=1):
                # Verificar se o chunk contém um placeholder de código
                contains_code = False
                for placeholder, code in placeholders.items():
                    if placeholder in chunk:
                        contains_code = True
                        chunk = chunk.replace(placeholder, code)
                
                chunk_data = {
                    "document": section["document"],
                    "section": section["section"],
                    "subsection": section["subsection"],
                    "subsubsection": section["subsubsection"],
                    "content": chunk,
                    "metadata": section["metadata"],
                    "contains_code": contains_code
                }
                document_chunks.append(chunk_data)
                
    return document_chunks

# Criar chunks com preservação de código
document_chunks = create_chunks_with_code_preservation(all_sections, chunk_size=250, chunk_overlap=50)

# Salvar cada chunk como um arquivo separado
for idx, chunk_data in enumerate(document_chunks, start=1):
    section_name = chunk_data["section"].replace(" ", "_").replace("/", "_")
    chunk_filename = f"{OUTPUT_DIR}{chunk_data['document']}_{section_name}_chunk{idx}.json"
    with open(chunk_filename, "w", encoding="utf-8") as chunk_file:
        json.dump(chunk_data, chunk_file, indent=4, ensure_ascii=False)

# Salvar JSON final
with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
    json.dump(document_chunks, json_file, indent=4, ensure_ascii=False)

print(f"Processamento concluído! JSON salvo em {OUTPUT_JSON}")
print(f"Chunks individuais salvos em {OUTPUT_DIR}")
print(f"Total de chunks: {len(document_chunks)}")