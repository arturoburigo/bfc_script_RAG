import json
import os
import openai
from tqdm import tqdm
import time
from pathlib import Path
import glob

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
current_dir = Path(__file__).parent.parent.parent
chunks_dir = current_dir / "chunks" / "enums_pessoal_and_folha"
output_file = current_dir / "embeddings" / "enums_pessoal_and_folha_with_embeddings.json"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

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

# Function to parse chunk filename to extract enum name and part number
def parse_chunk_filename(filename):
    base_name = os.path.basename(filename)
    name_parts = base_name.replace(".txt", "").split("_part_")
    
    enum_name = name_parts[0]
    part_number = int(name_parts[1]) if len(name_parts) > 1 else None
    
    return enum_name, part_number

# Function to read and process chunk files
def process_chunk_files():
    chunk_files = glob.glob(str(chunks_dir / "*.txt"))
    print(f"Found {len(chunk_files)} chunk files")
    
    # Group chunks by enum name
    enum_chunks = {}
    
    for chunk_file in chunk_files:
        enum_name, part_number = parse_chunk_filename(chunk_file)
        
        # Read the chunk content
        with open(chunk_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a unique key for the chunk
        chunk_key = f"{enum_name}_part_{part_number}" if part_number else enum_name
        
        # Store the chunk data
        if enum_name not in enum_chunks:
            enum_chunks[enum_name] = []
        
        enum_chunks[enum_name].append({
            "chunk_key": chunk_key,
            "content": content,
            "part_number": part_number
        })
    
    # Sort chunks by part number
    for enum_name in enum_chunks:
        enum_chunks[enum_name].sort(key=lambda x: x["part_number"] if x["part_number"] is not None else 0)
    
    return enum_chunks

# Process chunks and generate embeddings
print("Loading chunk files...")
enum_chunks = process_chunk_files()

print("Generating embeddings with OpenAI's text-embedding-3-large model...")
embeddings_data = {}

for enum_name, chunks in tqdm(enum_chunks.items()):
    embeddings_data[enum_name] = []
    
    for chunk in chunks:
        # Generate embedding for the content
        embedding = get_embedding(chunk["content"])
        if embedding:
            chunk["embedding"] = embedding
            embeddings_data[enum_name].append(chunk)
        
        # Add a small delay between requests to avoid rate limits
        time.sleep(0.5)

# Count successful embeddings
total_chunks = sum(len(chunks) for chunks in enum_chunks.values())
successful_embeddings = sum(len(chunks) for chunks in embeddings_data.values())
print(f"Successfully generated {successful_embeddings} embeddings out of {total_chunks} chunks")

# Save the JSON with embeddings
try:
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(embeddings_data, file, indent=4, ensure_ascii=False)
    print(f"Embeddings generated and saved to {output_file}!")
except Exception as e:
    print(f"Error saving embeddings: {e}")

print(f"Total enums processed: {len(embeddings_data)}") 