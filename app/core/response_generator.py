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
        """Prepare the messages for the model."""
        try:
            # Log input data for debugging
            logging.info(f"Preparing prompt for query: {query}")
            logging.info(f"Number of search results: {len(search_results)}")
            logging.info(f"Query analysis: {query_analysis}")
            
            # Format context from search results
            context_parts = []
            for result in search_results:
                if isinstance(result, dict):
                    collection = result.get('collection', 'unknown')
                    content = result.get('content', '')
                    context_parts.append(f"Source: {collection}\nContent: {content}")
                else:
                    logging.warning(f"Unexpected result type: {type(result)}")
                    context_parts.append(str(result))
            
            context = "\n\n".join(context_parts)
            
            # Build the messages
            messages = []
            
            # Add conversation history if available
            if conversation_history:
                for user, assistant in conversation_history[-3:]:  # Last 3 exchanges
                    messages.extend([
                        {"role": "user", "content": user},
                        {"role": "assistant", "content": assistant}
                    ])
            
            # Always use the new RAG_SYSTEM_PROMPT, formatted with query and context
            system_message = RAG_SYSTEM_PROMPT.format(query=query, context=context)
            messages.append({"role": "system", "content": system_message})
            
            # User message is just a repeat of the query for clarity (optional)
            messages.append({"role": "user", "content": query})
            
            logging.info(f"Generated messages count: {len(messages)}")
            return messages
            
        except Exception as e:
            logging.error(f"Error preparing prompt: {e}", exc_info=True)
            raise
    
    def generate_response(self,
                         query: str,
                         search_results: List[Dict[str, Any]],
                         query_analysis: Dict[str, Any],
                         conversation_history: Optional[List[tuple]] = None) -> str:
        """Generate a response using GPT-4o-mini."""
        try:
            # Prepare the messages
            messages = self._prepare_prompt(
                query=query,
                search_results=search_results,
                query_analysis=query_analysis,
                conversation_history=conversation_history
            )
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=4096,
                top_p=0.4,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and return the response
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating response: {e}", exc_info=True)
            return f"Desculpe, ocorreu um erro ao gerar a resposta: {str(e)}" 