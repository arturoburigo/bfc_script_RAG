import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment modes
ENV_DEV = "dev"
ENV_PROD = "prod"

# Default to development mode if not specified
ENV_MODE = os.getenv("ENV_MODE", ENV_DEV)

# Logging configuration
LOG_LEVEL = logging.DEBUG if ENV_MODE == ENV_DEV else logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# Log file paths
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging for the application
def setup_logging(name, log_file=None):
    """
    Set up logging for a module.
    
    Args:
        name: Name of the logger
        log_file: Optional log file path
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
    
    return logger

# Function to check if we're in development mode
def is_dev_mode():
    """
    Check if the application is running in development mode.
    
    Returns:
        bool: True if in development mode, False otherwise
    """
    return ENV_MODE == ENV_DEV

# Function to log debug information only in development mode
def log_debug(logger, message, *args, **kwargs):
    """
    Log debug information only in development mode.
    
    Args:
        logger: Logger instance
        message: Message to log
        *args: Additional arguments for logger.debug
        **kwargs: Additional keyword arguments for logger.debug
    """
    if is_dev_mode():
        logger.debug(message, *args, **kwargs)

# Function to log detailed information about function calls
def log_function_call(logger, func_name, args=None, kwargs=None):
    """
    Log detailed information about function calls in development mode.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being called
        args: Positional arguments
        kwargs: Keyword arguments
    """
    if is_dev_mode():
        args_str = str(args) if args else "()"
        kwargs_str = str(kwargs) if kwargs else "{}"
        logger.debug(f"CALL: {func_name}{args_str} {kwargs_str}")

# Function to log detailed information about function returns
def log_function_return(logger, func_name, result):
    """
    Log detailed information about function returns in development mode.
    
    Args:
        logger: Logger instance
        func_name: Name of the function returning
        result: Return value
    """
    if is_dev_mode():
        # Truncate long results for readability
        result_str = str(result)
        if len(result_str) > 500:
            result_str = result_str[:500] + "... (truncated)"
        logger.debug(f"RETURN: {func_name} -> {result_str}")

# Function to log detailed information about search results
def log_search_results(logger, query, results):
    """
    Log detailed information about search results in development mode.
    
    Args:
        logger: Logger instance
        query: Search query
        results: Search results
    """
    if is_dev_mode():
        logger.debug(f"SEARCH QUERY: {query}")
        logger.debug(f"SEARCH RESULTS COUNT: {len(results)}")
        
        for i, result in enumerate(results):
            relevance = result.get("relevance_score", 0.0)
            collection = result.get("collection", "unknown")
            logger.debug(f"RESULT {i+1}: Collection={collection}, Relevance={relevance:.4f}")
            
            # Log metadata if available
            metadata = result.get("metadata", {})
            if metadata:
                logger.debug(f"  METADATA: {metadata}")
            
            # Log a snippet of the content
            content = result.get("content", "")
            if content:
                snippet = content[:200] + "..." if len(content) > 200 else content
                logger.debug(f"  CONTENT SNIPPET: {snippet}") 