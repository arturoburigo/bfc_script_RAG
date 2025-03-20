import json
import os
import openai
from tqdm import tqdm
import time

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Read all chunk files from the directory
chunks_dir = "docs/chunks"
document_chunks = []

# Read each individual chunk file
print("Loading chunks from files...")
for filename in os.listdir(chunks_dir):
    if filename.endswith('.json'):
        with open(os.path.join(chunks_dir, filename), 'r', encoding='utf-8') as file:
            chunk = json.load(file)
            document_chunks.append(chunk)

print(f"Loaded {len(document_chunks)} chunks")

# Create embeddings for the chunks using OpenAI's text-embedding-large model
print("Generating embeddings with OpenAI's text-embedding-large model...")

# Function to create embedding with rate limit handling
def get_embedding(text):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=3072  # The full dimensionality of the model
            )
            return response.data[0].embedding
        except openai.RateLimitError:
            wait_time = (2 ** attempt) * 1  # Exponential backoff: 1, 2, 4, 8, 16 seconds
            print(f"Rate limit hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            time.sleep(1)
    
    print(f"Failed to generate embedding after {max_retries} attempts")
    return None

# Process chunks in batches to avoid rate limits
for i, chunk in enumerate(tqdm(document_chunks)):
    embedding = get_embedding(chunk["content"])
    if embedding:
        chunk["embedding"] = embedding
    
    # Add a small delay between requests to avoid rate limits
    if i % 10 == 0 and i > 0:
        time.sleep(0.5)

# Count successful embeddings
successful_embeddings = sum(1 for chunk in document_chunks if "embedding" in chunk)
print(f"Successfully generated {successful_embeddings} embeddings out of {len(document_chunks)} chunks")

# Save the JSON with embeddings
output_path = "docs/chunks/documentation_chunks_with_embeddings_v2.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(document_chunks, file, indent=4, ensure_ascii=False)

print(f"Embeddings generated and saved to {output_path}!")
print(f"Total chunks processed: {len(document_chunks)}")