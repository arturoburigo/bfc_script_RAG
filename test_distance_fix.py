#!/usr/bin/env python3
"""
Test script to verify ChromaDB distance metrics and semantic search performance.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.semantic_search import SemanticSearch
import chromadb
from chromadb.config import Settings
import numpy as np

def test_distance_metrics():
    """Test the distance metrics in ChromaDB collections."""
    print("Testing ChromaDB distance metrics...\n")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Check existing collections
    collections = client.list_collections()
    print(f"Found {len(collections)} collections:")
    
    for collection in collections:
        print(f"\nCollection: {collection.name}")
        print(f"  Document count: {collection.count()}")
        
        # Check metadata for distance metric
        try:
            # Get collection metadata
            coll = client.get_collection(collection.name)
            metadata = coll.metadata if hasattr(coll, 'metadata') else {}
            print(f"  Metadata: {metadata}")
            
            # Test with a sample query
            if coll.count() > 0:
                # Get a sample document to use as query
                sample = coll.get(limit=1, include=["embeddings"])
                if sample and sample.get("embeddings"):
                    query_embedding = sample["embeddings"][0]
                    
                    # Query for similar documents
                    results = coll.query(
                        query_embeddings=[query_embedding],
                        n_results=5,
                        include=["distances"]
                    )
                    
                    if results and results.get("distances"):
                        distances = results["distances"][0]
                        print(f"  Sample distances: {distances}")
                        print(f"  Distance range: [{min(distances):.4f}, {max(distances):.4f}]")
                        
                        # Check if distances look like L2 or cosine
                        if max(distances) > 2.0:
                            print("  ⚠️  WARNING: Distances > 2.0 suggest L2 distance (not cosine)")
                        else:
                            print("  ✓ Distances <= 2.0 suggest cosine distance")
        except Exception as e:
            print(f"  Error checking collection: {e}")

def test_search_query(query="exemplo de código para buscar funcionários"):
    """Test a semantic search query and show distance results."""
    print(f"\n\nTesting semantic search with query: '{query}'")
    print("-" * 80)
    
    try:
        # Initialize semantic search
        search_engine = SemanticSearch()
        
        # Perform search
        results = search_engine.search(query, top_k=5)
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results):
            print(f"\n[Result {i+1}]")
            print(f"  Collection: {result.get('collection', 'N/A')}")
            print(f"  Raw distance: {result.get('distance', 'N/A'):.4f}")
            print(f"  Relevance score: {result.get('relevance_score', 0.0):.4f}")
            print(f"  Has code example: {result.get('has_code_example', False)}")
            print(f"  Content preview: {result.get('content', '')[:100]}...")
            
    except Exception as e:
        print(f"Error during search: {e}")

def check_duplicates():
    """Check for duplicate documents in collections."""
    print("\n\nChecking for duplicate documents...")
    print("-" * 80)
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    for collection_name in ["docs", "enums", "folha", "pessoal"]:
        try:
            collection = client.get_collection(collection_name)
            all_ids = collection.get()["ids"]
            unique_ids = set(all_ids)
            
            print(f"\n{collection_name}:")
            print(f"  Total documents: {len(all_ids)}")
            print(f"  Unique documents: {len(unique_ids)}")
            
            if len(all_ids) > len(unique_ids):
                print(f"  ⚠️  Found {len(all_ids) - len(unique_ids)} duplicate documents!")
                # Find duplicate IDs
                from collections import Counter
                id_counts = Counter(all_ids)
                duplicates = {id: count for id, count in id_counts.items() if count > 1}
                print(f"  Duplicate IDs: {list(duplicates.keys())[:5]}...")  # Show first 5
            else:
                print("  ✓ No duplicates found")
                
        except Exception as e:
            print(f"  Error checking collection: {e}")

if __name__ == "__main__":
    print("ChromaDB Distance Metric Test\n")
    print("=" * 80)
    
    # Test 1: Check current distance metrics
    test_distance_metrics()
    
    # Test 2: Run a sample search query
    test_search_query()
    
    # Test 3: Check for duplicates
    check_duplicates()
    
    print("\n\nRecommendations:")
    print("-" * 80)
    print("1. If you see distances > 2.0, your collections are using L2 distance (incorrect)")
    print("2. Run: python -m app.core.initialize_chroma_db --reset")
    print("   This will recreate collections with cosine distance")
    print("3. If you see many duplicates, the reset will also fix this issue") 