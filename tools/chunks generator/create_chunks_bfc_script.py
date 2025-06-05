import json
import os
import re
import uuid # Para IDs de chunk únicos
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
# Em vez de from langchain.text_splitter import ... (para versões mais recentes de langchain)
# Se estiver usando uma versão mais antiga:
# from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# --- Configurações ---
INPUT_FILES = [
    os.path.join(".", "bfc_script_docs.md") # Exemplo, ajuste conforme necessário
]
OUTPUT_DIR_INDIVIDUAL_CHUNKS = "chunks_enhanced_v2/pessoal/" # Diretório para chunks individuais
OUTPUT_JSON_ALL_CHUNKS = "chunks_enhanced_v2/chunks_enhancedpessoal_summary_metadata.json" # JSON com todos os chunks

# Parâmetros de Chunking
CHUNK_SIZE = 300 # Tamanho alvo do chunk em caracteres (aproximado, pois RecursiveCharacterTextSplitter usa tokens)
CHUNK_OVERLAP = 50 # Sobreposição entre chunks
PRESERVE_SMALL_SECTIONS_THRESHOLD = CHUNK_SIZE * 0.5 # Seções menores que isso não serão divididas por RecursiveCharacterTextSplitter se não for necessário

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR_INDIVIDUAL_CHUNKS, exist_ok=True)

# --- Splitters LangChain ---
# Splitter para preservar estrutura de títulos do Markdown
# Ajuste os cabeçalhos conforme a estrutura do seu Markdown
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("### ", "header_level_3"), # Nome da chave no metadado
        ("#### ", "header_level_4"),
        ("##### ", "header_level_5"),
    ],
    strip_headers=False # Mantém o texto do cabeçalho no conteúdo se True, ou remove se False. Decida com base na necessidade.
                        # Para RAG, pode ser útil manter (strip_headers=False) e ter o header no início do conteúdo do chunk.
)

# Splitter recursivo para dividir o texto dentro das seções
# Usa uma lista de separadores para tentar manter blocos lógicos juntos.
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""], # Prioriza quebras de parágrafo, depois linhas, depois frases.
    length_function=len # Função para medir o tamanho do texto (padrão é len)
)

# --- Pré-processamento e Manipulação de Código ---
# Padrão para detectar blocos de código numerados específicos do bfc-script
# Exemplo: "1. some code line"
bfc_code_block_pattern = r'(?:^\d+\.\s+.*(?:\n|$))+' # Ajuste se o padrão for diferente

def format_bfc_code_block(match):
    """Formata blocos de código numerados para o formato Markdown ```bfc-script ... ```."""
    code_lines = match.group(0).strip().split('\n')
    processed_lines = []
    for line in code_lines:
        if not line.strip():
            continue
        clean_line = re.sub(r'^\d+\.\s+', '', line) # Remove numeração
        processed_lines.append(clean_line)
    
    if processed_lines:
        return "```bfc-script\n" + "\n".join(processed_lines) + "\n```"
    return ""

def preprocess_markdown_content(content: str) -> str:
    """Aplica pré-processamento ao conteúdo Markdown bruto."""
    # 1. Formata blocos de código bfc-script numerados
    content = re.sub(bfc_code_block_pattern, format_bfc_code_block, content, flags=re.MULTILINE)
    
    # 2. Normaliza múltiplos newlines (exceto dentro de blocos de código)
    # Esta é uma operação mais complexa para evitar quebrar blocos de código.
    # Por simplicidade, faremos uma normalização mais leve ou aplicaremos após a divisão inicial por headers.
    # content = re.sub(r'\n{3,}', '\n\n', content) # Pode ser aplicado no conteúdo da seção
    return content

def clean_section_text(text: str) -> str:
    """Limpa o texto de uma seção antes da divisão fina."""
    text = re.sub(r'\n{3,}', '\n\n', text) # Normaliza newlines excessivos
    text = re.sub(r'[ \t]{2,}', ' ', text) # Normaliza espaços excessivos (cuidado para não quebrar indentações de código se aplicado antes)
    return text.strip()

