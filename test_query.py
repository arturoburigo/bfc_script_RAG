# test_query.py
from app.core.integrated_rag_system import OptimizedSearchSystem
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import re

# Carrega variáveis de ambiente
load_dotenv()

def analyze_search_results(search_results: list, query: str, query_analysis: dict):
    """Analisa e exibe informações detalhadas sobre os resultados da busca."""
    print("\n📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("=" * 80)
    
    # Estatísticas gerais
    print(f"🔍 Total de resultados: {len(search_results)}")
    
    # Distribuição por coleção
    collections = {}
    for result in search_results:
        collection = result.get('collection', 'unknown')
        collections[collection] = collections.get(collection, 0) + 1
    
    print("\n📚 Distribuição por coleção:")
    for collection, count in collections.items():
        print(f"  - {collection}: {count} resultados")
    
    # Análise de scores
    scores = [r.get('relevance_score', 0) for r in search_results]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    print(f"\n🎯 Métricas de relevância:")
    print(f"  - Score médio: {avg_score:.4f}")
    print(f"  - Score máximo: {max_score:.4f}")
    print(f"  - Score mínimo: {min_score:.4f}")
    
    # Análise de conteúdo
    print("\n📝 Análise de conteúdo:")
    code_examples = sum(1 for r in search_results if r.get('has_code_example', False))
    print(f"  - Exemplos de código encontrados: {code_examples}")
    
    # Agrupar resultados por base chunk_key
    grouped_results = {}
    for result in search_results:
        metadata = result.get("metadata", {})
        chunk_key = metadata.get("chunk_key", "")
        base_key = re.sub(r'_part\d+_\d+$', '', chunk_key)
        
        if base_key not in grouped_results:
            grouped_results[base_key] = []
        grouped_results[base_key].append(result)
    
    # Construir o contexto exato que seria enviado para o LLM
    print("\n🔍 CONTEXTO EXATO QUE SERIA ENVIADO PARA O LLM")
    print("=" * 80)
    
    context_parts = []
    
    # Query Information
    context_parts.append("## Query Information")
    context_parts.append(f"Original Query: {query}")
    context_parts.append(f"Expected Output Type: {query_analysis.get('expected_output', 'unknown')}")
    context_parts.append(f"Query Intents: {', '.join(query_analysis.get('intents', []))}\n")
    
    # Process each group of related chunks
    for base_key, group in grouped_results.items():
        # Sort group by part number
        group.sort(key=lambda x: int(re.search(r'_part\d+_(\d+)$', x.get("metadata", {}).get("chunk_key", "")).group(1)) if re.search(r'_part\d+_(\d+)$', x.get("metadata", {}).get("chunk_key", "")) else 0)
        
        # Calculate average score for the group
        avg_score = sum(r.get("relevance_score", 0.0) for r in group) / len(group)
        
        # Add group header
        context_parts.append(f"\n## Related Information Group (Average Score: {avg_score:.4f})")
        
        # Add metadata information
        metadata = group[0].get("metadata", {})
        context_parts.append(f"Source: {group[0].get('collection', 'Unknown')}")
        if "file_path" in metadata:
            context_parts.append(f"File: {metadata['file_path']}")
        if "title" in metadata:
            context_parts.append(f"Title: {metadata['title']}")
        
        # Add content from all parts
        context_parts.append("\n### Content")
        for i, result in enumerate(group, 1):
            part_num = re.search(r'_part\d+_(\d+)$', result.get("metadata", {}).get("chunk_key", "")).group(1) if re.search(r'_part\d+_(\d+)$', result.get("metadata", {}).get("chunk_key", "")) else str(i)
            context_parts.append(f"Part {part_num} (Score: {result['relevance_score']:.4f}):")
            context_parts.append(f"{result['content']}\n")
        
        # Add relevance indicators
        context_parts.append("### Relevance Indicators")
        indicators = []
        if any(r.get("has_code_example") for r in group):
            indicators.append("Contains code examples")
        if any(r.get("has_field_definition") for r in group):
            indicators.append("Contains field definitions")
        if any(r.get("has_method_description") for r in group):
            indicators.append("Contains method descriptions")
        context_parts.append(", ".join(indicators) + "\n")
    
    # Print the exact context
    print("\n".join(context_parts))
    print("=" * 80)

def test_query():
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
        stats = search_system.initialize_database(reset_collections=True)
        print(f"✅ Banco de dados inicializado: {stats}")
        
        if not search_system.is_initialized:
            print("❌ Falha na inicialização do banco de dados.")
            return
            
        print("✅ Componentes inicializados com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inicializar componentes: {e}")
        return
    
    # Query de teste
    query = "   "

    print(f"\n🧠 Analisando query: '{query}'...")
    try:
        # Execute search
        print("\n🔍 Executando busca...")
        start_time = datetime.now()
        search_response = search_system.search(query, top_k=10)
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        print(f"✅ Busca concluída em {search_duration:.2f} segundos")
        
        # Análise detalhada dos resultados
        analyze_search_results(search_response.results, query, search_response.metadata['query_analysis'])
        
        # Gerar resposta da LLM
        print("\n🤖 Gerando resposta da LLM (GPT-4o-mini)...")
        llm_result = search_system.generate_llm_response(query, top_k=10)
        print("\n================ LLM RESPONSE ================")
        print(llm_result["llm_response"])
        print("==============================================")
        
    except Exception as e:
        print(f"❌ Erro ao executar a busca: {e}")
        return

if __name__ == "__main__":
    test_query()