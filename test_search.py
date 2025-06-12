#!/usr/bin/env python3
from app.core.integrated_rag_system import OptimizedSearchSystem
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def main():
    # Inicializa os componentes
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your .env file or environment.")
        return

    print("🚀 Inicializando componentes...")
    try:
        search_system = OptimizedSearchSystem(api_key=api_key)
        
        # Initialize the database
        print("📚 Inicializando banco de dados...")
        stats = search_system.initialize_database(reset_collections=False)
        print(f"✅ Banco de dados inicializado: {stats}")
        
        if not search_system.is_initialized:
            print("❌ Falha na inicialização do banco de dados.")
            return
            
        print("✅ Componentes inicializados com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inicializar componentes: {e}")
        return
    
    while True:
        # Query do usuário
        query = input("\n🔍 Digite sua busca (ou 'sair' para terminar): ")
        if query.lower() == 'sair':
            break

        print(f"\n🧠 Analisando query: '{query}'...")
        try:
            # Execute search
            print("\n🔍 Executando busca...")
            search_response = search_system.search(query, top_k=10)
            
            # Mostra os resultados
            print("\n=== RESULTADOS DA BUSCA ===")
            print("=" * 80)
            for i, result in enumerate(search_response.results, 1):
                print(f"\nResultado #{i}")
                print(f"Collection: {result['collection']}")
                print(f"Score: {result['relevance_score']:.4f}")
                print(f"Content:\n{result['content']}")
                print("-" * 80)
            
            print(f"\n⏱️ Tempo de processamento: {search_response.processing_time:.2f} segundos")
            print(f"📊 Análise da query: {search_response.metadata['query_analysis']}")
            
        except Exception as e:
            print(f"❌ Erro ao executar a busca: {e}")

if __name__ == "__main__":
    main() 