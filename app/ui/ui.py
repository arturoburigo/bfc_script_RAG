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
        # Criar instâncias se não forem fornecidas
        self.search_engine = search_engine or SemanticSearch()
        self.response_generator = response_generator or ResponseGenerator()
        
        # Sample examples for the interface
        self.examples = [
            "Como fazer loop imprimindo apenas numeros pares ?", 
            "Como trabalhar com arquivos?", 
            "Como mandar um email?",
            "Como calcular a diferença de dias entre duas datas?",
            "Como separar números pares e ímpares em um array?",
            "Como converter temperatura de Fahrenheit para Celsius?",
            "Qual a sintaxe correta para declarar funções em BFC-Script?",
            "Como realizar operações matemáticas básicas em BFC-Script?"
        ]
    
    def chat_handler(self, message, history):
        """
        Handle incoming chat messages and generate responses.
        
        Args:
            message (str): User message
            history (list): Chat history
            
        Returns:
            str: Assistant response
        """
        # Obter o contexto da documentação
        context, _ = self.search_engine.get_document_context(message)
        
        # Gerar resposta
        response = self.response_generator.generate_response(message, context, history)
        return response
    
    def create_interface(self):
        """
        Create and return the Gradio chat interface.
        
        Returns:
            gr.ChatInterface: The configured Gradio interface
        """
        demo = gr.ChatInterface(
            fn=self.chat_handler,
            title="BFC-Script Assistant",
            description="Faça perguntas sobre BFC-Script e obtenha respostas baseadas na documentação. Para funcionalidades não documentadas, fornecerei soluções em BFC-Script e Groovy.",
            theme="soft",
            examples=self.examples
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