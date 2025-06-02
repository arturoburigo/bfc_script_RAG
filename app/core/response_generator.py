# app/core/response_generator.py
import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Optional, Tuple
import logging
from .config import setup_logging #, is_dev_mode, log_debug, log_function_call, log_function_return
import tiktoken
# import re # Not used directly in this snippet after changes
# from app.utils.token_logger import TokenLogger # Assuming not core to this change
# from ..utils.logging_utils import log_context_details # Assuming not core to this change
from dataclasses import dataclass, field # field is used in ContextChunk
from collections import defaultdict

# Configure logging
logger = setup_logging(__name__, "logs/response_generator.log")

@dataclass
class ContextChunk:
    content: str
    relevance_score: float
    context_type: str # e.g., "code_example", "field_definition", "general_documentation"
    collection: str
    metadata: Dict[str, Any]
    tokens: int = 0
    efficiency: float = 0.0 # Added for optimizer step, if used explicitly

class ContextOptimizer:
    """Optimizes context to maximize relevance within token limits."""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.max_context_tokens = 8000  # Target for GPT-3.5-turbo context
        self.min_context_diversity = 0.3 # Not actively used in current logic, conceptual
        self.max_chunks = 5  # Max number of context chunks to include
        
    def optimize_context(self, context_chunks: List[ContextChunk], 
                        query_analysis: Dict[str, Any]) -> str:
        """Optimizes selection of context based on relevance, diversity, and token limits."""
        if not context_chunks:
            return ""
        
        for chunk in context_chunks:
            chunk.tokens = len(self.tokenizer.encode(chunk.content))
        
        # Strategy 1: Greedy selection by relevance/token ratio (efficiency)
        selected_chunks = self._greedy_selection(context_chunks, query_analysis)
        
        # Strategy 2: Ensure diversity if multiple types of information are relevant
        final_chunks = self._ensure_diversity(selected_chunks, query_analysis)
        
        return self._build_context_string(final_chunks, query_analysis)
    
    def _greedy_selection(self, chunks: List[ContextChunk], 
                         query_analysis: Dict[str, Any]) -> List[ContextChunk]:
        """Greedy selection based on efficiency score (relevance per token), boosted by query relevance."""
        for chunk in chunks:
            if chunk.tokens > 0:
                base_efficiency = chunk.relevance_score / (chunk.tokens / 100) # per 100 tokens
                
                # Boost efficiency based on query analysis (example boosts)
                boost = 1.0
                if query_analysis.get("expected_output") == "code" and chunk.context_type == "code_example":
                    boost *= 1.5
                elif "field_query" in query_analysis.get("intents", []) and chunk.context_type == "field_definition":
                    boost *= 1.4
                # Add more boosts as needed
                
                chunk.efficiency = base_efficiency * boost
            else:
                chunk.efficiency = 0
        
        chunks.sort(key=lambda x: x.efficiency, reverse=True)
        
        selected = []
        total_tokens = 0
        for chunk in chunks:
            if len(selected) >= self.max_chunks:
                break
            if total_tokens + chunk.tokens <= self.max_context_tokens:
                selected.append(chunk)
                total_tokens += chunk.tokens
        
        logger.info(f"Greedy selection: {len(selected)} chunks, {total_tokens} tokens")
        return selected
    
    def _ensure_diversity(self, chunks: List[ContextChunk], 
                         query_analysis: Dict[str, Any]) -> List[ContextChunk]:
        """Ensures some diversity if multiple context types are relevant, fitting within token limits."""
        # This is a simplified diversity logic; can be expanded
        if not chunks:
            return chunks

        final_selection = []
        tokens_used = 0
        
        # Determine priority types from query_analysis
        priority_types = self._get_priority_types(query_analysis)
        
        # Add at least one of each priority type if available and fits
        added_types = set()
        temp_chunks_for_priority = sorted(chunks, key=lambda x: x.relevance_score, reverse=True)

        for p_type in priority_types:
            if p_type not in added_types:
                for chunk in temp_chunks_for_priority:
                    if chunk.context_type == p_type and chunk not in final_selection:
                        if tokens_used + chunk.tokens <= self.max_context_tokens and len(final_selection) < self.max_chunks:
                            final_selection.append(chunk)
                            tokens_used += chunk.tokens
                            added_types.add(p_type)
                            break 
        
        # Fill remaining space with highest efficiency chunks not already selected
        remaining_chunks_sorted = sorted([c for c in chunks if c not in final_selection], key=lambda x: x.efficiency, reverse=True)
        
        for chunk in remaining_chunks_sorted:
            if len(final_selection) >= self.max_chunks:
                break
            if tokens_used + chunk.tokens <= self.max_context_tokens:
                final_selection.append(chunk)
                tokens_used += chunk.tokens
        
        logger.info(f"Diversity ensured selection: {len(final_selection)} chunks, {tokens_used} tokens")
        # Re-sort by original relevance or keep as is, depending on strategy
        final_selection.sort(key=lambda x: x.relevance_score, reverse=True)
        return final_selection

    def _get_priority_types(self, query_analysis: Dict[str, Any]) -> List[str]:
        intents = query_analysis.get("intents", [])
        expected_output = query_analysis.get("expected_output", "explanation")
        
        # Define context types you expect from your ChromaDB metadata or content structure
        # Example: "code_example", "data_source_definition", "field_definition", "enum_definition", "general_doc"
        
        if "report_query" in intents or expected_output == "code":
            return ["code_example", "data_source_definition", "general_doc"] # Order matters for preference
        elif "field_query" in intents:
            return ["field_definition", "data_source_definition", "code_example"]
        elif "enum_query" in intents:
            return ["enum_definition", "general_doc"]
        else: # Default for explanations
            return ["general_doc", "code_example", "field_definition"] 

    def _build_source_info(self, chunk: ContextChunk) -> str:
        """Builds a concise source string from chunk metadata."""
        metadata = chunk.metadata
        source_parts = [chunk.collection.title()] # Start with collection name
        
        # Customize based on your actual metadata structure
        if chunk.collection == "docs" and metadata.get("document"):
            source_parts.append(f"Doc: {metadata['document']}")
            if metadata.get("section"): source_parts.append(f"Sec: {metadata['section']}")
        elif chunk.collection in ["folha", "pessoal"] and metadata.get("function_name"):
            source_parts.append(f"Func: {metadata['function_name']}")
        elif chunk.collection == "enums" and metadata.get("enum_name"):
             source_parts.append(f"Enum: {metadata['enum_name']}")
        # Add more specific source info extraction as needed
        
        return " | ".join(source_parts)

    def _build_context_string(self, chunks: List[ContextChunk], 
                             query_analysis: Dict[str, Any]) -> str:
        """Builds the final context string from selected chunks."""
        if not chunks:
            return "Nenhum contexto relevante encontrado."
        
        # Sort chunks by relevance score for final presentation
        chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        context_parts = []
        for chunk in chunks:
            source_info = self._build_source_info(chunk)
            # Include relevance score for transparency, adjust formatting as needed
            context_parts.append(f"Fonte: [{source_info}] (Relevância: {chunk.relevance_score:.2f})\n{chunk.content}\n---")
        
        return "\n".join(context_parts)

