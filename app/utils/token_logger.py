# app/utils/token_logger.py
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import os
import logging # Usar logging para melhor controle

# Configurar um logger básico para este módulo
logger = logging.getLogger(__name__)
# Para ver os prints de debug no console ao rodar test_query.py diretamente:
# Se não houver outra configuração de logging, isso garante que as mensagens apareçam.
if not logger.handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TokenLogger:
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir.resolve()  # Resolve para caminho absoluto imediatamente
        logger.debug(f"[TokenLogger-__init__] Current working directory: {os.getcwd()}")
        logger.debug(f"[TokenLogger-__init__] Resolved log directory: {self.log_dir}")
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[TokenLogger-__init__] Log directory ensured/created at: {self.log_dir}")
        except Exception as e:
            logger.error(f"[TokenLogger-__init__] Failed to create log directory {self.log_dir}: {e}", exc_info=True)

    def log_llm_payload(self, payload: Dict[str, Any], retry_attempt: int = 0) -> None:
        """Logs the payload sent to the LLM API."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename_suffix = f"retry_{retry_attempt}_{timestamp}" if retry_attempt > 0 else timestamp
        
        file_path = self.log_dir / f"llm_payload_{filename_suffix}.json"
        
        logger.debug(f"[TokenLogger-log_llm_payload] Attempting to log payload to: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            logger.info(f"[TokenLogger-log_llm_payload] LLM payload logged successfully to {file_path}")
        except Exception as e:
            logger.error(f"[TokenLogger-log_llm_payload] Error logging LLM payload to {file_path}: {e}", exc_info=True)

    def log_token_usage(self, model_name: str, prompt_tokens: int, completion_tokens: int, total_tokens: int, cost: float) -> None:
        """Logs token usage and cost to a CSV file."""
        # (Implementação original)
        # ...
        pass # Manter a implementação original aqui se houver

    def log_search_results(self, query: str, results: Any, analysis: Dict[str, Any]) -> None:
        """Logs semantic search results."""
        # (Implementação original)
        # ...
        pass # Manter a implementação original aqui se houver
