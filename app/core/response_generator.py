# response_generator.py
import os
import json
import openai
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return
import tiktoken
import re
from app.utils.token_logger import TokenLogger
from ..utils.logging_utils import log_context_details

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
        self.max_context_tokens = 12000  # Aumento do limite para deixar mais espaço para contexto
        
        # Configure token limits for different components
        self.max_syntax_patterns_tokens = 3000 # Limit for syntax patterns extraction
        self.max_history_tokens = 2000  # Increased limit for conversation history
        
        # Initialize token logger
        self.token_logger = TokenLogger()
        
        # Common data sources and patterns to check in context
        self.data_sources = {
            "folha": ["Dados.folha.v2"],
            "pessoal": ["Dados.pessoal.v2"]
        }
        
        # Core entity patterns
        self.entity_patterns = {
            "funcionario": ["funcionario", "matriculas", "matricula"],
            "matricula": ["funcionario", "matriculas", "matricula"],
            "evento": ["evento", "eventos", "rubrica", "rubricas",],
            "rubrica": ["rubrica", "rubricas", "evento", "eventos"],
        }

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
                SYNTAX_EXTRACTION_PROMPT,
                REPORT_GENERATION_PROMPT
            )
            
            # Create dictionary with prompts
            prompts = {
                "RAG_SYSTEM_PROMPT": RAG_SYSTEM_PROMPT,
                "RAG_USER_PROMPT": RAG_USER_PROMPT,
                "SYNTAX_EXTRACTION_PROMPT": SYNTAX_EXTRACTION_PROMPT,
                "REPORT_GENERATION_PROMPT": REPORT_GENERATION_PROMPT
            }
            
            logger.info("Loaded prompts from prompts.py")
            return prompts
            
        except Exception as e:
            logger.error(f"Error loading prompts from prompts.py: {str(e)}")
            return {}
                  
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
    
    def format_history(self, history: List[Tuple[str, str]], max_entries: int = 5) -> str:
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
        
        # Format as conversation with clear separation
        history_parts = []
        for i, (q, a) in enumerate(last_exchanges):
            history_parts.append(f"[Conversa {i+1}]")
            history_parts.append(f"Usuário: {q}")
            history_parts.append(f"Assistente: {a}")
            history_parts.append("-" * 40)  # Add separator between exchanges
        
        history_text = "\n".join(history_parts)
        
        # Increase history token limit
        if self.count_tokens(history_text) > self.max_history_tokens:
            # Instead of truncating, try to keep more recent exchanges
            while self.count_tokens(history_text) > self.max_history_tokens and len(last_exchanges) > 1:
                last_exchanges = last_exchanges[1:]  # Remove oldest exchange
                history_parts = []
                for i, (q, a) in enumerate(last_exchanges):
                    history_parts.append(f"[Conversa {i+1}]")
                    history_parts.append(f"Usuário: {q}")
                    history_parts.append(f"Assistente: {a}")
                    history_parts.append("-" * 40)
                history_text = "\n".join(history_parts)
        
        return history_text
    
    def _extract_code_examples_from_context(self, context: str) -> List[Dict]:
        """
        Extract code examples and their context from the documentation.
        
        Args:
            context: Documentation context
            
        Returns:
            List of extracted examples with their full context
        """
        code_examples = []
        
        # Se o contexto começa com # ou ## provavelmente é uma documentação completa
        if context.strip().startswith('#'):
            # Extrai o título/nome da API
            title = context.split('\n')[0].strip('# ')
            
            # Procura por blocos de código (entre ```)
            code_blocks = re.findall(r'```\n(.*?)```', context, re.DOTALL)
            
            if code_blocks:
                # Adiciona o contexto completo com o código
                code_examples.append({
                    "title": title,
                    "full_content": context,  # Documento completo
                    "code": code_blocks[0].strip(),  # Código extraído
                    "index": 1
                })
        
        return code_examples
    
    def _find_data_sources_in_context(self, context: str) -> Dict[str, List[str]]:
        """
        Find data sources mentioned in the context.
        
        Args:
            context: Documentation context
            
        Returns:
            Dictionary of domain -> sources
        """
        found_sources = {
            "folha": [],
            "pessoal": []
        }
        
        # Look for data source patterns like Dados.folha.v2.X or Dados.pessoal.v2.Y
        folha_sources = re.findall(r'Dados\.folha\.v2\.([a-zA-Z0-9_]+)', context)
        pessoal_sources = re.findall(r'Dados\.pessoal\.v2\.([a-zA-Z0-9_]+)', context)
        
        # Deduplicate
        found_sources["folha"] = list(set(folha_sources))
        found_sources["pessoal"] = list(set(pessoal_sources))
        
        return found_sources
    
    def _find_enums_in_context(self, context: str) -> List[Dict[str, Any]]:
        """
        Find enum types mentioned in the context with their values and descriptions.
        
        Args:
            context: Documentation context
            
        Returns:
            List of dictionaries containing enum information:
            {
                "name": str,            # Nome do enum
                "values": List[Dict]    # Lista de valores do enum
            }
        """
        found_enums = []
        
        # Procura por padrões de enum no formato dos embeddings
        # Exemplo: # ClassificacaoRais\nEnum: ClassificacaoRais
        enum_blocks = re.finditer(r'#\s*(\w+)\s*\nEnum:\s*\1\n((?:[-\d]+[^\n]+\(Key:[^\n]+\n?)*)', context)
        
        for match in enum_blocks:
            enum_name = match.group(1)
            values_block = match.group(2)
            
            # Extrai os valores do enum
            # Exemplo: 10 - Rescisão... (Key: RESCISAO_...)
            values = []
            for value_match in re.finditer(r'(\d+)\s*-\s*([^(]+)\(Key:\s*(\w+)\)', values_block):
                values.append({
                    "description": value_match.group(2).strip(),  # Descrição
                    "key": value_match.group(3).strip()     # Chave do enum
                })
            
            if values:  # Só adiciona se encontrou valores
                found_enums.append({
                    "name": enum_name,
                    "values": values
                })
        
        return found_enums
    
    def extract_function_requirements(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract function requirements from the query including domain-specific entities, 
        fields, data sources, and domain-specific information. Uses context when available.
        
        Args:
            query: User query
            context: Optional search context to extract more accurate requirements
            
        Returns:
            Dictionary of function requirements
        """
        requirements = {
            "entity": None,
            "entity_type": None,
            "fields": [],
            "filters": [],
            "ordering": None,
            "data_source": None,
            "version": "v2",  # Default version
            "enum_type": None,
            "is_script_query": False,
            "code_examples": [],
            "specific_operations": []
        }
        
        # Check if this is a script generation query
        script_keywords = ["criar", "crie", "gere", "gerar", "script", "código", "codigo", 
                          "função", "funcao", "buscar", "busque", "consultar", "consulte", 
                          "implementar", "implementação", "exemplo", "explique", "crie um script"]
        query_lower = query.lower()
        
        requirements["is_script_query"] = any(keyword in query_lower for keyword in script_keywords)
        
        # Extract code examples from context if available
        if context and requirements["is_script_query"]:
            code_examples = self._extract_code_examples_from_context(context)
            if code_examples:
                requirements["code_examples"] = code_examples
                logger.info(f"Found {len(code_examples)} code examples in context")
        
        # For data source related queries
        for entity, patterns in self.entity_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                requirements["entity"] = entity
                logger.info(f"Detected entity: {entity}")
                
                # Determine likely domain (folha or pessoal)
                if "folha" in query_lower:
                    requirements["data_source"] = "Dados.folha.v2"
                    requirements["entity_type"] = "folha"
                elif "pessoal" in query_lower or entity in ["funcionario", "cargo", "contrato"]:
                    requirements["data_source"] = "Dados.pessoal.v2"
                    requirements["entity_type"] = "pessoal"
                
                # Use context to refine the data source if available
                if context:
                    data_sources = self._find_data_sources_in_context(context)
                    
                    # Find sources that match the entity
                    if requirements["entity_type"] == "folha" and entity in data_sources["folha"]:
                        requirements["data_source"] = f"Dados.folha.v2.{entity}"
                    elif requirements["entity_type"] == "pessoal" and entity in data_sources["pessoal"]:
                        requirements["data_source"] = f"Dados.pessoal.v2.{entity}"
                    elif entity in data_sources["folha"]:
                        requirements["data_source"] = f"Dados.folha.v2.{entity}"
                        requirements["entity_type"] = "folha"
                    elif entity in data_sources["pessoal"]:
                        requirements["data_source"] = f"Dados.pessoal.v2.{entity}"
                        requirements["entity_type"] = "pessoal"
                break
        
        # Extract field names mentioned in the query
        field_names = []
        
        # If "campos" is in the query, it's likely referring to specific fields
        if "campos" in query_lower or "campo" in query_lower:
            # Clear default fields to only use explicitly mentioned ones
            requirements["fields"] = []
            for field in field_names:
                if field in query_lower:
                    requirements["fields"].append(field)
        
        # Extract filter information
        filter_keywords = ["filtro", "filtros", "expression", "expressions", "expressao", "condicao", "condição", "criterio", "critério"]
        if any(keyword in query_lower for keyword in filter_keywords):
            filter_info = {}
            
            # Look for operators
            operators = ["=", ">", "<", ">=", "<=", "!=", "contem", "contém", "inicio", "início", "fim", "maior", "menor", "igual", "diferente"]
            for operator in operators:
                if operator in query_lower:
                    filter_info["operator"] = operator
                    break
                
            # Look for filter fields
            for field in field_names:
                if field in query_lower and any(kw in query_lower.split(field)[0][-15:] for kw in filter_keywords):
                    filter_info["field"] = field
                    break
                
            if filter_info:
                requirements["filters"].append(filter_info)
                
            # Add a general operation for filtering
            requirements["specific_operations"].append("filtro")
        
        # Extract ordering information
        order_keywords = ["ordenar", "ordenacao", "ordenação", "sort", "order"]
        if any(keyword in query_lower for keyword in order_keywords):
            # Common ordering directions
            directions = ["asc", "desc", "crescente", "decrescente"]
            for direction in directions:
                if direction in query_lower:
                    requirements["ordering"] = direction
                    break
            
            # Add a general operation for ordering
            requirements["specific_operations"].append("ordenacao")
        
        # Detect specific operations being requested
        operation_keywords = {
            "busca": ["busca", "buscar", "consulta", "consultar", "query"],
            "percorrer": ["percorrer", "iterar", "loop", "para cada"],
            "imprimir": ["imprimir", "mostrar", "exibir", "imprime", "print"],
            "mapear": ["mapear", "transformar", "converter"],
            "filtrar": ["filtrar", "filter", "onde", "where"],
            "agrupar": ["agrupar", "agrupar por", "group by", "group"]
        }
        
        for operation, keywords in operation_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if operation not in requirements["specific_operations"]:
                    requirements["specific_operations"].append(operation)
        
        logger.info(f"Extracted function requirements: {requirements}")
        return requirements
    
    def _log_context_details(self, query: str, context: str, function_requirements: Dict[str, Any], syntax_patterns: str, history_context: str) -> None:
        """
        Log detailed information about the context being used for response generation.
        
        Args:
            query: User query
            context: Documentation context
            function_requirements: Extracted function requirements
            syntax_patterns: Extracted syntax patterns
            history_context: Conversation history context
        """
        logger.info("----- CONTEXT DETAILS FOR RESPONSE GENERATION -----")
        logger.info(f"Query: {query}")
        logger.info(f"Context Length: {len(context)} characters")
        logger.info(f"Context Token Count: {self.count_tokens(context)} tokens")
        
        # Log function requirements
        logger.info("Function Requirements:")
        for key, value in function_requirements.items():
            if value:  # Only log non-empty values
                logger.info(f"  {key}: {value}")
        
        # Log syntax patterns
        if syntax_patterns:
            logger.info(f"Syntax Patterns Length: {len(syntax_patterns)} characters")
            logger.info(f"Syntax Patterns Token Count: {self.count_tokens(syntax_patterns)} tokens")
        
        # Log history context
        if history_context:
            logger.info(f"History Context Length: {len(history_context)} characters")
            logger.info(f"History Context Token Count: {self.count_tokens(history_context)} tokens")
        
        # Log complete context
        #logger.info("Complete Context:")
        #logger.info(context)
        
        logger.info("------------------------------------------------")

    def _preprocess_context(self, context: str, query: str, function_requirements: Dict[str, Any]) -> str:
        """
        Pré-processa o contexto para eliminar redundâncias e organizar as informações
        de forma mais estruturada antes de enviá-las ao modelo.
        
        Args:
            context: Contexto original
            query: Consulta do usuário
            function_requirements: Requisitos extraídos da consulta
            
        Returns:
            Contexto processado
        """
        # Se o contexto estiver vazio, retornar
        if not context.strip():
            return context
            
        # Separar o contexto em blocos
        blocks = context.split('#')
        processed_blocks = []
        
        # Coletar hashes de blocos para identificar duplicatas
        block_hashes = set()
        
        # Termos relevantes da consulta para classificação
        query_terms = query.lower().split()
        
        # Identificar a fonte específica mencionada na consulta
        source_mentioned = None
        if "fonte" in query.lower():
            for term in query_terms:
                if "fonte" in term:
                    source_mentioned = term
                    break
        
        # Processar cada bloco
        for block in blocks:
            # Ignorar blocos vazios
            if not block.strip():
                continue
                
            # Adicionar o # de volta
            block = '#' + block
            
            # Calcular um hash simplificado do bloco (primeiro parágrafo)
            first_paragraph = block.split('\n\n')[0] if '\n\n' in block else block
            block_hash = hash(first_paragraph[:100])
            
            # Se o bloco já foi processado, pular
            if block_hash in block_hashes:
                continue
                
            block_hashes.add(block_hash)
            
            # Calcular relevância do bloco para a consulta
            relevance_score = 0
            block_lower = block.lower()
            
            # Verificar se contém a fonte mencionada na consulta
            if source_mentioned and source_mentioned in block_lower:
                relevance_score += 20  # Máxima prioridade para a fonte mencionada
                
                # Se o bloco contém a fonte mencionada, dar prioridade máxima para:
                # 1. Seção de campos (Types)
                if "Types:" in block:
                    relevance_score += 30  # Prioridade máxima para campos da fonte
                    
                # 2. Seção de filtros/ordenações (Expressions)
                if "Expressions:" in block:
                    relevance_score += 30  # Prioridade máxima para filtros/ordenações
                    
            # Verificar se contém dados da fonte mencionada na consulta
            for term in query_terms:
                if term in block_lower:
                    relevance_score += 1
                    
            # Dar prioridade a blocos que mencionam "busca" se a consulta menciona busca
            if "busca" in query.lower() and "busca" in block_lower:
                relevance_score += 3
                
            # Dar prioridade a blocos com código de exemplo se a consulta é sobre implementação
            if any(term in query.lower() for term in ["implement", "criar", "código", "exemplo"]):
                if "```" in block or "Code Example:" in block:
                    relevance_score += 3
            
            # Armazenar o bloco com sua pontuação de relevância
            processed_blocks.append((block, relevance_score))
        
        # Ordenar blocos por relevância
        processed_blocks.sort(key=lambda x: x[1], reverse=True)
        
        # Reunir blocos processados e ordenados
        context_processed = "\n\n".join([block for block, _ in processed_blocks])
        
        # Registrar o pré-processamento no log
        log_debug(logger, f"Contexto processado: reduziu de {len(blocks)} para {len(processed_blocks)} blocos")
        
        return context_processed

    def _validate_report_structure(self, response: str) -> bool:
        """
        Validate if the response follows the report structure defined in REPORT_GENERATION_PROMPT.
        
        Args:
            response: Generated response
            
        Returns:
            True if response follows the structure, False otherwise
        """
        required_elements = [
            "esquema = [",
            "fonte = Dados.dinamico.v2.novo(esquema)",
            "parametros.",
            "fonteDados = Dados.",
            "filtro =",
            "dados = fonteDados.busca",
            "percorrer (dados)",
            "fonte.inserirLinha",
            "retornar fonte"
        ]
        
        return all(element in response for element in required_elements)

    def generate_response(self, query: str, context: str | List[str] | List[Dict], history: Optional[List[Tuple[str, str]]] = None) -> str:
        """
        Generate a response using the provided context and history.
        
        Args:
            query: User query
            context: Documentation context
            history: Conversation history
            
        Returns:
            Generated response
        """
        try:
            # Convert context to string if it's a list
            if isinstance(context, list):
                if context and isinstance(context[0], dict):
                    context = "\n\n".join(str(item.get('content', '')) for item in context)
                else:
                    context = "\n\n".join(str(item) for item in context)
            
            # Extract function requirements from query
            function_requirements = self.extract_function_requirements(query, context)
            
            # Check if this is a report-related query
            is_report_query = any(word in query.lower() for word in ["relatório", "relatorios", "relatorio"])
            
            # Preprocess context
            processed_context = self._preprocess_context(context, query, function_requirements)
            
            # Extract syntax patterns
            syntax_patterns = self.extract_syntax_patterns(processed_context)
            
            # Format history
            history_context = self.format_history(history or [])
            
            # Log context details
            log_context_details(query, processed_context, function_requirements, syntax_patterns, history_context)
            
            # Log token usage
            self.token_logger.log_token_usage(
                max_context_tokens=self.max_context_tokens,
                max_syntax_patterns_tokens=self.max_syntax_patterns_tokens,
                max_history_tokens=self.max_history_tokens,
                actual_context_tokens=self.count_tokens(processed_context),
                actual_syntax_patterns_tokens=self.count_tokens(syntax_patterns),
                actual_history_tokens=self.count_tokens(history_context),
                query=query
            )
            
            # Choose the appropriate system prompt based on query type
            system_prompt = self.prompts.get("REPORT_GENERATION_PROMPT", "") if is_report_query else self.system_prompt
            
            # Format the prompt with the context
            user_prompt = self.prompts.get("RAG_USER_PROMPT", "").format(
                query=query,
                context=processed_context,
                syntax_patterns=syntax_patterns,
                history_context=history_context
            )
            
            # Generate response using OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            
            response_content = response.choices[0].message.content
            
            # If this is a report query, validate the structure
            if is_report_query and not self._validate_report_structure(response_content):
                logger.warning("Generated response does not follow report structure. Regenerating with stronger guidance...")
                
                # Add explicit instruction to follow the structure
                enhanced_prompt = f"{user_prompt}\n\nIMPORTANTE: Siga EXATAMENTE a estrutura de relatório definida no prompt do sistema, incluindo a definição do esquema, criação da fonte dinâmica, parâmetros, busca e processamento dos dados."
                
                # Regenerate response with enhanced prompt
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    temperature=0.4  # Lower temperature for more consistent structure
                )
                response_content = response.choices[0].message.content
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente."