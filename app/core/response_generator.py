# response_generator.py
import os
import json
import openai
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return
import tiktoken

# Configure logging
logger = setup_logging(__name__, "logs/response_generator.log")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class ResponseGenerator:
    def __init__(self, api_key=None):
        """
        Initialize ResponseGenerator with OpenAI API key.
        
        Args:
            api_key: OpenAI API key
        """
        # Use environment variable if no key is provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Load prompts from prompts.py
        self.prompts = self._load_prompts()
        
        # Set system prompt from loaded prompts
        self.system_prompt = self.prompts.get("RAG_SYSTEM_PROMPT", "")
        
        # Initialize tokenizer
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        
        # Set maximum context length (leaving room for response)
        self.max_context_tokens = 6000  # Conservative limit to leave room for response
        
        # Configure token limits for different components
        self.max_syntax_patterns_tokens = 3000 # Limit for syntax patterns extraction
        self.max_history_tokens = 1000  # Limit for conversation history
        
        # Load common BFC-Script patterns
        self.bfc_patterns = self._load_bfc_patterns()
        
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))
    
    def truncate_context(self, context: str | List[str] | List[Dict], max_tokens: int) -> str:
        """
        Truncate context to fit within token limit while preserving structure.
        
        Args:
            context: Original context (string, list of strings, or list of dictionaries)
            max_tokens: Maximum number of tokens allowed
            
        Returns:
            Truncated context as string
        """
        # Convert list of dicts to string if necessary
        if isinstance(context, list):
            if context and isinstance(context[0], dict):
                # Extract content from dictionaries
                context = "\n\n".join(str(item.get('content', '')) for item in context)
            else:
                context = "\n\n".join(str(item) for item in context)
        
        # Split context into sections (assuming sections are separated by newlines)
        sections = context.split('\n\n')
        truncated_sections = []
        current_tokens = 0
        
        for section in sections:
            section_tokens = self.count_tokens(section)
            if current_tokens + section_tokens <= max_tokens:
                truncated_sections.append(section)
                current_tokens += section_tokens
            else:
                # If a single section is too long, truncate it
                if section_tokens > max_tokens:
                    # Try to preserve the first part of the section
                    words = section.split()
                    truncated_text = ""
                    for word in words:
                        if self.count_tokens(truncated_text + " " + word) <= max_tokens:
                            truncated_text += " " + word if truncated_text else word
                        else:
                            break
                    if truncated_text:
                        truncated_sections.append(truncated_text + "...")
                break
        
        return "\n\n".join(truncated_sections)
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Load prompts from prompts.py.
        
        Returns:
            Dictionary of prompts
        """
        try:
            # Import prompts from prompts.py
            from app.utils.prompts import (
                RAG_SYSTEM_PROMPT,
                RAG_USER_PROMPT,
                SYNTAX_EXTRACTION_PROMPT
            )
            
            # Create dictionary with prompts
            prompts = {
                "RAG_SYSTEM_PROMPT": RAG_SYSTEM_PROMPT,
                "RAG_USER_PROMPT": RAG_USER_PROMPT,
                "SYNTAX_EXTRACTION_PROMPT": SYNTAX_EXTRACTION_PROMPT
            }
            
            logger.info("Loaded prompts from prompts.py")
            return prompts
            
        except Exception as e:
            logger.error(f"Error loading prompts from prompts.py: {str(e)}")
                  
    
    def _load_bfc_patterns(self) -> Dict[str, Any]:
        """
        Load common BFC-Script patterns for better code generation.
        
        Returns:
            Dictionary of BFC-Script patterns
        """
        return {
            "data_sources": {
                "folha": {
                    "cargo": "Dados.folha.v2.cargo",
                    "funcionario": "Dados.folha.v2.funcionario",
                    "contrato": "Dados.folha.v2.contrato",
                    "evento": "Dados.folha.v2.evento",
                    "rubrica": "Dados.folha.v2.rubrica",
                    "lancamento": "Dados.folha.v2.lancamento",
                    "historico": "Dados.folha.v2.historico",
                    "movimento": "Dados.folha.v2.movimento"
                },
                "pessoal": {
                    "funcionario": "Dados.pessoal.v2.funcionario",
                    "contrato": "Dados.pessoal.v2.contrato",
                    "cargo": "Dados.pessoal.v2.cargo",
                    "departamento": "Dados.pessoal.v2.departamento",
                    "centro_custo": "Dados.pessoal.v2.centroCusto"
                }
            },
            "common_functions": {
                "busca": "busca(campos: string, filtros: object, ordenacao: string)",
                "percorrer": "percorrer(colecao) { item -> ... }",
                "filtro": "filtro(campo, operador, valor)",
                "ordenacao": "ordenacao(campo, direcao)"
            }
        }
    
    def extract_syntax_patterns(self, context: str) -> str:
        """
        Extract common BFC-Script syntax patterns from context.
        
        Args:
            context: Documentation context
            
        Returns:
            Extracted syntax patterns
        """
        try:
            # Truncate context for syntax extraction to avoid token limit
            truncated_context = self.truncate_context(context, self.max_syntax_patterns_tokens)
            
            # Get the prompt template and ensure it's a string
            prompt_template = self.prompts.get("SYNTAX_EXTRACTION_PROMPT", "")
            if isinstance(prompt_template, list):
                prompt_template = "\n".join(prompt_template)
            
            # Format the prompt with the context
            syntax_prompt = prompt_template.format(context=truncated_context)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um analisador sintático técnico que extrai padrões de código de documentação."},
                    {"role": "user", "content": syntax_prompt}
                ],
                temperature=0.3  # Lower temperature for more consistent pattern extraction
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao extrair padrões sintáticos: {str(e)}")
            return "Não foi possível extrair padrões sintáticos."
    
    def format_history(self, history: List[Tuple[str, str]], max_entries: int = 2) -> str:
        """
        Format conversation history for inclusion in prompt.
        
        Args:
            history: List of (query, response) tuples
            max_entries: Maximum number of history entries to include
            
        Returns:
            Formatted history string
        """
        if not history:
            return ""
            
        # Take the most recent entries
        last_exchanges = history[-max_entries:] if len(history) > max_entries else history
        
        # Format as conversation
        history_parts = []
        for i, (q, a) in enumerate(last_exchanges):
            history_parts.append(f"[Conversa {i+1}]\nUsuário: {q}\nAssistente: {a}")
        
        history_text = "\n\n".join(history_parts)
        
        # Truncate history if too long
        if self.count_tokens(history_text) > self.max_history_tokens:
            history_text = self.truncate_context(history_text, self.max_history_tokens)
        
        return history_text
    
    def extract_function_requirements(self, query: str) -> Dict[str, Any]:
        """
        Extract function requirements from the query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary of function requirements
        """
        requirements = {
            "entity": None,
            "fields": [],
            "filters": [],
            "ordering": None
        }
        
        # Common entity keywords
        entity_keywords = {
            "cargo": ["cargo", "cargos", "cbo"],
            "funcionario": ["funcionario", "funcionários", "colaborador", "colaboradores"],
            "contrato": ["contrato", "contratos"],
            "evento": ["evento", "eventos"],
            "rubrica": ["rubrica", "rubricas"],
            "lancamento": ["lancamento", "lançamentos"],
            "historico": ["historico", "histórico"],
            "movimento": ["movimento", "movimentos"],
            "departamento": ["departamento", "departamentos"],
            "centro_custo": ["centro de custo", "centro de custos", "centro_custo", "centro_custos"]
        }
        
        # Detect entity
        query_lower = query.lower()
        for entity, keywords in entity_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    requirements["entity"] = entity
                    break
            if requirements["entity"]:
                break
        
        # Extract fields
        if "campos" in query_lower:
            # Try to extract fields from the query
            # This is a simple approach and might need improvement
            field_keywords = ["cbo", "id", "descricao", "tipo", "codigo", "nome", "data", "valor"]
            for keyword in field_keywords:
                if keyword in query_lower:
                    requirements["fields"].append(keyword)
        
        # If no fields were detected, add some defaults based on entity
        if not requirements["fields"] and requirements["entity"]:
            if requirements["entity"] == "cargo":
                requirements["fields"] = ["id", "descricao"]
            elif requirements["entity"] == "funcionario":
                requirements["fields"] = ["id", "nome"]
            elif requirements["entity"] == "contrato":
                requirements["fields"] = ["id", "dataInicio", "dataFim"]
        
        return requirements
    
    def generate_response(self, query: str, context: str | List[str] | List[Dict], history: Optional[List[Tuple[str, str]]] = None) -> str:
        """
        Generate a response for the user query using RAG.
        
        Args:
            query: The user's query
            context: Documentation context retrieved from search (string, list of strings, or list of dictionaries)
            history: Chat history as list of (query, response) tuples
            
        Returns:
            Generated response
        """
        try:
            # Convert context to string if it's a list
            if isinstance(context, list):
                if context and isinstance(context[0], dict):
                    # Extract content from dictionaries
                    context = "\n\n".join(str(item.get('content', '')) for item in context)
                else:
                    context = "\n\n".join(str(item) for item in context)
            
            # Extract function requirements if this is a code generation query
            is_code_query = any(keyword in query.lower() for keyword in ["criar", "crie", "script", "código", "codigo", "função", "funcao"])
            function_requirements = None
            
            if is_code_query:
                function_requirements = self.extract_function_requirements(query)
                logger.info(f"Extracted function requirements: {function_requirements}")
            
            # If context is empty, try to generate a response anyway
            if not context:
                logger.warning(f"Empty context for query: {query}")
                
                # For code generation queries, use the function requirements
                if is_code_query and function_requirements:
                    # Create a minimal context with the function requirements
                    entity = function_requirements["entity"]
                    fields = function_requirements["fields"]
                    
                    if entity and fields:
                        # Get the data source from our patterns
                        data_source = None
                        for source_type, sources in self.bfc_patterns["data_sources"].items():
                            if entity in sources:
                                data_source = sources[entity]
                                break
                        
                        if data_source:
                            # Create a minimal context with the data source and fields
                            context = f"Fonte de dados: {data_source}\nCampos disponíveis: {', '.join(fields)}"
                            logger.info(f"Created minimal context: {context}")
                        else:
                            context = "Não há documentação específica disponível para esta consulta. Por favor, forneça uma resposta baseada no seu conhecimento geral sobre BFC-Script."
                    else:
                        context = "Não há documentação específica disponível para esta consulta. Por favor, forneça uma resposta baseada no seu conhecimento geral sobre BFC-Script."
                else:
                    context = "Não há documentação específica disponível para esta consulta. Por favor, forneça uma resposta baseada no seu conhecimento geral sobre BFC-Script."
            
            # Format history if available
            history_context = self.format_history(history) if history else ""
            
            # Extract syntax patterns for undocumented responses
            syntax_patterns = self.extract_syntax_patterns(context)
            
            # Add common BFC-Script patterns to syntax patterns
            if self.bfc_patterns:
                syntax_patterns += "\n\nPadrões comuns do BFC-Script:\n"
                
                # Add data sources
                syntax_patterns += "\nFontes de dados:\n"
                for source_type, sources in self.bfc_patterns["data_sources"].items():
                    syntax_patterns += f"- {source_type}:\n"
                    for entity, source in sources.items():
                        syntax_patterns += f"  - {entity}: {source}\n"
                
                # Add common functions
                syntax_patterns += "\nFunções comuns:\n"
                for func, signature in self.bfc_patterns["common_functions"].items():
                    syntax_patterns += f"- {func}: {signature}\n"
            
            # Build user prompt with all necessary context
            user_prompt = self.prompts.get("RAG_USER_PROMPT").format(
                context=context,
                syntax_patterns=syntax_patterns,
                history_context=history_context,
                query=query
            )
            
            # Count tokens and truncate if necessary
            total_tokens = (
                self.count_tokens(self.system_prompt) +
                self.count_tokens(user_prompt)
            )
            
            if total_tokens > self.max_context_tokens:
                logger.warning(f"Context too long ({total_tokens} tokens), truncating...")
                # Truncate context while preserving structure
                truncated_context = self.truncate_context(context, self.max_context_tokens)
                user_prompt = self.prompts.get("RAG_USER_PROMPT").format(
                    context=truncated_context,
                    syntax_patterns=syntax_patterns,
                    history_context=history_context,
                    query=query
                )
            
            # Generate response with appropriate model
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=2000  # Adjust based on expected response length
            )

            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return f"Desculpe, ocorreu um erro ao processar sua consulta. Por favor, tente novamente ou reformule sua pergunta."