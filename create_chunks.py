import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Configurações automáticas para todos os arquivos .md no diretório
INPUT_FILES = [
    os.path.join("docs/BFC Doc", f) 
    for f in os.listdir("docs/BFC Doc") 
    if f.endswith('.md')
]
OUTPUT_JSON = "docs/documentation_chunks.json"
OUTPUT_DIR = "docs/chunks/"

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Função para processar arquivos e extrair seções
def process_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    document_name = os.path.basename(file_path).replace(".md", "")
    sections = []
    current_section = None
    section_name = "Geral"  # Definir um valor padrão para evitar erro
    
    for line in lines:
        line = line.strip()
        if line.startswith("### "):
            section_name = line.replace("### ", "").strip()
        elif line.startswith("##### ") or line.startswith("#### "):
            subsection_name = line.replace("##### ", "").replace("#### ", "").strip()
            current_section = {
                "document": document_name,
                "section": section_name,
                "subsection": subsection_name,
                "content": "",
                "metadata": {"source": file_path}
            }
            sections.append(current_section)
        elif current_section:
            current_section["content"] += line + "\n"
    
    return sections

# Processar todos os arquivos
all_sections = []
for file in INPUT_FILES:
    all_sections.extend(process_markdown(file))

# Configuração do LangChain para dividir os chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50
)

# Criar chunks pequenos para RAG
document_chunks = []
for section in all_sections:
    chunks = text_splitter.split_text(section["content"])
    for idx, chunk in enumerate(chunks, start=1):
        chunk_data = {
            "document": section["document"],
            "section": section["section"],
            "subsection": section["subsection"],
            "content": chunk,
            "metadata": section["metadata"]
        }
        document_chunks.append(chunk_data)
        
        # Salvar cada chunk como um arquivo separado
        chunk_filename = f"{OUTPUT_DIR}{section['document']}_chunk{idx}.json"
        with open(chunk_filename, "w", encoding="utf-8") as chunk_file:
            json.dump(chunk_data, chunk_file, indent=4, ensure_ascii=False)

# Salvar JSON final
with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
    json.dump(document_chunks, json_file, indent=4, ensure_ascii=False)

print(f"Processamento concluído! JSON salvo em {OUTPUT_JSON}")
print(f"Chunks individuais salvos em {OUTPUT_DIR}")
