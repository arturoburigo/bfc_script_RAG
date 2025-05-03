import logging
import os
from datetime import datetime
from typing import Dict, Optional

class TokenLogger:
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the token logger.
        
        Args:
            log_dir (str): Directory where log files will be stored
        """
        self.log_dir = log_dir
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"token_usage_{timestamp}.log")
        
        self.logger = logging.getLogger("token_logger")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(fh)
        
    def log_token_usage(self, 
                        max_context_tokens: int,
                        max_syntax_patterns_tokens: int,
                        max_history_tokens: int,
                        actual_context_tokens: Optional[int] = None,
                        actual_syntax_patterns_tokens: Optional[int] = None,
                        actual_history_tokens: Optional[int] = None,
                        query: Optional[str] = None):
        """
        Log token usage information.
        
        Args:
            max_context_tokens (int): Maximum tokens allocated for context
            max_syntax_patterns_tokens (int): Maximum tokens allocated for syntax patterns
            max_history_tokens (int): Maximum tokens allocated for history
            actual_context_tokens (int, optional): Actual tokens used in context
            actual_syntax_patterns_tokens (int, optional): Actual tokens used in syntax patterns
            actual_history_tokens (int, optional): Actual tokens used in history
            query (str, optional): The user query that triggered this token usage
        """
        log_message = (
            f"\nToken Usage Summary:\n"
            f"Query: {query if query else 'N/A'}\n"
            f"Maximum Allocations:\n"
            f"  - Context: {max_context_tokens} tokens\n"
            f"  - Syntax Patterns: {max_syntax_patterns_tokens} tokens\n"
            f"  - History: {max_history_tokens} tokens\n"
        )
        
        if all(v is not None for v in [actual_context_tokens, actual_syntax_patterns_tokens, actual_history_tokens]):
            log_message += (
                f"Actual Usage:\n"
                f"  - Context: {actual_context_tokens} tokens ({actual_context_tokens/max_context_tokens*100:.1f}% of max)\n"
                f"  - Syntax Patterns: {actual_syntax_patterns_tokens} tokens ({actual_syntax_patterns_tokens/max_syntax_patterns_tokens*100:.1f}% of max)\n"
                f"  - History: {actual_history_tokens} tokens ({actual_history_tokens/max_history_tokens*100:.1f}% of max)\n"
            )
            
        self.logger.info(log_message) 