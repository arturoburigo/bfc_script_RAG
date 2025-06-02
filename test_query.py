# test_query.py
from app.core.semantic_search import SemanticSearch
from app.core.response_generator import ResponseGenerator
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_query():
    # Inicializa os componentes
    # Ensure OPENAI_API_KEY is set in your .env file or environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your .env file or environment.")
        return

    print("🚀 Inicializando componentes...")
    try:
        search_engine = SemanticSearch(api_key=api_key)
        # Check if query_analyzer was initialized correctly in SemanticSearch
        if not search_engine.query_analyzer:
            print("❌ Query Analyzer not initialized in SemanticSearch. Exiting.")
            return
            
        response_generator = ResponseGenerator(api_key=api_key)
        print("✅ Componentes inicializados com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inicializar componentes: {e}")
        return
    
    # Query de teste
    query = "crie um relatório que tenha parametro de data inicial e final onde filtra os funcionarios admitidos neste periodo"

    print(f"\n🧠 Analisando query: '{query}'...")
    # 1. Realiza a análise da query usando o analisador do search_engine
    try:
        query_analysis = search_engine.query_analyzer.analyze_query(query)
        print(f"💡 Análise da query: {query_analysis}")
    except Exception as e:
        print(f"❌ Erro ao analisar a query: {e}")
        return

    print("\n🔍 Executando busca...")
    # 2. Realiza a busca passando a query e a análise da query
    try:
        search_results = search_engine.search(query, query_analysis) # Passar query_analysis
    except Exception as e:
        print(f"❌ Erro ao executar a busca: {e}")
        return
    
    # Descomente para ver os resultados da busca
    # print(f"\n📊 Resultados encontrados: {len(search_results)}")
    # for i, result in enumerate(search_results, 1):
    #     print(f"\nResultado #{i}")
    #     print(f"  Score: {result.get('relevance_score', 0):.4f}")
    #     print(f"  Collection: {result.get('collection', 'N/A')}")
    #     print(f"  Content Preview: {result.get('content', '')[:100]}...") 
    
    print("\n🤖 Gerando resposta...")
    # 3. Gera a resposta passando a query, resultados da busca, a análise da query e o histórico
    try:
        response = response_generator.generate_response(
            query=query,
            search_results=search_results,
            query_analysis=query_analysis, # Passar query_analysis
            history=[]
        )
    except Exception as e:
        print(f"❌ Erro ao gerar a resposta: {e}")
        return
    
    print("\n📝 Resposta gerada:")
    print("=" * 80)
    print(response)
    print("=" * 80)

if __name__ == "__main__":
    test_query()