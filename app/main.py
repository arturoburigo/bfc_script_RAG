# app/main.py - Versão com Auto-Fix Genérico
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import setup_logging, is_dev_mode

# Configure logging
logger = setup_logging(__name__, "logs/main.log")

def main():
    """
    Main entry point with automatic context processing fix.
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
        
        logger.info("Starting BFC-Script Assistant with automatic fixes...")
        
        # Apply generic context processing fix
        try:
            logger.info("Applying generic context processing fixes...")
            from app.core.context_processor import auto_patch
            # auto_patch() is called automatically when context_processor is imported
            logger.info("Generic fixes applied successfully")
        except Exception as e:
            logger.warning(f"Could not apply generic fixes: {e}")
        
        # Try to use optimized system first
        try:
            from app.core.simple_optimized_system import create_simple_rag_system
            
            # Create optimized RAG system
            rag_system = create_simple_rag_system(api_key=api_key)
            logger.info("Using optimized RAG system with generic fixes")
            
            # Initialize ChromaDB
            if not os.path.exists("./chroma_db") or len(os.listdir("./chroma_db")) == 0:
                logger.info("ChromaDB not found or empty, initializing...")
                init_stats = rag_system.initialize_database(reset_collections=False)
                logger.info(f"ChromaDB initialized: {init_stats}")
            else:
                logger.info("ChromaDB already exists, loading existing collections...")
                rag_system.search_engine._load_collections()
                rag_system.is_initialized = True
                logger.info("Existing ChromaDB loaded successfully")
            
            # Get system status
            status = rag_system.get_system_status()
            logger.info(f"System Status: {status}")
            
            # Create and launch optimized UI
            logger.info("Launching optimized user interface...")
            from app.ui.simple_optimized_ui import SimpleOptimizedBFCScriptUI
            
            bfc_ui = SimpleOptimizedBFCScriptUI(rag_system)
            bfc_ui.run(share=True)
            
        except ImportError as e:
            logger.warning(f"Could not import optimized system ({e}), falling back to original system...")
            
            # Fallback to original system with fixes applied
            from app.core.semantic_search import SemanticSearch
            from app.core.response_generator import ResponseGenerator
            from app.core.initialize_chroma_db import initialize_chroma_db
            
            # Initialize ChromaDB
            logger.info("Initializing ChromaDB...")
            try:
                initialize_chroma_db(reset_collections=False)
                logger.info("ChromaDB initialization completed successfully")
            except Exception as e:
                logger.error(f"Error initializing ChromaDB: {str(e)}")
                return
            
            # Initialize main components
            logger.info("Initializing semantic search...")
            search_engine = SemanticSearch(api_key=api_key)
            
            logger.info("Initializing response generator (with fixes)...")
            response_generator = ResponseGenerator(api_key=api_key)
            
            # Create and launch the original user interface
            logger.info("Launching original user interface...")
            from app.ui.optimized_ui import SimpleOptimizedBFCScriptUI
            bfc_ui = SimpleOptimizedBFCScriptUI(search_engine, response_generator)
            bfc_ui.run(share=True)
        
    except Exception as e:
        logger.error(f"Error starting BFC-Script Assistant: {str(e)}")
        raise

if __name__ == "__main__":
    main()