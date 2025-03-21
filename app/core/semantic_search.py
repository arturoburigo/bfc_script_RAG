import json
import os
import faiss
import numpy as np
from openai import OpenAI

class SemanticSearch:
    def __init__(self, api_key=None):
        # Use environment variable if no key is provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.index_path = "index/faiss_index.bin"
        self.chunks_path = "docs/chunks_embedded/documentation_chunks_with_embeddings.json"
        
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
            
            # Converter para o formato numpy necessário para FAISS
            query_embedding_np = np.array(query_embedding).astype("float32").reshape(1, -1)
            
            # Carregar o índice FAISS
            index = faiss.read_index(self.index_path)
            
            # Buscar os k resultados mais próximos
            distances, indices = index.search(query_embedding_np, top_k)
            
            # Carregar os chunks para retornar os textos
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
    
    def extract_syntax_patterns(self, context):
        """
        Extrai padrões sintáticos comuns do BFC-Script do contexto.
        
        Args:
            context (str): Documentation context
            
        Returns:
            str: Extracted syntax patterns
        """
        try:
            from app.utils.prompts import SYNTAX_EXTRACTION_PROMPT
            
            syntax_prompt = SYNTAX_EXTRACTION_PROMPT.format(context=context)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um analisador sintático técnico que extrai padrões de código de documentação."},
                    {"role": "user", "content": syntax_prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao extrair padrões sintáticos: {str(e)}")
            return ""
    
    def generate_response(self, query, history=None):
        """
        Generate a response for the user query using RAG.
        
        Args:
            query (str): The user's query
            history (list): Chat history
            
        Returns:
            str: Generated response
        """
        try:
            from app.utils.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT
            
            # Incorporate chat history context for better continuity
            history_context = ""
            if history and len(history) > 0:
                last_exchanges = history[-3:] if len(history) > 3 else history
                history_context = "\n".join([f"Usuário: {q}\nAssistente: {a}" for q, a in last_exchanges])
            
            # Buscar documentação relevante
            results = self.search(query)
            
            if not results:
                return "Não foi possível realizar a busca semântica. Verifique os logs para mais detalhes."
                
            context = "\n".join([r["content"] for r in results])
            
            # Extrair padrões sintáticos para uso em respostas não documentadas
            syntax_patterns = self.extract_syntax_patterns(context)
            
            # Montar o prompt completo
            prompt = RAG_USER_PROMPT.format(
                context=context,
                syntax_patterns=syntax_patterns,
                history_context=history_context,
                query=query
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return f"Ocorreu um erro ao processar sua consulta: {str(e)}"