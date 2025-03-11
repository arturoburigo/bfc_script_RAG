from sentence_transformers import SentenceTransformer
import json
import os

# Carregar o modelo de embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

# Ler todos os arquivos de chunks do diretório
chunks_dir = "docs/chunks"
document_chunks = []

# Ler cada arquivo de chunk individual
for filename in os.listdir(chunks_dir):
    if filename.endswith('.json'):
        with open(os.path.join(chunks_dir, filename), 'r', encoding='utf-8') as file:
            chunk = json.load(file)
            document_chunks.append(chunk)

# Criar os embeddings dos chunks
for chunk in document_chunks:
    chunk["embedding"] = model.encode(chunk["content"]).tolist()

# Salvar o JSON com embeddings
output_path = "docs/chunks/documentation_chunks_with_embeddings.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(document_chunks, file, indent=4, ensure_ascii=False)

print(f"Embeddings gerados e salvos em {output_path}!")
print(f"Total de chunks processados: {len(document_chunks)}")