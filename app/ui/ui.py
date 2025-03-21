import gradio as gr

class BFCScriptUI:
    def __init__(self, search_engine):
        """
        Initialize the Gradio UI for BFC-Script Assistant.
        
        Args:
            search_engine: An instance of SemanticSearch
        """
        self.search_engine = search_engine
        
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
        return self.search_engine.generate_response(message, history)
    
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