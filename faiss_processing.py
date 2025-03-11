import json
import faiss
import numpy as np

# Carregar os chunks com embeddings
with open("docs/chunks_embedded/documentation_chunks_with_embeddings.json", "r", encoding="utf-8") as file:
    document_chunks = json.load(file)

# Criar a matriz de embeddings
embeddings = np.array([chunk["embedding"] for chunk in document_chunks]).astype("float32")

# Criar o índice FAISS
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Salvar o índice
faiss.write_index(index, "index/faiss_index.bin")

print("Indexação concluída!")
