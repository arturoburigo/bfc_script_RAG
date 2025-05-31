#!/usr/bin/env python3
"""
Diagnostic script to test embedding similarity and identify issues.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.semantic_search import SemanticSearch
import chromadb
from chromadb.config import Settings
import numpy as np
from openai import OpenAI

def test_embedding_similarity():
    """Test if embeddings are working correctly by comparing identical texts."""
    print("Testing Embedding Similarity\n" + "="*80)
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        return
        
    client = OpenAI(api_key=api_key)
    
    # Test 1: Identical texts should have very high similarity
    print("\nTest 1: Identical Text Similarity")
    text1 = "exemplo de código para buscar funcionários"
    text2 = "exemplo de código para buscar funcionários"
    
    # Generate embeddings
    response1 = client.embeddings.create(
        model="text-embedding-3-small",
        input=text1,
        dimensions=512
    )
    response2 = client.embeddings.create(
        model="text-embedding-3-small",
        input=text2,
        dimensions=512
    )
    
    emb1 = np.array(response1.data[0].embedding)
    emb2 = np.array(response2.data[0].embedding)
    
    # Calculate cosine similarity
    cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    cosine_distance = 1 - cosine_sim
    
    print(f"Text 1: '{text1}'")
    print(f"Text 2: '{text2}'")
    print(f"Cosine similarity: {cosine_sim:.4f}")
    print(f"Cosine distance: {cosine_distance:.4f}")
    print(f"Expected: ~0.0 (identical texts)")
    
    # Test 2: Similar texts
    print("\n\nTest 2: Similar Text Similarity")
    text3 = "código de exemplo para procurar empregados"
    
    response3 = client.embeddings.create(
        model="text-embedding-3-small",
        input=text3,
        dimensions=512
    )
    emb3 = np.array(response3.data[0].embedding)
    
    cosine_sim = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
    cosine_distance = 1 - cosine_sim
    
    print(f"Text 1: '{text1}'")
    print(f"Text 3: '{text3}'")
    print(f"Cosine similarity: {cosine_sim:.4f}")
    print(f"Cosine distance: {cosine_distance:.4f}")
    print(f"Expected: ~0.2-0.4 (similar meaning)")

if __name__ == "__main__":
    test_embedding_similarity() 