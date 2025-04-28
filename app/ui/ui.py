import logging
import gradio as gr
from typing import Optional, List, Tuple
from app.core.semantic_search import SemanticSearch
from app.core.response_generator import ResponseGenerator
from app.core.config import setup_logging, is_dev_mode, log_debug, log_function_call, log_function_return

# Configure logging
logger = setup_logging(__name__, "logs/ui.log")

class BFCScriptUI:
    def __init__(self, search_engine=None, response_generator=None):
        """Initialize the UI with a RAG system."""
        log_function_call(logger, "BFCScriptUI.__init__")
        self.search_engine = search_engine
        self.response_generator = response_generator

    def _process_query(
        self, 
        message: str, 
        history: List[Tuple[str, str]]
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """Process a user query and return the response with updated history."""
        log_function_call(logger, "BFCScriptUI._process_query", kwargs={"message": message})
        
        try:
            # Use the search engine to find relevant documents
            search_results = self.search_engine.search(message)
            
            # Generate a response using the response generator
            response = self.response_generator.generate_response(message, search_results)
            
            history.append((message, response))
            log_function_return(logger, "BFCScriptUI._process_query", response=response)
            return "", history
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            history.append((message, error_msg))
            log_function_return(logger, "BFCScriptUI._process_query", error=error_msg)
            return "", history

    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface."""
        log_function_call(logger, "BFCScriptUI.create_interface")
        
        with gr.Blocks(title="BFC Script Assistant") as interface:
            gr.Markdown("# BFC Script Assistant")
            gr.Markdown("Ask questions about BFC Script programming.")
            
            chatbot = gr.Chatbot(
                height=600,
                show_copy_button=True,
                bubble_full_width=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your question here...",
                    show_label=False,
                    container=False
                )
                submit = gr.Button("Send", variant="primary")
            
            clear = gr.Button("Clear Conversation")
            
            def user(user_message, history):
                return "", history + [[user_message, None]]
            
            def bot(history):
                history[-1][1] = ""
                # Use the search engine to find relevant documents
                search_results = self.search_engine.search(history[-1][0])
                
                # Generate a response using the response generator
                response = self.response_generator.generate_response(history[-1][0], search_results)
                history[-1][1] = response
                yield history
            
            submit.click(
                user,
                [msg, chatbot],
                [msg, chatbot],
                queue=False
            ).then(
                bot,
                chatbot,
                chatbot
            )
            
            msg.submit(
                user,
                [msg, chatbot],
                [msg, chatbot],
                queue=False
            ).then(
                bot,
                chatbot,
                chatbot
            )
            
            clear.click(lambda: None, None, chatbot, queue=False)
        
        log_function_return(logger, "BFCScriptUI.create_interface", result=interface)
        return interface

    def run(self, share: bool = False):
        """Run the Gradio interface."""
        log_function_call(logger, "BFCScriptUI.run", kwargs={"share": share})
        
        interface = self.create_interface()
        interface.launch(
            share=share,
            server_name="0.0.0.0",
            server_port=7860
        )
        log_function_return(logger, "BFCScriptUI.run", result=None)