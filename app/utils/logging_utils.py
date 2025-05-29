import logging
import json
from datetime import datetime
from typing import List, Dict, Any

# Configuração do logger
logger = logging.getLogger('context_logger')
logger.setLevel(logging.DEBUG)

# Handler para arquivo
file_handler = logging.FileHandler('logs/context_logs.log')
file_handler.setLevel(logging.DEBUG)

# Formato do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_context_details(query: str, context: str, function_requirements: Dict[str, Any], 
                       syntax_patterns: str, history_context: str) -> None:
    """
    Registra detalhes completos do contexto sendo enviado para a LLM.
    
    Args:
        query: Consulta do usuário
        context: Contexto processado
        function_requirements: Requisitos extraídos da consulta
        syntax_patterns: Padrões sintáticos extraídos
        history_context: Contexto do histórico de conversa
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Estrutura do log
    log_data = {
        'timestamp': timestamp,
        'query': query,
        'context_blocks': context.split('\n\n'),  # Divide o contexto em blocos
        'function_requirements': function_requirements,
        'syntax_patterns': syntax_patterns,
        'history_context': history_context
    }
    
    # Log detalhado
    logger.debug("="*80)
    logger.debug(f"CONSULTA: {query}")
    logger.debug("-"*80)
    logger.debug("BLOCOS DE CONTEXTO:")
    for i, block in enumerate(log_data['context_blocks'], 1):
        logger.debug(f"\nBLOCO {i}:")
        logger.debug(block)
    logger.debug("-"*80)
    logger.debug("REQUISITOS DA FUNÇÃO:")
    logger.debug(json.dumps(function_requirements, indent=2, ensure_ascii=False))
    logger.debug("-"*80)
    logger.debug("PADRÕES SINTÁTICOS:")
    logger.debug(syntax_patterns)
    logger.debug("-"*80)
    logger.debug("HISTÓRICO DE CONVERSA:")
    logger.debug(history_context)
    logger.debug("="*80) 