def extract_specific_code_blocks(text: str, lang_tag: str = "bfc-script") -> list[str]:
    """Extrai blocos de código formatados (ex: ```bfc-script ... ```)."""
    pattern = rf'```{lang_tag}\n(.*?)\n```'
    return re.findall(pattern, text, re.DOTALL)

# --- Processamento Principal ---
def process_single_markdown_file(file_path: str) -> list[dict]:
    """
    Processa um único arquivo Markdown:
    1. Lê o conteúdo.
    2. Pré-processa (formata blocos de código bfc).
    3. Divide em seções com base nos cabeçalhos Markdown.
    4. Para cada seção, limpa o texto e prepara para chunking mais fino.
    """
    print(f"\n📄 Processando arquivo: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        raw_content = file.read()

    preprocessed_content = preprocess_markdown_content(raw_content)
    
    # Usa o MarkdownHeaderTextSplitter do LangChain
    # Ele retorna uma lista de LangChain Document objects
    langchain_docs_from_headers = markdown_splitter.split_text(preprocessed_content)
    
    processed_sections_for_chunking = []
    for i, doc in enumerate(langchain_docs_from_headers):
        section_metadata = doc.metadata.copy() # Metadados dos cabeçalhos (ex: {"header_level_3": "Título da Seção"})
        section_metadata["original_document_filename"] = os.path.basename(file_path)
        section_metadata["original_document_filepath"] = file_path
        section_metadata["section_index_in_document"] = i # Ordem da seção no documento

        # Limpa o conteúdo da página da seção antes de prosseguir
        # Se strip_headers=False no MarkdownHeaderTextSplitter, o texto do header estará aqui.
        cleaned_page_content = clean_section_text(doc.page_content)

        processed_sections_for_chunking.append({
            "raw_section_content": cleaned_page_content, # Conteúdo da seção para ser dividido
            "base_metadata": section_metadata,      # Metadados da seção (origem, cabeçalhos)
            "original_markdown_header_text": doc.page_content.splitlines()[0] if doc.page_content and markdown_splitter.strip_headers is False else ""
        })
        # print(f"  📑 Seção {i} (Header: {section_metadata.get('header_level_3', 'N/A')}): {len(cleaned_page_content)} caracteres")

    return processed_sections_for_chunking


def create_final_chunks(sections_to_chunk: list[dict]) -> list[dict]:
    """
    Cria chunks finais a partir das seções processadas, preservando blocos de código.
    """
    all_final_chunks = []
    
    for section_idx, section_data in enumerate(sections_to_chunk):
        content_to_split = section_data["raw_section_content"]
        base_metadata = section_data["base_metadata"]
        
        # Lógica de preservação de código (placeholder)
        code_blocks = extract_specific_code_blocks(content_to_split, "bfc-script")
        placeholders = {}
        temp_content_for_splitting = content_to_split

        if code_blocks:
            for i, code_content in enumerate(code_blocks):
                placeholder = f"__CODE_BLOCK_PLACEHOLDER_{i}__"
                full_code_block_text = f"```bfc-script\n{code_content}\n```"
                placeholders[placeholder] = full_code_block_text
                # Substitui apenas a primeira ocorrência para evitar problemas com blocos idênticos
                temp_content_for_splitting = temp_content_for_splitting.replace(full_code_block_text, placeholder, 1)

        # Estratégia de Chunking Mais Inteligente (parcial):
        # Se a seção (sem código) for pequena o suficiente, pode não precisar ser dividida pelo RecursiveCharacterTextSplitter.
        # No entanto, a divisão por placeholders de código ainda pode quebrar o texto.
        # A abordagem mais simples é sempre tentar dividir, e o RecursiveCharacterTextSplitter
        # retornará um único chunk se for menor que chunk_size.

        split_texts = recursive_text_splitter.split_text(temp_content_for_splitting)
        
        for chunk_seq, text_chunk in enumerate(split_texts):
            final_chunk_content = text_chunk
            contains_code_flag = False
            
            # Restaura blocos de código
            for placeholder, code_block_text in placeholders.items():
                if placeholder in final_chunk_content:
                    final_chunk_content = final_chunk_content.replace(placeholder, code_block_text)
                    contains_code_flag = True # Marca que este chunk contém código

            chunk_id = str(uuid.uuid4())
            chunk_metadata = base_metadata.copy() # Herda metadados da seção
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "chunk_sequence_in_section": chunk_seq,
                "contains_code": contains_code_flag,
                "estimated_char_length": len(final_chunk_content),
                # Se strip_headers=False e você quiser o texto do header no metadado explicitamente:
                # "header_text_if_any": section_data["original_markdown_header_text"] if chunk_seq == 0 else ""
            })
            
            # Adiciona o chunk final à lista (estrutura similar a um LangChain Document)
            all_final_chunks.append({
                "page_content": final_chunk_content,
                "metadata": chunk_metadata
            })
            # print(f"    📦 Chunk {chunk_id[:8]}... ({len(final_chunk_content)} chars, Code: {contains_code_flag})")

    return all_final_chunks

