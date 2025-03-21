import os
from app.core.semantic_search import SemanticSearch
from app.ui.ui import BFCScriptUI

def main():
    """
    Main entry point for the BFC-Script Assistant application.
    """
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("AVISO: OPENAI_API_KEY não está definida no ambiente. Por favor, defina-a antes de executar o aplicativo.")
        return
    
    try:
        # Initialize the semantic search engine
        search_engine = SemanticSearch(api_key=api_key)
        
        # Create and launch the UI
        bfc_ui = BFCScriptUI(search_engine)
        bfc_ui.launch(share=True)
    except Exception as e:
        print(f"Erro ao iniciar o BFC-Script Assistant: {str(e)}")

if __name__ == "__main__":
    main()