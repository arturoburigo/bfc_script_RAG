import gradio as gr
from core.semantic_search import SemanticSearch
from core.response_generator import ResponseGenerator

class BFCScriptUI:
    def __init__(self, search_engine=None, response_generator=None):
        """
        Initialize the Gradio UI for BFC-Script Assistant.
        
        Args:
            search_engine: An instance of SemanticSearch (optional)
            response_generator: An instance of ResponseGenerator (optional)
        """
        # Create instances if not provided
        self.search_engine = search_engine or SemanticSearch()
        self.response_generator = response_generator or ResponseGenerator()
    
    def chat_handler(self, message, history):
        """
        Handle incoming chat messages and generate responses.
        
        Args:
            message (str): User message
            history (list): Chat history
            
        Returns:
            str: Assistant response
        """
        # Get document context
        context, _ = self.search_engine.get_document_context(message)
        
        # Generate response
        response = self.response_generator.generate_response(message, context, history)
        return response
    
    def create_interface(self):
        """
        Create and return the Gradio chat interface.
        
        Returns:
            gr.ChatInterface: The configured Gradio interface
        """
        with gr.Blocks(theme="soft") as demo:
            gr.Markdown("# BFC-Script Assistant")
            gr.Markdown("""
            Bem-vindo ao BFC-Script Assistant! 
            
            Este assistente utiliza a documentação do BFC-Script para responder suas perguntas e gerar código.
            Você pode perguntar sobre:
            - Sintaxe e funcionalidades do BFC-Script
            - Exemplos de código e implementações
            - Enums e funções disponíveis
            - Boas práticas e padrões de desenvolvimento
            
            O assistente irá automaticamente buscar as informações mais relevantes em toda a base de conhecimento.
            """)
            
            # Create the chat interface
            chat = gr.ChatInterface(
                fn=self.chat_handler,
                title="Chat",
                description="Faça suas perguntas sobre BFC-Script",
                examples=[
                    "Como criar uma função no BFC-Script?",
                    "Quais são os tipos de dados suportados?",
                    "Como fazer um loop em BFC-Script?",
                    "Mostre um exemplo de uso de enums"
                ],
                theme="soft"
            )
            
        return demo
    
    def launch(self, share=True):
        """
        Launch the Gradio interface.
        
        Args:
            share (bool): Whether to create a public sharable link
            
        Returns:
            gr.Interface: The running interface
        """
        interface = self.create_interface()
        print("Iniciando o BFC-Script Assistant...")
        return interface.launch(share=share)