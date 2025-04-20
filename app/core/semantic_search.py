import os
import chromadb
from chromadb.config import Settings
from openai import OpenAI


class SemanticSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize ChromaDB client with specific embedding function
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Get collections
        try:
            self.docs_collection = self.chroma_client.get_collection("docs")
            self.enums_collection = self.chroma_client.get_collection("enums")
            self.folha_collection = self.chroma_client.get_collection("folha")
            self.pessoal_collection = self.chroma_client.get_collection("pessoal")
        except Exception as e:
            print(f"Error loading collections: {str(e)}")
            raise
    
    def get_embedding(self, text):
        """
        Get embedding for text using the correct model.
        
        Args:
            text (str): Text to get embedding for
            
        Returns:
            list: Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-large",  # Using the same model as used for collection creation
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            raise
    
    def search(self, query, category="Geral", top_k=8):
        """
        Perform semantic search on the documentation based on the query and category.
        
        Args:
            query (str): The user's query
            category (str): The selected category (Geral, Service Layer, Fonte de Dados, Relatório)
            top_k (int): Number of top results to retrieve
            
        Returns:
            list: Filtered search results
        """
        try:
            # Expand query for better semantic search
            expanded_query = f"{query} BFC-Script documentação exemplos código sintaxe"
            
            # Get embedding for the query
            query_embedding = self.get_embedding(expanded_query)
            
            # Search in the appropriate collection based on category
            if category == "Geral":
                # Search across all collections
                all_results = []
                for collection in [self.docs_collection, self.enums_collection, self.folha_collection, self.pessoal_collection]:
                    try:
                        collection_results = collection.query(
                            query_embeddings=[query_embedding],
                            n_results=top_k
                        )
                        if collection_results and 'documents' in collection_results:
                            for i in range(len(collection_results['documents'][0])):
                                all_results.append({
                                    "content": collection_results['documents'][0][i],
                                    "metadata": collection_results['metadatas'][0][i] if 'metadatas' in collection_results else {}
                                })
                    except Exception as e:
                        print(f"Error searching in collection {collection.name}: {str(e)}")
                        continue
                
                # Sort and limit results
                all_results = all_results[:top_k]
                return all_results
            else:
                # Search in specific collection based on category
                collection = self.docs_collection  # Default to docs collection
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                # Format results
                formatted_results = []
                if results and 'documents' in results:
                    for i in range(len(results['documents'][0])):
                        formatted_results.append({
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i] if 'metadatas' in results else {}
                        })
                
                return formatted_results
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return []

    def get_document_context(self, query, top_k=8):
        """
        Get context from documents based on the query.
        
        Args:
            query (str): The user's query
            top_k (int): Number of top results to retrieve
            
        Returns:
            tuple: (context string, search results list)
        """
        try:
            # Extract category from query if present
            category = "Geral"
            if "[Categoria:" in query:
                category = query.split("[Categoria:")[1].split("]")[0].strip()
                query = query.split("]")[1].strip()
            
            results = self.search(query, category, top_k)
            if not results:
                return "", []
            
            context = "\n".join([r["content"] for r in results])
            return context, results
        except Exception as e:
            print(f"Error getting document context: {str(e)}")
            return "", []