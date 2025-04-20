from openai import OpenAI
import os

class ResponseGenerator:
    def __init__(self, api_key=None):
        # Use environment variable if no key is provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Define specific prompts for each category
        self.category_prompts = {
            "Service Layer": """Você é um especialista em Service Layer do BFC-Script. 
            Suas respostas devem focar em:
            - Criação e implementação de serviços
            - Boas práticas de arquitetura em camadas
            - Padrões de design para serviços
            - Integração entre camadas
            - Tratamento de erros em serviços
            - Performance e otimização de serviços""",
            
            "Fonte de Dados": """Você é um especialista em Fontes de Dados do BFC-Script.
            Suas respostas devem focar em:
            - Conexão com diferentes tipos de bancos de dados
            - Queries e manipulação de dados
            - Otimização de consultas
            - Tratamento de transações
            - Cache e performance
            - Segurança e proteção de dados""",
            
            "Relatório": """Você é um especialista em Geração de Relatórios do BFC-Script.
            Suas respostas devem focar em:
            - Criação de relatórios
            - Formatação e layout
            - Agregação de dados
            - Gráficos e visualizações
            - Exportação em diferentes formatos
            - Personalização e templates"""
        }
    
    def extract_syntax_patterns(self, context):
        """
        Extract common BFC-Script syntax patterns from context.
        
        Args:
            context (str): Documentation context
            
        Returns:
            str: Extracted syntax patterns
        """
        try:
            from utils.prompts import SYNTAX_EXTRACTION_PROMPT
            
            syntax_prompt = SYNTAX_EXTRACTION_PROMPT.format(context=context)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um analisador sintático técnico que extrai padrões de código de documentação."},
                    {"role": "user", "content": syntax_prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao extrair padrões sintáticos: {str(e)}")
            return ""
    
    def get_category_from_query(self, query):
        """
        Extract category from query.
        
        Args:
            query (str): User query
            
        Returns:
            str: Category name
        """
        if "[Categoria:" in query:
            return query.split("[Categoria:")[1].split("]")[0].strip()
        return "Geral"
    
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
            
            # Extract category from query
            category = self.get_category_from_query(query)
            
            # Select category-specific prompt
            category_prompt = self.category_prompts.get(category, RAG_SYSTEM_PROMPT)
            
            # Incorporate chat history context for better continuity
            history_context = ""
            if history and len(history) > 0:
                last_exchanges = history[-3:] if len(history) > 3 else history
                history_context = "\n".join([f"Usuário: {q}\nAssistente: {a}" for q, a in last_exchanges])
            
            if not context:
                return "Não foi possível realizar a busca semântica. Verifique os logs para mais detalhes."
            
            # Extract syntax patterns for undocumented responses
            syntax_patterns = self.extract_syntax_patterns(context)
            
            # Build complete prompt
            prompt = RAG_USER_PROMPT.format(
                context=context,
                syntax_patterns=syntax_patterns,
                history_context=history_context,
                query=query
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": category_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return f"Ocorreu um erro ao processar sua consulta: {str(e)}"