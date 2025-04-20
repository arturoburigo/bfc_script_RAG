import json
import os
import openai
from tqdm import tqdm
import time

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Input and output file paths
input_file = "pessoal_v2_fontedados_no_enums_chunked.json"
output_file = "pessoal_v2_fontedados_no_enums_with_embeddings.json"

# Read the input JSON file
print("Loading documentation from file...")
try:
    with open(input_file, 'r', encoding='utf-8') as file:
        documentation_chunks = json.load(file)
    print(f"Loaded {len(documentation_chunks)} documentation chunks")
except FileNotFoundError:
    print(f"Error: Could not find input file {input_file}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in {input_file}")
    exit(1)

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

# Process chunks and generate embeddings
print("Generating embeddings with OpenAI's text-embedding-3-large model...")
for i, chunk in enumerate(tqdm(documentation_chunks)):
    # Generate embedding for the content
    embedding = get_embedding(chunk["content"])
    if embedding:
        chunk["embedding"] = embedding
    
    # Add a small delay between requests to avoid rate limits
    if i % 10 == 0 and i > 0:
        time.sleep(0.5)

# Count successful embeddings
successful_embeddings = sum(1 for chunk in documentation_chunks if "embedding" in chunk)
print(f"Successfully generated {successful_embeddings} embeddings out of {len(documentation_chunks)} chunks")

# Save the JSON with embeddings
try:
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(documentation_chunks, file, indent=4, ensure_ascii=False)
    print(f"Embeddings generated and saved to {output_file}!")
except Exception as e:
    print(f"Error saving embeddings: {e}")

print(f"Total chunks processed: {len(documentation_chunks)}") 