import chromadb
from chromadb.config import Settings
import json
from typing import Dict, List, Tuple
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_embedding(text: str, client: OpenAI) -> List[float]:
    """Get embedding for a text using OpenAI's API."""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=512
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

def analyze_pessoal_collection():
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get the pessoal collection
    collection = client.get_collection("pessoal")
    
    # Get all documents
    results = collection.get()
    
    # Initialize OpenAI client for embeddings
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test query
    test_query = "matriculas_busca"
    query_embedding = get_embedding(test_query, openai_client)
    
    print("\n🔍 ANALISANDO COLEÇÃO PESSOAL")
    print("=" * 80)
    print(f"Total de documentos: {len(results['ids'])}")
    
    # Store results with similarity scores
    ranked_results: List[Tuple[float, str, str, Dict]] = []
    
    # Analyze each document
    for i, (doc_id, content, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas']), 1):
        # Get document embedding
        doc_embedding = collection.get(
            ids=[doc_id],
            include=['embeddings']
        )['embeddings'][0]
        
        # Calculate similarity with test query
        if doc_embedding and query_embedding:
            # Simple cosine similarity
            import numpy as np
            similarity = np.dot(doc_embedding, query_embedding) / (
                np.linalg.norm(doc_embedding) * np.linalg.norm(query_embedding)
            )
        else:
            similarity = 0.0
        
        # Store result with similarity score
        ranked_results.append((similarity, doc_id, content, metadata))
    
    # Sort results by similarity score in descending order
    ranked_results.sort(key=lambda x: x[0], reverse=True)
    
    # Display ranked results
    for i, (similarity, doc_id, content, metadata) in enumerate(ranked_results, 1):
        print(f"\n{'='*80}")
        print(f"Resultado #{i} (Similaridade: {similarity:.4f})")
        print(f"ID: {doc_id}")
        
        # Print metadata
        print("\nMetadata:")
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        
        # Print content preview
        print("\nConteúdo:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Check if content contains matricula_busca
        if "matricula_busca" in content.lower():
            print("\n⚠️ ENCONTRADO 'matricula_busca' NO CONTEÚDO!")
        
        # Check if function_name in metadata contains matricula_busca
        if metadata.get('function_name', '').lower() == 'matricula_busca':
            print("\n⚠️ ENCONTRADO 'matricula_busca' NO NOME DA FUNÇÃO!")

if __name__ == "__main__":
    analyze_pessoal_collection() 