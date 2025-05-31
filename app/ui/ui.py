import logging
import gradio as gr
from typing import List, Tuple
from app.core.semantic_search import SemanticSearch
from app.core.response_generator import ResponseGenerator
from app.core.config import setup_logging

# Configure logging
logger = setup_logging(__name__, "logs/ui.log")

class BFCScriptUI:
    def __init__(self, search_engine: SemanticSearch, response_generator: ResponseGenerator):
        """Initialize the UI with search engine and response generator."""
        self.search_engine = search_engine
        self.response_generator = response_generator

    def _process_query(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Process a user query and return the response with updated history."""
        try:
            # Search for relevant documents
            search_results = self.search_engine.search(message)
            
            # Generate response
            response = self.response_generator.generate_response(message, search_results)
            
            # Update history
            history.append((message, response))
            return "", history
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append((message, error_msg))
            return "", history

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="BFC Script Assistant", theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown("# 🤖 BFC Script Assistant")
            gr.Markdown("Ask questions about BFC Script programming and get instant answers.")
            
            # Chat interface
            chatbot = gr.Chatbot(
                height=500,
                show_copy_button=True,
                bubble_full_width=False,
                elem_id="chatbot"
            )
            
            # Input area
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your question here...",
                    show_label=False,
                    container=False,
                    scale=9
                )
                submit = gr.Button("Send", variant="primary", scale=1)
            
            # Clear button
            clear = gr.Button("Clear Conversation", variant="secondary")
            
            # Event handlers
            def user(user_message, history):
                return "", history + [[user_message, None]]
            
            def bot(history):
                history[-1][1] = ""
                search_results = self.search_engine.search(history[-1][0])
                response = self.response_generator.generate_response(history[-1][0], search_results)
                history[-1][1] = response
                yield history
            
            def clear_history():
                return []
            
            # Connect events
            submit.click(
                fn=user,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            ).then(
                fn=bot,
                inputs=chatbot,
                outputs=chatbot
            )
            
            msg.submit(
                fn=user,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            ).then(
                fn=bot,
                inputs=chatbot,
                outputs=chatbot
            )
            
            clear.click(
                fn=clear_history,
                inputs=[],
                outputs=chatbot
            )
        
        return interface

    def run(self, share: bool = False):
        """Run the Gradio interface."""
        interface = self.create_interface()
        interface.queue()  # Enable queuing for better performance
        interface.launch(
            share=share,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            show_api=False
        ) 