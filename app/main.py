import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from core.semantic_search import SemanticSearch
from core.response_generator import ResponseGenerator
from core.initialize_chroma_db import initialize_chroma_db
from core.config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return

# Configure logging
logger = setup_logging(__name__, "logs/main.log")

def main():
    """
    Main entry point for the BFC-Script Assistant application.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY is not set in the environment. Please set it before running the application.")
            return
        
        # Configure environment to avoid tokenizer warning
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB...")
        try:
            initialize_chroma_db(reset_collections=False)  # Set to True if you want to reset collections
            logger.info("ChromaDB initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            return
        
        # Initialize main components
        logger.info("Initializing semantic search...")
        search_engine = SemanticSearch(api_key=api_key)
        
        logger.info("Initializing response generator...")
        response_generator = ResponseGenerator(api_key=api_key)
        
        # Create and launch the user interface
        logger.info("Launching user interface...")
        from ui.ui import BFCScriptUI
        bfc_ui = BFCScriptUI(search_engine, response_generator)
        bfc_ui.launch(share=True)
        
    except Exception as e:
        logger.error(f"Error starting BFC-Script Assistant: {str(e)}")
        raise

if __name__ == "__main__":
    main()