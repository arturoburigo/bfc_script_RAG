import chromadb
from chromadb.config import Settings
import json
from typing import Dict, Any

# Initialize ChromaDB client with persistent storage
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False
    )
)

def print_collection_info(collection_name: str):
    """Print detailed information about a specific collection"""
    try:
        collection = client.get_collection(collection_name)
        #print(f"\n=== Collection: {collection_name} ===")
        
        # Get collection count
        count = collection.count()
        #print(f"Total documents: {count}")
        
        # Get sample documents with metadata and embeddings
        results = collection.get(
            include=["documents", "metadatas", "embeddings"],
            limit=3
        )
        
        #print("\nSample documents:")
        for i, (doc, metadata, embedding) in enumerate(zip(results['documents'], results['metadatas'], results['embeddings'])):
            print(f"\nDocument {i+1}:")
            print(f"Content preview: {doc[:200]}...")
            print("Metadata:", json.dumps(metadata, indent=2, ensure_ascii=False))
            print(f"Embedding preview (first 5 values): {embedding[:5]}")
            print(f"Embedding length: {len(embedding)}")
            
    except Exception as e:
        print(f"Error accessing collection {collection_name}: {str(e)}")

def main():
    # List all collections
    collections = client.list_collections()
    print("Available collections:")
    for collection in collections:
        print(f"- {collection.name}")
        print_collection_info(collection.name)

if __name__ == "__main__":
    main()
