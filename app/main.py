import os
from core.semantic_search import SemanticSearch
from core.response_generator import ResponseGenerator
from ui.ui import BFCScriptUI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the BFC-Script Assistant application.
    """
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY is not set in the environment. Please set it before running the application.")
        return
    
    # Configurar ambiente para evitar warning do tokenizer
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    try:
        # Initialize main components
        search_engine = SemanticSearch(api_key=api_key)
        response_generator = ResponseGenerator(api_key=api_key)
        
        # Create and launch the user interface
        bfc_ui = BFCScriptUI(search_engine, response_generator)
        bfc_ui.launch(share=True)
    except Exception as e:
        print(f"Error starting BFC-Script Assistant: {str(e)}")

if __name__ == "__main__":
    main()