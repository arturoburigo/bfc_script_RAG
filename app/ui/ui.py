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
        
        # Categorias disponíveis
        self.categories = ["Geral", "Service Layer", "Fonte de Dados", "Relatório"]
        
    def chat_handler(self, message, history, category):
        """
        Handle incoming chat messages and generate responses.
        
        Args:
            message (str): User message
            history (list): Chat history
            category (str): Selected category
            
        Returns:
            str: Assistant response
        """
        # Adicionar contexto da categoria selecionada à mensagem
        context_message = f"[Categoria: {category}] {message}"
        
        # Obter o contexto da documentação
        context, _ = self.search_engine.get_document_context(context_message)
        
        # Gerar resposta
        response = self.response_generator.generate_response(context_message, context, history)
        return response
    
    def create_interface(self):
        """
        Create and return the Gradio chat interface.
        
        Returns:
            gr.ChatInterface: The configured Gradio interface
        """
        with gr.Blocks(theme="soft") as demo:
            gr.Markdown("# BFC-Script Assistant")
            gr.Markdown("Faça perguntas sobre BFC-Script e obtenha respostas baseadas na documentação. Para funcionalidades não documentadas, fornecerei soluções em BFC-Script e Groovy.")
            
            # Adicionar radio buttons para categorias
            category = gr.Radio(
                choices=self.categories,
                value="Geral",  # Valor padrão
                label="Selecione a categoria",
                info="Escolha a categoria da sua pergunta"
            )
            
            # Criar o chat interface
            chat = gr.ChatInterface(
                fn=self.chat_handler,
                additional_inputs=[category],
                type="messages"  # Usar o novo formato de mensagens
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