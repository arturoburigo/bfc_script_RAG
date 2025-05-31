# app/ui/optimized_ui.py - UI Simplificada Otimizada
import logging
import gradio as gr
from typing import List, Tuple, Optional, Union
from app.core.simple_optimized_system import SimpleOptimizedRAGSystem, RAGResponse
from app.core.semantic_search import SemanticSearch
from app.core.response_generator import ResponseGenerator
from app.core.config import setup_logging
import time
import json

# Configure logging
logger = setup_logging(__name__, "logs/simple_optimized_ui.log")

class SimpleOptimizedBFCScriptUI:
    def __init__(self, 
                 search_engine: Union[SimpleOptimizedRAGSystem, SemanticSearch],
                 response_generator: Optional[ResponseGenerator] = None):
        """
        Initialize the optimized UI with either a complete RAG system or separate components.
        
        Args:
            search_engine: Either a SimpleOptimizedRAGSystem or SemanticSearch instance
            response_generator: ResponseGenerator instance (required if search_engine is SemanticSearch)
        """
        if isinstance(search_engine, SimpleOptimizedRAGSystem):
            self.rag_system = search_engine
            self.search_engine = search_engine.search_engine
            self.response_generator = search_engine.response_generator
        else:
            if response_generator is None:
                raise ValueError("response_generator is required when using separate components")
            self.rag_system = None
            self.search_engine = search_engine
            self.response_generator = response_generator
            
        self.conversation_history = []
        
    def _process_query(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Process a user query and return the response with updated history."""
        try:
            start_time = time.time()
            
            # Convert Gradio history format to our format
            conversation_history = [(h[0], h[1]) for h in history] if history else []
            
            # Process query based on initialization type
            if self.rag_system is not None:
                # Use integrated RAG system
                rag_response: RAGResponse = self.rag_system.query(
                    query_text=message,
                    conversation_history=conversation_history
                )
                response = rag_response.response
                relevance_score = rag_response.relevance_score
                sources = rag_response.sources
            else:
                # Use separate components
                search_results = self.search_engine.search(message)
                response = self.response_generator.generate_response(
                    query=message,
                    search_results=search_results,
                    history=conversation_history
                )
                relevance_score = 1.0  # Default score for separate components
                sources = len(search_results)
            
            # Store in internal history for context
            self.conversation_history = conversation_history + [(message, response)]
            
            # Update Gradio history
            updated_history = history + [[message, response]]
            
            # Log query processing
            processing_time = time.time() - start_time
            logger.info(f"Query processed - Time: {processing_time:.3f}s, "
                       f"Relevance: {relevance_score:.3f}, "
                       f"Sources: {sources}")
            
            return "", updated_history
            
        except Exception as e:
            error_msg = f"❌ Erro ao processar consulta: {str(e)}"
            logger.error(f"Error processing query: {str(e)}")
            
            # Add error to history
            updated_history = history + [[message, error_msg]]
            return "", updated_history

    def _get_system_info(self) -> str:
        """Get current system information for display"""
        try:
            if self.rag_system is not None:
                status = self.rag_system.get_system_status()
                
                info_parts = [
                    "🔧 **Status do Sistema RAG Simplificado**",
                    f"📊 Sistema Inicializado: {'✅ Sim' if status['system_initialized'] else '❌ Não'}",
                    f"⚙️ Ambiente: {status['config_environment']}",
                    f"💾 Cache: {'✅ Ativo' if status['cache_enabled'] else '❌ Inativo'} ({status['cache_entries']} entradas)",
                ]
                
                if 'search_engine' in status:
                    search_info = status['search_engine']
                    info_parts.extend([
                        f"🔍 Coleções Carregadas: {search_info['collections_loaded']}",
                        f"📄 Total de Documentos: {search_info['total_documents']}",
                    ])
            else:
                info_parts = [
                    "🔧 **Status do Sistema RAG Simplificado**",
                    "📊 Sistema Inicializado: ✅ Sim",
                    "⚙️ Modo: Componentes Separados",
                    "🔍 Busca Semântica: ✅ Ativa",
                    "🤖 Gerador de Respostas: ✅ Ativo"
                ]
            
            info_parts.extend([
                "",
                "🚀 **Melhorias Ativas**",
                "✅ Análise inteligente de consultas",
                "✅ Busca semântica otimizada",
                "✅ Reranking por tipo de conteúdo",
                "✅ Geração de resposta adaptativa",
                "✅ Cache de consultas",
                "✅ Classificação automática de contexto"
            ])
            
            return "\n".join(info_parts)
            
        except Exception as e:
            return f"❌ Erro ao obter status do sistema: {str(e)}"

    def _get_query_examples(self) -> List[str]:
        """Get example queries"""
        return [
            "Como criar um relatório de funcionários usando BFC-Script?",
            "Quais são os campos disponíveis na fonte Dados.pessoal.v2.funcionario?",
            "Exemplo de código para buscar rubricas de um funcionário específico",
            "Como filtrar funcionários por departamento usando expressões?",
            "Quais enums estão disponíveis para classificação de funcionários?",
            "Criar script para calcular folha de pagamento",
            "Como fazer ordenação de resultados por nome do funcionário?",
            "Implementar busca de funcionários por cargo",
            "Como acessar dados históricos de um funcionário?",
            "Exemplo de uso da fonte Dados.folha.v2 para eventos"
        ]

    def create_interface(self) -> gr.Blocks:
        """Create the simplified optimized Gradio interface."""
        
        # Custom CSS for better styling
        custom_css = """
        .system-info {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            font-family: monospace;
        }
        .examples-panel {
            background-color: #e8f4fd;
            border: 1px solid #b6d7ff;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .chat-container {
            height: 600px;
        }
        """
        
        with gr.Blocks(
            title="BFC Script Assistant Otimizado", 
            theme=gr.themes.Soft(),
            css=custom_css
        ) as interface:
            
            # Header
            gr.Markdown("""
            # 🚀 BFC Script Assistant Otimizado
            ### Sistema RAG com melhorias de performance e qualidade
            """)
            
            # Main layout
            with gr.Row():
                # Main chat area
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        height=500,
                        show_copy_button=True,
                        bubble_full_width=False,
                        elem_id="chatbot",
                        )
                    
                    # Input area
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Digite sua pergunta sobre BFC Script...",
                            show_label=False,
                            container=False,
                            scale=9
                        )
                        submit = gr.Button("Enviar", variant="primary", scale=1)
                    
                    # Action buttons
                    with gr.Row():
                        clear = gr.Button("Limpar Conversa", variant="secondary")
                        examples_btn = gr.Button("Ver Exemplos", variant="secondary")
                
                # Sidebar with info and examples
                with gr.Column(scale=1):
                    # System status
                    with gr.Group():
                        gr.Markdown("### 🔧 Status do Sistema")
                        system_info = gr.Markdown(
                            self._get_system_info(),
                            elem_classes=["system-info"]
                        )
                        refresh_status = gr.Button("🔄 Atualizar Status", size="sm")
                    
                    # Quick stats
                    with gr.Group():
                        gr.Markdown("### 📊 Estatísticas da Sessão")
                        stats_display = gr.Markdown(
                            "**Consultas nesta sessão:** 0\n**Cache hits:** 0\n**Tempo médio:** 0.0s",
                            elem_classes=["system-info"]
                        )
            
            # Examples section (initially hidden)
            with gr.Row(visible=False) as examples_row:
                with gr.Column():
                    gr.Markdown("### 💡 Exemplos de Consultas")
                    examples_list = gr.Examples(
                        examples=[[example] for example in self._get_query_examples()],
                        inputs=msg,
                        label="Clique em um exemplo para usá-lo:"
                    )
            
            # Statistics tracking
            session_stats = gr.State({"queries": 0, "cache_hits": 0, "total_time": 0.0})
            
            # Event handlers
            def user_message(user_message, history):
                return "", history + [[user_message, None]]
            
            def bot_response(history, stats):
                if history and history[-1][1] is None:
                    user_msg = history[-1][0]
                    
                    # Track timing
                    start_time = time.time()
                    
                    # Check if it was a cache hit
                    cache_key = self.rag_system._generate_cache_key(user_msg, [])
                    was_cache_hit = cache_key in self.rag_system._query_cache
                    
                    # Process query
                    _, updated_history = self._process_query(user_msg, history[:-1])
                    
                    # Update stats
                    processing_time = time.time() - start_time
                    stats["queries"] += 1
                    stats["total_time"] += processing_time
                    if was_cache_hit:
                        stats["cache_hits"] += 1
                    
                    return updated_history, stats
                return history, stats
            
            def clear_history():
                self.conversation_history = []
                return []
            
            def toggle_examples():
                return gr.update(visible=True)
            
            def update_system_status():
                return self._get_system_info()
            
            def update_stats_display(stats):
                if stats["queries"] > 0:
                    avg_time = stats["total_time"] / stats["queries"]
                    cache_rate = (stats["cache_hits"] / stats["queries"]) * 100
                else:
                    avg_time = 0.0
                    cache_rate = 0.0
                
                return f"""**Consultas nesta sessão:** {stats["queries"]}
**Cache hits:** {stats["cache_hits"]} ({cache_rate:.1f}%)
**Tempo médio:** {avg_time:.2f}s
**Tempo total:** {stats["total_time"]:.1f}s"""
            
            # Connect events
            submit_event = submit.click(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            ).then(
                fn=bot_response,
                inputs=[chatbot, session_stats],
                outputs=[chatbot, session_stats]
            ).then(
                fn=update_stats_display,
                inputs=session_stats,
                outputs=stats_display
            )
            
            msg_event = msg.submit(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            ).then(
                fn=bot_response,
                inputs=[chatbot, session_stats],
                outputs=[chatbot, session_stats]
            ).then(
                fn=update_stats_display,
                inputs=session_stats,
                outputs=stats_display
            )
            
            clear.click(
                fn=clear_history,
                inputs=[],
                outputs=chatbot
            )
            
            examples_btn.click(
                fn=toggle_examples,
                inputs=[],
                outputs=examples_row
            )
            
            refresh_status.click(
                fn=update_system_status,
                inputs=[],
                outputs=system_info
            )
        
        return interface

    def run(self, share: bool = False):
        """Run the simplified optimized Gradio interface."""
        interface = self.create_interface()
        interface.queue()  # Enable queuing for better performance
        
        logger.info("Starting simplified optimized UI...")
        interface.launch(
            share=share,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            show_api=False
        )