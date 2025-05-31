# response_generator.py - Versão Otimizada
import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return
import tiktoken
import re
from app.utils.token_logger import TokenLogger
from ..utils.logging_utils import log_context_details
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logger = setup_logging(__name__, "logs/response_generator.log")

@dataclass
class ContextChunk:
    content: str
    relevance_score: float
    context_type: str
    collection: str
    metadata: Dict[str, Any]
    tokens: int = 0

class ContextOptimizer:
    """Otimiza o contexto para maximizar relevância dentro dos limites de token"""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.max_context_tokens = 8000  # Reduzido para GPT-3.5-turbo
        self.min_context_diversity = 0.3  # Mínimo de diversidade de contexto
        self.max_chunks = 5  # Limite máximo de chunks
        
    def optimize_context(self, context_chunks: List[ContextChunk], 
                        query_analysis: Dict[str, Any]) -> str:
        """
        Otimiza seleção de contexto baseado em relevância, diversidade e tokens
        """
        if not context_chunks:
            return ""
        
        # Calculate tokens for each chunk
        for chunk in context_chunks:
            chunk.tokens = len(self.tokenizer.encode(chunk.content))
        
        # Strategy 1: Greedy selection by relevance/token ratio
        selected_chunks = self._greedy_selection(context_chunks, query_analysis)
        
        # Strategy 2: Ensure diversity
        final_chunks = self._ensure_diversity(selected_chunks, query_analysis)
        
        # Build final context
        return self._build_context_string(final_chunks, query_analysis)
    
    def _greedy_selection(self, chunks: List[ContextChunk], 
                         query_analysis: Dict[str, Any]) -> List[ContextChunk]:
        """Seleção greedy baseada em score/token ratio"""
        
        # Calculate efficiency score (relevance per token)
        for chunk in chunks:
            if chunk.tokens > 0:
                # Base efficiency
                efficiency = chunk.relevance_score / (chunk.tokens / 100)  # per 100 tokens
                
                # Boost efficiency for query-relevant types
                if query_analysis.get("expected_output") == "code" and chunk.context_type == "code_example":
                    efficiency *= 1.5
                elif "field_query" in query_analysis.get("intents", []) and chunk.context_type == "field_definition":
                    efficiency *= 1.4
                elif "enum_query" in query_analysis.get("intents", []) and chunk.context_type == "enum_definition":
                    efficiency *= 1.4
                
                chunk.efficiency = efficiency
            else:
                chunk.efficiency = 0
        
        # Sort by efficiency
        chunks.sort(key=lambda x: x.efficiency, reverse=True)
        
        # Greedy selection
        selected = []
        total_tokens = 0
        
        for chunk in chunks:
            if len(selected) >= self.max_chunks:
                break
                
            if total_tokens + chunk.tokens <= self.max_context_tokens:
                selected.append(chunk)
                total_tokens += chunk.tokens
            else:
                # Try to fit a smaller high-value chunk
                if chunk.efficiency > 1.0 and chunk.tokens < 500:
                    # Truncate if necessary
                    if total_tokens + 500 <= self.max_context_tokens:
                        chunk.content = chunk.content[:1000] + "..."
                        chunk.tokens = 500
                        selected.append(chunk)
                        total_tokens += chunk.tokens
        
        logger.info(f"Greedy selection: {len(selected)} chunks, {total_tokens} tokens")
        return selected
    
    def _ensure_diversity(self, chunks: List[ContextChunk], 
                         query_analysis: Dict[str, Any]) -> List[ContextChunk]:
        """Garante diversidade mínima de tipos de contexto"""
        
        # Group by type
        by_type = defaultdict(list)
        for chunk in chunks:
            by_type[chunk.context_type].append(chunk)
        
        # Ensure minimum representation of each relevant type
        final_chunks = []
        used_tokens = 0
        
        # Priority types based on query
        priority_types = self._get_priority_types(query_analysis)
        
        # Ensure at least one chunk from each priority type
        for context_type in priority_types:
            if context_type in by_type and by_type[context_type]:
                best_chunk = max(by_type[context_type], key=lambda x: x.relevance_score)
                if used_tokens + best_chunk.tokens <= self.max_context_tokens:
                    final_chunks.append(best_chunk)
                    used_tokens += best_chunk.tokens
                    by_type[context_type].remove(best_chunk)
        
        # Add remaining chunks by efficiency
        remaining_chunks = []
        for chunks_list in by_type.values():
            remaining_chunks.extend(chunks_list)
        
        remaining_chunks.sort(key=lambda x: x.efficiency, reverse=True)
        
        for chunk in remaining_chunks:
            if len(final_chunks) >= self.max_chunks:
                break
                
            if used_tokens + chunk.tokens <= self.max_context_tokens:
                final_chunks.append(chunk)
                used_tokens += chunk.tokens
        
        logger.info(f"Final selection: {len(final_chunks)} chunks, {used_tokens} tokens")
        return final_chunks
    
    def _get_priority_types(self, query_analysis: Dict[str, Any]) -> List[str]:
        """Determina tipos de contexto prioritários baseado na análise da query"""
        
        intents = query_analysis.get("intents", [])
        
        if "code_request" in intents:
            return ["code_example", "data_source", "field_definition"]
        elif "field_query" in intents:
            return ["field_definition", "data_source", "code_example"]
        elif "enum_query" in intents:
            return ["enum_definition", "data_source"]
        elif "report_query" in intents:
            return ["code_example", "data_source", "field_definition"]
        else:
            return ["data_source", "general_documentation", "code_example"]
    
    def _build_context_string(self, chunks: List[ContextChunk], 
                             query_analysis: Dict[str, Any]) -> str:
        """Constrói string de contexto otimizada"""
        
        if not chunks:
            return ""
        
        # Group by type for organized presentation
        by_type = defaultdict(list)
        for chunk in chunks:
            by_type[chunk.context_type].append(chunk)
        
        # Sort within each type by relevance
        for context_type in by_type:
            by_type[context_type].sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Build context with clear sections
        context_parts = []
        
        # Get priority order
        priority_types = self._get_priority_types(query_analysis)
        
        # Add priority types first
        for context_type in priority_types:
            if context_type in by_type:
                for chunk in by_type[context_type]:
                    # Build source info
                    source_info = self._build_source_info(chunk)
                    context_parts.append(f"[{source_info}] (Score: {chunk.relevance_score:.3f})")
                    context_parts.append(chunk.content)
                    context_parts.append("")  # Empty line for separation
                
                del by_type[context_type]
        
        # Add remaining types
        for chunks_list in by_type.values():
            for chunk in chunks_list:
                source_info = self._build_source_info(chunk)
                context_parts.append(f"[{source_info}] (Score: {chunk.relevance_score:.3f})")
                context_parts.append(chunk.content)
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_source_info(self, chunk: ContextChunk) -> str:
        """Constrói informação de fonte para o chunk"""
        metadata = chunk.metadata
        source_parts = [chunk.collection.title()]
        
        if chunk.collection == "docs":
            if metadata.get("document"):
                source_parts.append(f"Doc: {metadata['document']}")
            if metadata.get("section"):
                source_parts.append(f"Seção: {metadata['section']}")
        elif chunk.collection in ["folha", "pessoal"]:
            if metadata.get("function_name"):
                source_parts.append(f"Função: {metadata['function_name']}")
        elif chunk.collection == "enums":
            if metadata.get("enum_name"):
                source_parts.append(f"Enum: {metadata['enum_name']}")
        
        return " | ".join(source_parts)