class AdvancedPromptEngine:
    """Generates adaptive prompts based on query analysis and context."""
    def __init__(self):
        self.base_prompts = self._load_prompts() # Assumes prompts.py is correctly set up
        
    def _load_prompts(self) -> Dict[str, str]:
        try:
            from app.utils.prompts import (RAG_SYSTEM_PROMPT, RAG_USER_PROMPT, 
                                           SYNTAX_EXTRACTION_PROMPT, REPORT_GENERATION_PROMPT)
            return {
                "RAG_SYSTEM_PROMPT": RAG_SYSTEM_PROMPT,
                "RAG_USER_PROMPT": RAG_USER_PROMPT,
                "SYNTAX_EXTRACTION_PROMPT": SYNTAX_EXTRACTION_PROMPT,
                "REPORT_GENERATION_PROMPT": REPORT_GENERATION_PROMPT
            }
        except ImportError:
            logger.error("Failed to load prompts from app.utils.prompts. Using default fallbacks.")
            return { # Fallback prompts
                "RAG_SYSTEM_PROMPT": "Você é um assistente IA. Use o contexto fornecido para responder à pergunta.",
                "RAG_USER_PROMPT": "Contexto:\n{context}\n\nPergunta: {query}",
                "REPORT_GENERATION_PROMPT": "Você é um assistente IA especializado em gerar relatórios em BFC-Script. Use o contexto para criar o script solicitado."
            }

    def get_optimal_prompt(self, query_analysis: Dict[str, Any], 
                          context_summary: Dict[str, Any]) -> Tuple[str, str]:
        intents = query_analysis.get("intents", [])
        expected_output = query_analysis.get("expected_output", "explanation")
        
        system_prompt_key = "RAG_SYSTEM_PROMPT" # Default
        if "report_query" in intents:
            system_prompt_key = "REPORT_GENERATION_PROMPT"
        elif expected_output == "code" or "code_request" in intents:
            # Could have a specific prompt for code if different from general RAG
             system_prompt_key = "RAG_SYSTEM_PROMPT" # Or a "CODE_GENERATION_PROMPT"

        system_prompt = self.base_prompts.get(system_prompt_key, self.base_prompts["RAG_SYSTEM_PROMPT"])
        
        # Enhance system prompt with context insights
        enhancements = []
        if context_summary.get("has_high_relevance_sources"):
            enhancements.append("Fontes de alta relevância (>0.7) foram identificadas no contexto.")
        if context_summary.get("has_code_examples"):
            enhancements.append("Exemplos de código BFC-Script estão disponíveis no contexto; use-os como base preferencial para respostas de código.")
        if context_summary.get("dominant_collection"):
             enhancements.append(f"A coleção '{context_summary['dominant_collection']}' parece ser a mais relevante.")
        
        if enhancements:
            system_prompt += "\n\nObservações sobre o Contexto:\n- " + "\n- ".join(enhancements)
            
        user_prompt_template = self.base_prompts.get("RAG_USER_PROMPT", "Contexto:\n{context}\n\nPergunta: {query}")
        return system_prompt, user_prompt_template

class ResponseGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base") # Standard tokenizer
        self.context_optimizer = ContextOptimizer(self.tokenizer)
        self.prompt_engine = AdvancedPromptEngine()
        # BasicQueryAnalyzer is removed from here
        logger.info("ResponseGenerator initialized successfully")
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _convert_results_to_chunks(self, results: List[Dict]) -> List[ContextChunk]:
        chunks = []
        for r in results:
            # Determine context_type from metadata if available, otherwise default
            # This needs alignment with how metadata is structured in ChromaDB
            context_type = r.get("metadata", {}).get("type", "general_documentation")
            if r.get("has_code_example"): # Prioritize this if SemanticSearch flagged it
                 context_type = "code_example"

            chunks.append(ContextChunk(
                content=r.get("content", ""),
                relevance_score=r.get("relevance_score", 0.0),
                context_type=context_type,
                collection=r.get("collection", "unknown"),
                metadata=r.get("metadata", {})
            ))
        return chunks

    def _analyze_context_summary(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        summary = {
            "total_chunks": len(chunks),
            "has_high_relevance_sources": False,
            "has_code_examples": False,
            "has_data_sources": False, # Example specific type
            "has_field_definitions": False, # Example specific type
            "dominant_collection": None,
            "avg_relevance": 0.0
        }
        if not chunks: return summary

        relevances = [c.relevance_score for c in chunks if c.relevance_score is not None]
        if relevances:
            summary["avg_relevance"] = sum(relevances) / len(relevances)
            summary["has_high_relevance_sources"] = any(r > 0.7 for r in relevances)

        type_counts = defaultdict(int)
        collection_counts = defaultdict(int)
        for chunk in chunks:
            type_counts[chunk.context_type] += 1
            collection_counts[chunk.collection] += 1
            if chunk.context_type == "code_example": summary["has_code_examples"] = True
            if chunk.context_type == "data_source_definition": summary["has_data_sources"] = True # Match example in optimizer
            if chunk.context_type == "field_definition": summary["has_field_definitions"] = True


        if collection_counts:
            summary["dominant_collection"] = max(collection_counts, key=collection_counts.get)
        
        logger.info(f"Context summary: {summary}")
        return summary
        
    # Signature changed to accept query_analysis
    def generate_response(self, query: str, search_results: List[Dict], 
                         query_analysis: Dict[str, Any], 
                         history: Optional[List[Tuple[str, str]]] = None) -> str:
        try:
            # query_analysis is now passed as an argument, no need to recalculate
            
            context_chunks = self._convert_results_to_chunks(search_results)
            context_summary = self._analyze_context_summary(context_chunks)
            
            optimized_context_str = self.context_optimizer.optimize_context(
                context_chunks, query_analysis
            )
            
            system_prompt, user_prompt_template = self.prompt_engine.get_optimal_prompt(
                query_analysis, context_summary
            )
            
            history_text = self._format_history_efficiently(history)
            
            model = self._select_optimal_model(query_analysis) # Removed context_summary from selection for now
            temperature = self._get_optimal_temperature(query_analysis)
            
            # Construct user prompt content
            user_content = user_prompt_template.format(context=optimized_context_str, query=query)

            messages = [{"role": "system", "content": system_prompt}]
            if history_text:
                # Simple history injection; could be more sophisticated
                messages.append({"role": "user", "content": f"Histórico da conversa anterior:\n{history_text}"})
                messages.append({"role": "assistant", "content": "Entendido. Prosseguindo com a nova pergunta."})


            messages.append({"role": "user", "content": user_content})
            
            logger.debug(f"Sending messages to OpenAI: {json.dumps(messages, indent=2)}")

            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000 
            )
            response_text = completion.choices[0].message.content

            if self._should_retry_generation(response_text, query_analysis, context_summary):
                logger.info("Retrying generation with enhanced guidance.")
                response_text = self._retry_with_enhanced_guidance(
                    messages, query_analysis, model # Pass current messages
                )
            
            # Log details (optional)
            # self._log_generation_details(query, optimized_context_str, query_analysis, context_summary, model, temperature)

            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"❌ Erro ao gerar resposta: {str(e)}"

    def _format_history_efficiently(self, history: Optional[List[Tuple[str, str]]]) -> str:
        if not history: return ""
        # Simplified: take last 2 exchanges, truncate responses
        recent_history = history[-2:] 
        formatted_history = []
        for q, a in recent_history:
            a_truncated = a[:250] + "..." if len(a) > 250 else a
            formatted_history.append(f"Usuário: {q}\nAssistente: {a_truncated}")
        return "\n---\n".join(formatted_history)

    def _select_optimal_model(self, query_analysis: Dict[str, Any]) -> str:
        # Simpler model selection logic for now
        if query_analysis.get("complexity") == "complex" or query_analysis.get("expected_output") == "code":
             # Consider GPT-4 variants for complex tasks or critical code generation
             # return "gpt-4-turbo-preview" # Example, ensure model availability
             pass # Fall through to default for now
        return "gpt-3.5-turbo" # Default

    def _get_optimal_temperature(self, query_analysis: Dict[str, Any]) -> float:
        if query_analysis.get("expected_output") == "code":
            return 0.1 
        elif query_analysis.get("expected_output") == "structured_list":
            return 0.2
        return 0.3 # Default for explanations

    def _should_retry_generation(self, response: str, query_analysis: Dict[str, Any], context_summary: Dict[str, Any]) -> bool:
        # Basic retry conditions
        if query_analysis.get("expected_output") == "code" and "```" not in response:
            logger.warning("Code output expected but not found in standard format.")
            return True
        
        # If context had high relevance but response is very short or generic
        if context_summary.get("has_high_relevance_sources", False) and len(response) < 50 and \
           any(phrase in response.lower() for phrase in ["não sei", "não encontrei", "sem informação"]):
            logger.warning("High relevance context but generic/short response.")
            return True
            
        return False

    def _retry_with_enhanced_guidance(self, original_messages: List[Dict], 
                                     query_analysis: Dict[str, Any], model: str) -> str:
        """Retry generation with an enhanced instruction in the user prompt."""
        
        # Copy messages to avoid modifying the original list if retry also fails
        retry_messages = [msg.copy() for msg in original_messages]

        enhancement_instruction = "\n\nINSTRUÇÃO ADICIONAL: Por favor, revise sua resposta anterior. "
        if query_analysis.get("expected_output") == "code":
            enhancement_instruction += "É crucial que a resposta inclua um bloco de código BFC-Script formatado corretamente (```bfc-script ... ```). Adapte os exemplos do contexto se necessário."
        elif query_analysis.get("expected_output") == "structured_list":
            enhancement_instruction += "A resposta deve ser uma lista bem estruturada e completa, utilizando todos os elementos relevantes do contexto."
        else:
            enhancement_instruction += "Tente fornecer uma resposta mais detalhada e diretamente baseada no contexto fornecido."

        # Add enhancement to the last user message content
        if retry_messages and retry_messages[-1]["role"] == "user":
            retry_messages[-1]["content"] += enhancement_instruction
        else: # Fallback: add as a new user message (less ideal)
            retry_messages.append({"role": "user", "content": enhancement_instruction + " Pergunta Original: " + query_analysis.get("original_query", "")})

        logger.debug(f"Retry messages: {json.dumps(retry_messages, indent=2)}")
        try:
            completion = self.client.chat.completions.create(
                model=model, # Use same model or a slightly different one for retry
                messages=retry_messages,
                temperature=0.05,  # Lower temperature for more deterministic retry
                max_tokens=2500 # Allow slightly more tokens for retry
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error during retry generation: {str(e)}", exc_info=True)
            return "Desculpe, mesmo após uma tentativa adicional, não foi possível gerar uma resposta adequada."