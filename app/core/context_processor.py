# app/core/context_processor.py - Processador genérico de contexto
import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class ContextProcessor:
    """Processador genérico que converte qualquer formato de contexto em string limpa"""
    
    @staticmethod
    def process_context(context: Union[str, List, Dict, Any]) -> str:
        """
        Converte qualquer formato de contexto em string processável pelo modelo
        
        Args:
            context: Contexto em qualquer formato (string, list, dict, etc.)
            
        Returns:
            String limpa e estruturada do contexto
        """
        try:
            if context is None:
                return ""
            
            # Se já é string, retorna diretamente
            if isinstance(context, str):
                return context.strip()
            
            # Se é lista de dicionários (formato comum do search results)
            if isinstance(context, list):
                context_parts = []
                
                for i, item in enumerate(context):
                    if isinstance(item, dict):
                        # Extrai conteúdo do dicionário
                        content = ContextProcessor._extract_content_from_dict(item, i+1)
                        if content:
                            context_parts.append(content)
                    else:
                        # Converte item para string
                        str_content = str(item).strip()
                        if str_content:
                            context_parts.append(f"[Documento {i+1}]\n{str_content}")
                
                return "\n\n".join(context_parts)
            
            # Se é dicionário único
            if isinstance(context, dict):
                return ContextProcessor._extract_content_from_dict(context, 1)
            
            # Fallback: converter para string
            return str(context).strip()
            
        except Exception as e:
            logger.error(f"Error processing context: {e}")
            # Fallback seguro
            return str(context) if context else ""
    
    @staticmethod
    def _extract_content_from_dict(item: Dict[str, Any], index: int) -> str:
        """
        Extrai conteúdo estruturado de um dicionário
        
        Args:
            item: Dicionário com dados do contexto
            index: Índice do item para organização
            
        Returns:
            String formatada do conteúdo
        """
        try:
            parts = [f"[Documento {index}]"]
            
            # Prioridade para campo 'content'
            if 'content' in item and item['content']:
                parts.append(str(item['content']))
            
            # Se não tem 'content', tenta outros campos comuns
            elif 'text' in item and item['text']:
                parts.append(str(item['text']))
            
            elif 'document' in item and item['document']:
                parts.append(str(item['document']))
            
            else:
                # Tenta extrair qualquer conteúdo textual significativo
                content_fields = []
                for key, value in item.items():
                    if isinstance(value, str) and len(value) > 20:  # Apenas conteúdo significativo
                        content_fields.append(f"{key}: {value}")
                
                if content_fields:
                    parts.extend(content_fields)
                else:
                    # Fallback: converte todo o dict para string limpa
                    parts.append(str(item))
            
            # Adiciona metadados se disponíveis
            metadata_info = ContextProcessor._extract_metadata_info(item)
            if metadata_info:
                parts.append(f"[Fonte: {metadata_info}]")
            
            return "\n".join(parts)
            
        except Exception as e:
            logger.error(f"Error extracting content from dict: {e}")
            return str(item)
    
    @staticmethod
    def _extract_metadata_info(item: Dict[str, Any]) -> str:
        """Extrai informações de metadados relevantes"""
        try:
            metadata_parts = []
            
            # Informações de coleção
            if 'collection' in item:
                metadata_parts.append(f"Coleção: {item['collection']}")
            
            # Score de relevância
            if 'relevance_score' in item:
                metadata_parts.append(f"Relevância: {item['relevance_score']:.3f}")
            
            # Tipo de contexto
            if 'context_type' in item:
                metadata_parts.append(f"Tipo: {item['context_type']}")
            
            # Metadados aninhados
            if 'metadata' in item and isinstance(item['metadata'], dict):
                meta = item['metadata']
                if 'function_name' in meta:
                    metadata_parts.append(f"Função: {meta['function_name']}")
                if 'enum_name' in meta:
                    metadata_parts.append(f"Enum: {meta['enum_name']}")
            
            return " | ".join(metadata_parts)
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return ""


# Patch para o sistema existente
def patch_response_generator():
    """
    Aplica patch no response generator existente para usar processamento genérico
    """
    try:
        from app.core.response_generator import ResponseGenerator
        
        # Salva o método original
        original_generate = ResponseGenerator.generate_response
        
        def patched_generate_response(self, query: str, context, history=None) -> str:
            """Versão corrigida que processa o contexto genericamente"""
            try:
                # Processa o contexto usando o processador genérico
                processed_context = ContextProcessor.process_context(context)
                
                logger.info(f"Context processed: {len(processed_context)} chars")
                
                # Chama o método original com contexto processado
                return original_generate(self, query, processed_context, history)
                
            except Exception as e:
                logger.error(f"Error in patched response generation: {e}")
                # Fallback para o método original
                return original_generate(self, query, str(context), history)
        
        # Aplica o patch
        ResponseGenerator.generate_response = patched_generate_response
        logger.info("Response generator patched successfully")
        
    except ImportError:
        logger.warning("Could not patch ResponseGenerator - original not found")
    except Exception as e:
        logger.error(f"Error patching ResponseGenerator: {e}")


def patch_simple_optimized_system():
    """
    Aplica patch no sistema otimizado para usar processamento genérico
    """
    try:
        # Importa e aplica patch
        patch_response_generator()
        
        # Agora importa o sistema otimizado
        from app.core.simple_optimized_system import EnhancedResponseGenerator
        
        # Salva o método original
        original_enhanced_generate = EnhancedResponseGenerator.enhanced_generate_response
        
        def patched_enhanced_generate(self, query: str, search_results, history=None) -> str:
            """Versão corrigida que processa search_results genericamente"""
            try:
                # Processa os resultados da busca
                processed_context = ContextProcessor.process_context(search_results)
                
                logger.info(f"Enhanced context processed: {len(processed_context)} chars")
                
                # Usa o gerador base com contexto processado
                if hasattr(self, 'generator'):
                    return self.generator.generate_response(query, processed_context, history)
                else:
                    # Fallback para método original
                    return original_enhanced_generate(self, query, search_results, history)
                
            except Exception as e:
                logger.error(f"Error in patched enhanced generation: {e}")
                # Fallback absoluto
                context_str = "\n\n".join([str(r.get('content', str(r))) for r in search_results])
                return context_str  # Retorna pelo menos o contexto bruto
        
        # Aplica o patch
        EnhancedResponseGenerator.enhanced_generate_response = patched_enhanced_generate
        logger.info("Enhanced response generator patched successfully")
        
    except ImportError:
        logger.warning("Could not patch EnhancedResponseGenerator")
    except Exception as e:
        logger.error(f"Error patching EnhancedResponseGenerator: {e}")


# Auto-apply patches when module is imported
def auto_patch():
    """Aplica patches automaticamente quando o módulo é importado"""
    try:
        patch_response_generator()
        patch_simple_optimized_system()
        logger.info("All context processing patches applied successfully")
    except Exception as e:
        logger.error(f"Error in auto-patching: {e}")

# Execute auto-patch
auto_patch()