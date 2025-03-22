import os
from core.semantic_search import SemanticSearch
from core.response_generator import ResponseGenerator
from ui.ui import BFCScriptUI

def main():
    """
    Ponto de entrada principal da aplicação BFC-Script Assistant.
    """
    # Verificar se a chave API está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("AVISO: OPENAI_API_KEY não está definida no ambiente. Por favor, defina-a antes de executar o aplicativo.")
        return
    
    # Configurar ambiente para evitar warning do tokenizer
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    try:
        # Inicializar componentes principais
        search_engine = SemanticSearch(api_key=api_key)
        response_generator = ResponseGenerator(api_key=api_key)
        
        # Criar e lançar a interface do usuário
        bfc_ui = BFCScriptUI(search_engine, response_generator)
        bfc_ui.launch(share=True)
    except Exception as e:
        print(f"Erro ao iniciar o BFC-Script Assistant: {str(e)}")

if __name__ == "__main__":
    main()