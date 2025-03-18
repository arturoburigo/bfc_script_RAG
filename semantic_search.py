import json
import os
import faiss
import gradio as gr
import numpy as np
from openai import OpenAI

# Configurar o ambiente para evitar warning do tokenizer
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Use a mesma chave API para todo o aplicativo
OPENAI_API_KEY = ""

def search(query, top_k=8):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Criar embeddings expandidos para melhorar a busca semântica
        expanded_query = f"{query} BFC-Script documentação exemplos código sintaxe"
        
        # Criar o embedding da pergunta usando text-embedding-3-large
        query_embedding_response = client.embeddings.create(
            model="text-embedding-3-large",
            input=expanded_query
        )
        query_embedding = query_embedding_response.data[0].embedding
        
        # Converter para o formato numpy necessário para FAISS
        query_embedding_np = np.array(query_embedding).astype("float32").reshape(1, -1)
        
        # Carregar o índice FAISS
        index = faiss.read_index("index/faiss_index.bin")
        
        # Buscar os k resultados mais próximos
        distances, indices = index.search(query_embedding_np, top_k)
        
        # Carregar os chunks para retornar os textos
        with open("docs/chunks_embedded/documentation_chunks_with_embeddings.json", "r", encoding="utf-8") as file:
            document_chunks = json.load(file)
        
        # Filtrar resultados por relevância usando um threshold
        filtered_results = []
        for i, idx in enumerate(indices[0]):
            if distances[0][i] < 1.0:  # Ajuste este threshold conforme necessário
                filtered_results.append(document_chunks[idx])
        
        # Se não houver resultados relevantes, retornar alguns para contexto geral
        if not filtered_results and len(indices[0]) > 0:
            filtered_results = [document_chunks[idx] for idx in indices[0][:3]]
            
        return filtered_results
    except Exception as e:
        print(f"Erro na busca: {str(e)}")
        return []