# --- Execução do Pipeline ---
all_processed_chunks = []
for md_file in INPUT_FILES:
    if os.path.exists(md_file):
        sections_from_file = process_single_markdown_file(md_file)
        chunks_from_file = create_final_chunks(sections_from_file)
        all_processed_chunks.extend(chunks_from_file)
    else:
        print(f"⚠️ Arquivo não encontrado: {md_file}")

# --- Salvamento e Validação ---
# Salvar cada chunk como um arquivo JSON separado
for chunk_data in all_processed_chunks:
    # Cria um nome de arquivo mais descritivo (mas pode ficar longo)
    doc_name = chunk_data["metadata"]["original_document_filename"].replace(".md", "")
    header_info = chunk_data["metadata"].get("header_level_3", 
                  chunk_data["metadata"].get("header_level_4", 
                  chunk_data["metadata"].get("header_level_5", "geral"))).replace(" ", "_").replace("/", "_")
    chunk_filename_stem = f"{doc_name}_section{chunk_data['metadata']['section_index_in_document']}_{header_info}_chunk{chunk_data['metadata']['chunk_sequence_in_section']}"
    
    # Simplificando para usar chunk_id para garantir unicidade e evitar nomes de arquivo muito longos
    chunk_filename = f"{OUTPUT_DIR_INDIVIDUAL_CHUNKS}{chunk_data['metadata']['chunk_id']}.txt"
    
    # Save as .txt file for the chunk content
    with open(chunk_filename, "w", encoding="utf-8") as chunk_file:
        chunk_file.write(chunk_data["page_content"])

# Salvar JSON final com todos os chunks (metadata summary)
with open(OUTPUT_JSON_ALL_CHUNKS, "w", encoding="utf-8") as json_file:
    json.dump(all_processed_chunks, json_file, indent=4, ensure_ascii=False)

print(f"\n--- ✨ Processamento Concluído ✨ ---")
print(f"✅ Total de chunks processados: {len(all_processed_chunks)}")
print(f"📄 JSON com todos os chunks salvo em: {OUTPUT_JSON_ALL_CHUNKS}")
print(f"🗂️ Chunks individuais salvos em: {OUTPUT_DIR_INDIVIDUAL_CHUNKS}")

# Validação e Qualidade (Estatísticas)
if all_processed_chunks:
    chunk_lengths = [len(chunk["page_content"]) for chunk in all_processed_chunks]
    code_chunks_count = sum(1 for chunk in all_processed_chunks if chunk["metadata"]["contains_code"])
    
    print("\n--- 📊 Estatísticas dos Chunks ---")
    print(f"📏 Tamanho Médio dos Chunks (caracteres): {sum(chunk_lengths) / len(chunk_lengths):.2f}")
    print(f"↔️ Tamanho Mín/Máx dos Chunks (caracteres): {min(chunk_lengths)} / {max(chunk_lengths)}")
    print(f"💻 Número de chunks contendo blocos de código 'bfc-script': {code_chunks_count}")
else:
    print("\n⚠️ Nenhum chunk foi gerado.")