class AdvancedPromptEngine:
    """Engine avançado para geração de prompts contextuais"""
    
    def __init__(self):
        self.base_prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompts from prompts.py"""
        try:
            from app.utils.prompts import (
                RAG_SYSTEM_PROMPT,
                RAG_USER_PROMPT,
                SYNTAX_EXTRACTION_PROMPT,
                REPORT_GENERATION_PROMPT
            )
            
            return {
                "RAG_SYSTEM_PROMPT": RAG_SYSTEM_PROMPT,
                "RAG_USER_PROMPT": RAG_USER_PROMPT,
                "SYNTAX_EXTRACTION_PROMPT": SYNTAX_EXTRACTION_PROMPT,
                "REPORT_GENERATION_PROMPT": REPORT_GENERATION_PROMPT
            }
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            return {}
    
    def get_optimal_prompt(self, query_analysis: Dict[str, Any], 
                          context_summary: Dict[str, Any]) -> Tuple[str, str]:
        """
        Seleciona prompt ótimo baseado na análise da query e contexto
        """
        intents = query_analysis.get("intents", [])
        expected_output = query_analysis.get("expected_output", "explanation")
        
        # Select system prompt
        if "report_query" in intents:
            system_prompt = self.base_prompts.get("REPORT_GENERATION_PROMPT", "")
        elif expected_output == "code" or "code_request" in intents:
            system_prompt = self.base_prompts.get("RAG_SYSTEM_PROMPT", "")
        elif expected_output == "structured_list" or "field_query" in intents:
            system_prompt = self.base_prompts.get("RAG_SYSTEM_PROMPT", "")
        else:
            system_prompt = self.base_prompts.get("RAG_SYSTEM_PROMPT", "")
        
        # Enhance system prompt with context insights
        if context_summary.get("has_high_relevance_sources"):
            system_prompt += "\n\nCONTEXTO DISPONÍVEL: Fontes de alta relevância identificadas. Priorize informações com score > 0.7"
        
        if context_summary.get("has_code_examples"):
            system_prompt += "\n\nEXEMPLOS DE CÓDIGO: Exemplos práticos disponíveis no contexto. Use como base para implementações."
        
        # Select user prompt template
        user_prompt_template = self.base_prompts.get("RAG_USER_PROMPT", "")
        
        return system_prompt, user_prompt_template

class ResponseGenerator:
    """Gerador de respostas otimizado com análise de contexto e prompts adaptativos"""
    
    def __init__(self, api_key=None):
        """Initialize the response generator with OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.context_optimizer = ContextOptimizer(self.tokenizer)
        self.prompt_engine = AdvancedPromptEngine()
        self._init_query_analyzer()
        
        logger.info("ResponseGenerator initialized successfully")
    
    def _init_query_analyzer(self):
        """Initialize basic query analyzer"""
        class BasicQueryAnalyzer:
            def analyze_query(self, query: str) -> Dict[str, Any]:
                query_lower = query.lower()
                
                analysis = {
                    "intents": [],
                    "expected_output": "explanation",
                    "complexity": "simple"
                }
                
                # Detect intents
                if any(term in query_lower for term in ["código", "script", "implementa", "criar", "exemplo"]):
                    analysis["intents"].append("code_request")
                    analysis["expected_output"] = "code"
                
                if any(term in query_lower for term in ["campos", "types", "propriedades"]):
                    analysis["intents"].append("field_query")
                    analysis["expected_output"] = "structured_list"
                
                if any(term in query_lower for term in ["enum", "classificação", "tipos de"]):
                    analysis["intents"].append("enum_query")
                    analysis["expected_output"] = "structured_list"
                
                if any(term in query_lower for term in ["relatório", "report"]):
                    analysis["intents"].append("report_query")
                    analysis["expected_output"] = "code"
                
                if any(term in query_lower for term in ["fonte", "dados."]):
                    analysis["intents"].append("data_source_query")
                
                return analysis
        
        self.query_analyzer = BasicQueryAnalyzer()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    def _convert_results_to_chunks(self, results: List[Dict]) -> List[ContextChunk]:
        """Convert search results to context chunks"""
        chunks = []
        
        for result in results:
            chunk = ContextChunk(
                content=result.get("content", ""),
                relevance_score=result.get("relevance_score", 0.0),
                context_type=result.get("context_type", "general_documentation"),
                collection=result.get("collection", "unknown"),
                metadata=result.get("metadata", {}),
                tokens=0  # Will be calculated by optimizer
            )
            chunks.append(chunk)
        
        return chunks
    
    def _analyze_context_summary(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        """Analyze context to provide summary insights"""
        summary = {
            "total_chunks": len(chunks),
            "has_high_relevance_sources": False,
            "has_code_examples": False,
            "has_data_sources": False,
            "has_field_definitions": False,
            "dominant_collection": None,
            "avg_relevance": 0.0
        }
        
        if not chunks:
            return summary
        
        # Calculate statistics
        relevances = [chunk.relevance_score for chunk in chunks]
        summary["avg_relevance"] = sum(relevances) / len(relevances)
        summary["has_high_relevance_sources"] = any(r > 0.7 for r in relevances)
        
        # Analyze content types
        type_counts = defaultdict(int)
        collection_counts = defaultdict(int)
        
        for chunk in chunks:
            type_counts[chunk.context_type] += 1
            collection_counts[chunk.collection] += 1
            
            if chunk.context_type == "code_example":
                summary["has_code_examples"] = True
            elif chunk.context_type == "data_source":
                summary["has_data_sources"] = True
            elif chunk.context_type == "field_definition":
                summary["has_field_definitions"] = True
        
        # Find dominant collection
        if collection_counts:
            summary["dominant_collection"] = max(collection_counts.items(), key=lambda x: x[1])[0]
        
        return summary
    
    def generate_response(self, query: str, search_results: List[Dict], 
                         history: Optional[List[Tuple[str, str]]] = None) -> str:
        """Generate a response using the optimized pipeline."""
        try:
            # Analyze query
            query_analysis = self.query_analyzer.analyze_query(query)
            
            # Convert results to chunks
            context_chunks = self._convert_results_to_chunks(search_results)
            
            # Analyze context
            context_summary = self._analyze_context_summary(context_chunks)
            
            # Optimize context
            optimized_context = self.context_optimizer.optimize_context(
                context_chunks, query_analysis
            )
            
            # Get optimal prompt
            system_prompt, user_prompt = self.prompt_engine.get_optimal_prompt(
                query_analysis, context_summary
            )
            
            # Format history efficiently
            history_text = self._format_history_efficiently(history)
            
            # Select optimal model
            model = self._select_optimal_model(query_analysis, context_summary)
            
            # Get optimal temperature
            temperature = self._get_optimal_temperature(query_analysis)
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add history if available
            if history_text:
                messages.append({"role": "user", "content": f"Histórico da conversa:\n{history_text}"})
            
            # Add current query and context
            messages.append({
                "role": "user", 
                "content": f"Contexto:\n{optimized_context}\n\nPergunta: {query}"
            })
            
            # Generate response
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            ).choices[0].message.content
            
            # Check if retry is needed
            if self._should_retry_generation(response, query_analysis):
                response = self._retry_with_enhanced_guidance(
                    system_prompt, messages, query_analysis, model
                )
            
            # Log generation details
            self._log_generation_details(
                query, optimized_context, query_analysis, context_summary
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"❌ Erro ao gerar resposta: {str(e)}"
    
    def _format_history_efficiently(self, history: Optional[List[Tuple[str, str]]]) -> str:
        """Format conversation history efficiently"""
        if not history:
            return ""
        
        # Take only recent relevant history
        recent_history = history[-3:] if len(history) > 3 else history
        
        history_parts = []
        for i, (q, a) in enumerate(recent_history):
            # Truncate long responses in history
            truncated_response = a[:300] + "..." if len(a) > 300 else a
            history_parts.append(f"[{i+1}] Q: {q}")
            history_parts.append(f"    A: {truncated_response}")
        
        history_text = "\n".join(history_parts)
        
        # Ensure history doesn't exceed token limit
        max_history_tokens = 1000
        if self.count_tokens(history_text) > max_history_tokens:
            # Keep only the most recent exchange
            if recent_history:
                last_q, last_a = recent_history[-1]
                last_a_truncated = last_a[:200] + "..." if len(last_a) > 200 else last_a
                history_text = f"[Última] Q: {last_q}\n         A: {last_a_truncated}"
        
        return history_text
    
    def _select_optimal_model(self, query_analysis: Dict[str, Any], 
                            context_summary: Dict[str, Any]) -> str:
        """Select optimal model based on query and context analysis"""
        
        # Use gpt-3.5-turbo for most cases (faster and more cost-effective)
        if query_analysis.get("complexity") == "simple":
            return "gpt-3.5-turbo"
        
        # Use gpt-4 for complex tasks
        if query_analysis.get("complexity") == "complex":
            return "gpt-4"
        
        return "gpt-3.5-turbo"  # Default choice
    
    def _get_optimal_temperature(self, query_analysis: Dict[str, Any]) -> float:
        """Get optimal temperature based on query type"""
        
        if query_analysis.get("expected_output") == "code":
            return 0.1  # Low temperature for code generation
        elif query_analysis.get("expected_output") == "structured_list":
            return 0.2  # Low temperature for structured outputs
        else:
            return 0.3  # Slightly higher for explanations
    
    def _should_retry_generation(self, response: str, query_analysis: Dict[str, Any]) -> bool:
        """Determine if response should be regenerated"""
        
        # Check for code generation requirements
        if query_analysis.get("expected_output") == "code":
            if "```" not in response and any(term in query_analysis.get("intents", []) 
                                           for term in ["code_request", "report_query"]):
                return True
        
        # Check for very short responses to complex queries
        if query_analysis.get("complexity") == "complex" and len(response) < 100:
            return True
        
        # Check for generic error responses
        if any(phrase in response.lower() for phrase in [
            "não tenho informação suficiente",
            "não foi possível encontrar",
            "contexto não contém"
        ]) and len(response) < 200:
            return True
        
        return False
    
    def _retry_with_enhanced_guidance(self, system_prompt: str, messages: List[Dict],
                                    query_analysis: Dict[str, Any], model: str) -> str:
        """Retry generation with enhanced guidance"""
        
        enhanced_instruction = ""
        
        if query_analysis.get("expected_output") == "code":
            enhanced_instruction = "\n\nIMPORTANTE: Forneça uma resposta com código BFC-Script funcional em blocos ```bfc-script, mesmo que precise adaptar exemplos disponíveis."
        elif query_analysis.get("expected_output") == "structured_list":
            enhanced_instruction = "\n\nIMPORTANTE: Organize a resposta em lista estruturada e completa, usando TODOS os elementos encontrados no contexto."
        
        # Add enhanced instruction to the last message
        messages[-1]["content"] += enhanced_instruction
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,  # Lower temperature for retry
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in retry generation: {e}")
            return "Desculpe, não foi possível gerar uma resposta adequada com as informações disponíveis."
    
    def _log_generation_details(self, query: str, context: str, 
                              query_analysis: Dict[str, Any],
                              context_summary: Dict[str, Any]):
        """Log detailed information about response generation"""
        
        context_tokens = self.count_tokens(context)
        
        logger.info("=" * 60)
        logger.info("RESPONSE GENERATION DETAILS")
        logger.info("=" * 60)
        logger.info(f"Query: {query}")
        logger.info(f"Query Analysis: {query_analysis}")
        logger.info(f"Context Summary: {context_summary}")
        logger.info(f"Context Tokens: {context_tokens}")
        logger.info(f"Context Length: {len(context)} chars")
        
        # Log context quality metrics
        if context_summary.get("has_high_relevance_sources"):
            logger.info("✓ High relevance sources available")
        if context_summary.get("has_code_examples"):
            logger.info("✓ Code examples available")
        if context_summary.get("has_data_sources"):
            logger.info("✓ Data source documentation available")
        
        logger.info("=" * 60)