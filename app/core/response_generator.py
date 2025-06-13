import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..utils.prompts import RAG_SYSTEM_PROMPT

class ResponseGenerator:
    """Response generator using GPT-4o-mini."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        logging.info("ResponseGenerator initialized with GPT-4o-mini")
    
    def _prepare_prompt(self, 
                       query: str, 
                       search_results: List[Dict[str, Any]], 
                       query_analysis: Dict[str, Any],
                       conversation_history: Optional[List[tuple]] = None) -> List[Dict[str, str]]:
        """
        Prepara as mensagens para o modelo com uma estrutura clara:
        1. Histórico da Conversa (se houver).
        2. Mensagem de Sistema: Contém apenas as regras (RAG_SYSTEM_PROMPT).
        3. Mensagem de Usuário: Contém o contexto recuperado e a query atual.
        """
        try:
            # Formata o contexto dos resultados da busca
            context_parts = []
            for result in search_results:
                if isinstance(result, dict):
                    collection = result.get('collection', 'unknown')
                    content = result.get('content', '')
                    # Adiciona uma formatação clara para cada parte do contexto
                    context_parts.append(f"### Bloco de Documentação (Fonte: {collection})\n{content}")
                else:
                    context_parts.append(str(result))
            
            context = "\n\n".join(context_parts)
            
            # Monta o conteúdo da mensagem de usuário com o contexto e a query
            user_prompt_content = (
                f"## DOCUMENTAÇÃO Recuperada:\n"
                f"{context}\n\n"
                f"---------------------\n\n"
                f"## QUERY DO USUÁRIO:\n"
                f"{query}"
            )

            # Inicia a lista de mensagens
            messages = []
            
            # Adiciona o histórico da conversa (se disponível)
            if conversation_history:
                for user, assistant in conversation_history[-3:]:
                    messages.extend([
                        {"role": "user", "content": user},
                        {"role": "assistant", "content": assistant}
                    ])
            
            # Adiciona a mensagem de sistema (APENAS as regras)
            messages.append({"role": "system", "content": RAG_SYSTEM_PROMPT})
            
            # Adiciona a mensagem de usuário (Contexto + Query)
            messages.append({"role": "user", "content": user_prompt_content})
            
            logging.info("Prompt preparado com sucesso, separando regras do conteúdo.")
            return messages
            
        except Exception as e:
            logging.error(f"Erro ao preparar o prompt: {e}", exc_info=True)
            raise
    
    def generate_response(self,
                         query: str,
                         search_results: List[Dict[str, Any]],
                         query_analysis: Dict[str, Any],
                         conversation_history: Optional[List[tuple]] = None) -> str:
        """Gera uma resposta usando o GPT-4o-mini."""
        try:
            # Prepara as mensagens com a nova estrutura
            messages = self._prepare_prompt(
                query=query,
                search_results=search_results,
                query_analysis=query_analysis,
                conversation_history=conversation_history
            )
            
            # Gera a resposta
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2, # Um pouco mais baixo para seguir regras estritas
                max_tokens=4096,
                top_p=0.4,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extrai e retorna o conteúdo da resposta
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Erro ao gerar a resposta: {e}", exc_info=True)
            return f"Desculpe, ocorreu um erro ao gerar a resposta: {str(e)}"