import json
import os
import openai
from tqdm import tqdm
import time
import re

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Input and output paths
input_files = [
    "app/core/docs/fontedados/enums/extracted_enums_folha.md",
    "app/core/docs/fontedados/enums/extracted_enums_pessoal.md"
]
output_file = "enum_embeddings.json"

def parse_markdown_enum(content):
    """Parse markdown content into enum chunks."""
    chunks = []
    current_enum = None
    current_items = []
    
    # Split content into lines
    lines = content.split('\n')
    
    for line in lines:
        # Check for enum header (### EnumName)
        if line.startswith('### '):
            # If we have a previous enum, save it
            if current_enum and current_items:
                chunks.append({
                    "enum_name": current_enum,
                    "content": format_enum_content(current_enum, current_items)
                })
            current_enum = line.replace('### ', '').strip()
            current_items = []
            continue
        
        # Skip table headers and empty lines
        if '|' not in line or line.startswith('| Key |') or line.startswith('|--'):
            continue
            
        # Parse enum items
        if line.strip():
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                key = parts[1].strip()
                description = parts[2].strip()
                if key and description:
                    current_items.append({"key": key, "description": description})
    
    # Don't forget to add the last enum
    if current_enum and current_items:
        chunks.append({
            "enum_name": current_enum,
            "content": format_enum_content(current_enum, current_items)
        })
    
    return chunks

def format_enum_content(enum_name, items):
    """Format enum content for embedding."""
    content = f"Enum: {enum_name}\n\nValues:\n"
    for item in items:
        content += f"- {item['key']}: {item['description']}\n"
    return content

def get_embedding(text):
    """Create embedding with rate limit handling."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=3072
            )
            return response.data[0].embedding
        except openai.RateLimitError:
            wait_time = (2 ** attempt) * 1
            print(f"Rate limit hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            time.sleep(1)
    
    print(f"Failed to generate embedding after {max_retries} attempts")
    return None

# Load and process all enum files
all_chunks = []
for input_file in input_files:
    print(f"Processing {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            chunks = parse_markdown_enum(content)
            all_chunks.extend(chunks)
            print(f"Found {len(chunks)} enums in {input_file}")
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
        continue
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        continue

# Generate embeddings
print("\nGenerating embeddings with OpenAI's text-embedding-3-large model...")
for chunk in tqdm(all_chunks):
    embedding = get_embedding(chunk["content"])
    if embedding:
        chunk["embedding"] = embedding
    time.sleep(0.5)  # Rate limiting precaution

# Count successful embeddings
successful_embeddings = sum(1 for chunk in all_chunks if "embedding" in chunk)
print(f"\nSuccessfully generated {successful_embeddings} embeddings out of {len(all_chunks)} chunks")

# Save the JSON with embeddings
try:
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_chunks, file, indent=4, ensure_ascii=False)
    print(f"Embeddings generated and saved to {output_file}!")
except Exception as e:
    print(f"Error saving embeddings: {e}")

print(f"Total chunks processed: {len(all_chunks)}") 