def extract_syntax_patterns(context):
    """
    Extrai padrões sintáticos comuns do BFC-Script do contexto para auxiliar
    na geração de código quando a documentação específica não está disponível.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        syntax_prompt = f"""
        Analise a documentação do BFC-Script abaixo e extraia os padrões sintáticos essenciais,
        incluindo como declarar variáveis, funções, estruturas de controle e operações comuns.
        
        DOCUMENTAÇÃO:
        {context}
        
        EXTRAIA APENAS:
        1. Como declarar e chamar funções (não use palavras como "função", "def", etc. se não aparecerem na documentação)
        2. Como criar estruturas de controle (if, else, loops)
        3. Como declarar variáveis e seus tipos
        4. Operadores e sintaxe de expressões
        5. Convenções de nomenclatura observadas
        
        Forneça um resumo conciso APENAS dos padrões sintáticos observados, sem elaborar.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um analisador sintático técnico que extrai padrões de código de documentação."},
                {"role": "user", "content": syntax_prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao extrair padrões sintáticos: {str(e)}")
        return ""

def rag_response(query, history=None):
    try:
        # Incorporate chat history context for better continuity
        history_context = ""
        if history and len(history) > 0:
            last_exchanges = history[-3:] if len(history) > 3 else history
            history_context = "\n".join([f"Usuário: {q}\nAssistente: {a}" for q, a in last_exchanges])
        
        # Buscar documentação relevante
        results = search(query)
        
        if not results:
            return "Não foi possível realizar a busca semântica. Verifique os logs para mais detalhes."
            
        context = "\n".join([r["content"] for r in results])
        
        # Extrair padrões sintáticos para uso em respostas não documentadas
        syntax_patterns = extract_syntax_patterns(context)
        
        # Usar a mesma chave API que usamos para embeddings
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prompt aprimorado com foco na sintaxe correta e convenções do BFC-Script
        prompt = f"""
        Consulte a documentação do BFC-Script fornecida para responder à pergunta do usuário.

        DOCUMENTAÇÃO (contexto recuperado):
        {context}
        
        PADRÕES SINTÁTICOS DO BFC-SCRIPT:
        {syntax_patterns}
        
        HISTÓRICO DE CONVERSA RECENTE:
        {history_context}

        PERGUNTA DO USUÁRIO: {query}

        INSTRUÇÕES ESPECÍFICAS:
        1. PRIMEIRO: Verifique cuidadosamente se a documentação fornecida contém exemplos diretos ou informações suficientes para responder à pergunta.
        
        2. Se a documentação CONTIVER informações suficientes:
           - Cite diretamente trechos relevantes da documentação
           - Use APENAS as estruturas sintáticas, funções e padrões EXATAMENTE como aparecem na documentação
           - Forneça exemplos de código que sigam fielmente os exemplos encontrados
           - NÃO INVENTE funções ou métodos que não estejam na documentação
        
        3. Se a documentação NÃO CONTIVER informações suficientes:
           - Indique claramente: "Esta funcionalidade específica não está documentada no material fornecido. Vou mostrar duas soluções:"
           - SOLUÇÃO 1: Crie uma implementação usando APENAS os padrões sintáticos do BFC-Script identificados na documentação. Se não houver exemplos claros de como declarar funções no BFC-Script, NÃO use palavras-chave como "função", "def", etc.
           - SOLUÇÃO 2: Forneça uma implementação equivalente em Groovy, claramente identificada: "### Implementação alternativa em Groovy:"
        
        4. IMPORTANTE - CONVENÇÕES DE CÓDIGO:
           - NÃO use acentos em nomes de funções ou variáveis
           - Siga estritamente as convenções de nomenclatura observadas na documentação
           - Mantenha consistência com maiúsculas/minúsculas em palavras-chave
           - Se você não vir exemplos claros da sintaxe para declarar funções, variáveis ou estruturas, PERGUNTE-SE: "Como isso aparece nos exemplos da documentação?" e siga apenas esses exemplos
        
        5. PARA CÓDIGO NÃO DOCUMENTADO:
           - Analise a documentação para identificar padrões sintáticos (como loops são escritos, como funções são declaradas)
           - Siga ESTRITAMENTE esses padrões ao criar novos exemplos
           - Se não houver exemplos de uma estrutura específica, mencione isso e sugira alternativas que estejam documentadas
        """

        system_prompt = """
        Você é um especialista técnico em BFC-Script que prioriza a precisão sintática acima de tudo.
        
        GUIA DE ESTILO:
        1. Seja extremamente rigoroso com a sintaxe - NUNCA invente sintaxe que não tenha exemplo na documentação
        2. Quando não tiver certeza da sintaxe correta, opte por fornecer duas soluções: uma tentativa baseada apenas na documentação disponível e uma alternativa em Groovy
        3. Cite exemplos específicos da documentação para justificar suas escolhas sintáticas
        4. Para qualquer código BFC-Script, analise criticamente se cada linha segue exatamente os padrões observados na documentação
        5. Sempre considere que palavras-chave como "função", "if", "for" podem ser completamente diferentes em BFC-Script - use apenas o que está documentado
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        return f"Ocorreu um erro ao processar sua consulta: {str(e)}"

# Função para a interface de chat que mantém histórico
def chat_interface(message, history):
    full_history = history if history else []
    response = rag_response(message, full_history)
    return response

# Criar interface Gradio
demo = gr.ChatInterface(
    fn=chat_interface,
    title="BFC-Script Assistant",
    description="Faça perguntas sobre BFC-Script e obtenha respostas baseadas na documentação. Para funcionalidades não documentadas, fornecerei soluções em BFC-Script e Groovy.",
    theme="soft",
    examples=[
        "Como fazer loop em BFC-Script?", 
        "Como trabalhar com arquivos?", 
        "Como mandar um email?",
        "Como calcular a diferença de dias entre duas datas?",
        "Como separar números pares e ímpares em um array?",
        "Como converter temperatura de Fahrenheit para Celsius?",
        "Qual a sintaxe correta para declarar funções em BFC-Script?",
        "Como realizar operações matemáticas básicas em BFC-Script?"
    ]
)

# Iniciar a interface
if __name__ == "__main__":
    print("Iniciando o BFC-Script Assistant...")
    demo.launch(share=True)  # share=True cria uma URL pública temporária