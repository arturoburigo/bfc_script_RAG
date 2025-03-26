import json
import os
import faiss
import numpy as np
from openai import OpenAI


class SemanticSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)

        # Obtém o diretório base do arquivo semantic_search.py
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Define caminhos absolutos para evitar problemas
        self.index_path = os.path.join(base_dir, "index", "faiss_index.bin")
        self.chunks_path = os.path.join(base_dir, "docs", "documentation_chunks_with_embeddings.json")

        # Configurar o ambiente para evitar warning do tokenizer
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    def search(self, query, top_k=8):
        """
        Perform semantic search on the documentation based on the query.
        
        Args:
            query (str): The user's query
            top_k (int): Number of top results to retrieve
            
        Returns:
            list: Filtered search results
        """
        try:
            # Criar embeddings expandidos para melhorar a busca semântica
            expanded_query = f"{query} BFC-Script documentação exemplos código sintaxe"
            
            # Criar o embedding da pergunta usando text-embedding-3-large
            query_embedding_response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=expanded_query
            )
            query_embedding = query_embedding_response.data[0].embedding
            query_embedding_np = np.array(query_embedding).astype("float32").reshape(1, -1)

            # Verificar se o arquivo do índice FAISS existe
            if not os.path.exists(self.index_path):
                raise FileNotFoundError(f"Arquivo do índice FAISS não encontrado: {self.index_path}")
            
            index = faiss.read_index(self.index_path)
            
            distances, indices = index.search(query_embedding_np, top_k)
            with open(self.chunks_path, "r", encoding="utf-8") as file:
                document_chunks = json.load(file)
            
            # Filtrar resultados por relevância usando um threshold
            filtered_results = []
            for i, idx in enumerate(indices[0]):
                if distances[0][i] < 1.0:  # Ajuste este threshold conforme necessário
                    filtered_results.append(document_chunks[idx])
            
            # Se não houver resultados relevantes, retornar alguns para contexto geral
            if not filtered_results and len(indices[0]) > 0:
                filtered_results = [document_chunks[idx] for idx in indices[0][:3]]
                
            return filtered_results
        except Exception as e:
            print(f"Erro na busca: {str(e)}")
            return []

    def get_document_context(self, query, top_k=8):
        """
        Get context from documents based on the query.
        
        Args:
            query (str): The user's query
            top_k (int): Number of top results to retrieve
            
        Returns:
            str: Concatenated context from search results
        """
        results = self.search(query, top_k)
        if not results:
            return ""
        
        context = "\n".join([r["content"] for r in results])
        return context, results