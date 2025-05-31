from app.core.semantic_search import SemanticSearch
from app.core.response_generator import ResponseGenerator
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_query():
    # Inicializa os componentes
    search_engine = SemanticSearch()
    response_generator = ResponseGenerator()
    
    # Query de teste
    query = "crie um relatório que tenha parametro de data inicial e final onde filtra os funcionarios admitidos neste periodo"
    
    print("\n🔍 Executando busca...")
    # Realiza a busca
    search_results = search_engine.search(query)
    
    print(f"\n📊 Resultados encontrados: {len(search_results)}")
    for i, result in enumerate(search_results, 1):
        print(f"\nResultado #{i}")
        print(f"Score: {result.get('relevance_score', 0):.4f}")
        print(f"Collection: {result.get('collection', 'N/A')}")
        print(f"Content Preview: {result.get('content', '')[:200]}...")
    
    print("\n🤖 Gerando resposta...")
    # Gera a resposta
    response = response_generator.generate_response(
        query=query,
        search_results=search_results,
        history=[]
    )
    
    print("\n📝 Resposta gerada:")
    print("=" * 80)
    print(response)
    print("=" * 80)

if __name__ == "__main__":
    test_query() 