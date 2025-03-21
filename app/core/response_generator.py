from openai import OpenAI
import os

class ResponseGenerator:
    def __init__(self, api_key=None):
        # Use environment variable if no key is provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def extract_syntax_patterns(self, context):
        """
        Extrai padrões sintáticos comuns do BFC-Script do contexto.
        
        Args:
            context (str): Documentation context
            
        Returns:
            str: Extracted syntax patterns
        """
        try:
            from utils.prompts import SYNTAX_EXTRACTION_PROMPT
            
            syntax_prompt = SYNTAX_EXTRACTION_PROMPT.format(context=context)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um analisador sintático técnico que extrai padrões de código de documentação."},
                    {"role": "user", "content": syntax_prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao extrair padrões sintáticos: {str(e)}")
            return ""
    
    def generate_response(self, query, context, history=None):
        """
        Generate a response for the user query using RAG.
        
        Args:
            query (str): The user's query
            context (str): Documentation context retrieved from search
            history (list): Chat history
            
        Returns:
            str: Generated response
        """
        try:
            from utils.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT
            
            # Incorporate chat history context for better continuity
            history_context = ""
            if history and len(history) > 0:
                last_exchanges = history[-3:] if len(history) > 3 else history
                history_context = "\n".join([f"Usuário: {q}\nAssistente: {a}" for q, a in last_exchanges])
            
            if not context:
                return "Não foi possível realizar a busca semântica. Verifique os logs para mais detalhes."
            
            # Extrair padrões sintáticos para uso em respostas não documentadas
            syntax_patterns = self.extract_syntax_patterns(context)
            
            # Montar o prompt completo
            prompt = RAG_USER_PROMPT.format(
                context=context,
                syntax_patterns=syntax_patterns,
                history_context=history_context,
                query=query
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return f"Ocorreu um erro ao processar sua consulta: {str(e)}"