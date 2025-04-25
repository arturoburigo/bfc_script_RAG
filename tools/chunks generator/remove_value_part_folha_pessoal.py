import os
import re
from pathlib import Path

def process_file(file_path):
    """
    Process a single file to remove ", Value:" and everything after it until the next ")"
    Remove a parte inutil do enum pessoal e do enum folha.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Use regex to find and replace the pattern
    # This will match ", Value:" followed by any characters until the next ")"
    pattern = r', Value:[^)]*\)'
    new_content = re.sub(pattern, ')', content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    return file_path

def main():
    # Define the directory containing the text files
    current_dir = Path(__file__).parent.parent.parent
    chunks_dir = current_dir / "chunks" / "enums_pessoal_and_folha"
    
    print(f"Processing files in: {chunks_dir}")
    
    # Process all .txt files in the directory
    processed_files = 0
    for file_path in chunks_dir.glob("*.txt"):
        try:
            process_file(file_path)
            processed_files += 1
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Successfully processed {processed_files} files")

if __name__ == "__main__":
    main() 