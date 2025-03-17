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

def search(query, top_k=5):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Criar o embedding da pergunta usando text-embedding-3-large
        query_embedding_response = client.embeddings.create(
            model="text-embedding-3-large",
            input=query
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
        
        # Retornar os chunks mais relevantes
        results = [document_chunks[idx] for idx in indices[0]]
        return results
    except Exception as e:
        print(f"Erro na busca: {str(e)}")
        return []

def rag_response(query):
    try:
        results = search(query)
        
        if not results:
            return "Não foi possível realizar a busca semântica. Verifique os logs para mais detalhes."
            
        context = "\n".join([r["content"] for r in results])

        # Usar a mesma chave API que usamos para embeddings
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prompt unificado que permite que o modelo decida se precisa usar conhecimento externo
        prompt = f"""
        Consulte a documentação do BFC-Script fornecida para responder à pergunta do usuário.

        DOCUMENTAÇÃO (contexto recuperado):
        {context}

        PERGUNTA DO USUÁRIO: {query}

        INSTRUÇÕES ESPECÍFICAS:
        1. PRIMEIRO: Analise se a documentação fornecida contém informações suficientes para responder diretamente à pergunta.
        
        2. Se a documentação CONTIVER informações suficientes:
           - Analise cuidadosamente toda a documentação fornecida no contexto
           - Identifique seções relevantes, funções, exemplos de código e explicações técnicas
           - Cite diretamente trechos relevantes da documentação ao responder
           - Forneça exemplos de código específicos encontrados na documentação
           - Use APENAS as informações encontradas na documentação
        
        3. Se a documentação NÃO CONTIVER informações suficientes para responder à pergunta (caso de algoritmos específicos ou funcionalidades não documentadas):
           - Indique brevemente no início da resposta: "Esta funcionalidade específica não está documentada, mas posso fornecer uma solução baseada nos padrões sintáticos do BFC-Script."
           - Use seu conhecimento geral para resolver o problema solicitado
           - MUITO IMPORTANTE: Adapte a solução seguindo estritamente a sintaxe e padrões do BFC-Script observados na documentação fornecida
           - Use apenas estruturas e comandos que parecem compatíveis com BFC-Script
           - Lembre-se que as funções em BFC-Script não utilizam acentos
           - Forneça uma solução completa com código e explicações

        4. Em ambos os casos, SEMPRE:
           - Priorize a clareza e precisão nas explicações
           - Forneça exemplos práticos de código
           - funções não utilizam acentos
        """

        system_prompt = "Você é um especialista em BFC-Script capaz de responder perguntas usando a documentação fornecida. Para questões diretamente cobertas pela documentação, você cita e utiliza apenas o material documentado. Para questões sobre algoritmos ou funcionalidades não documentadas, você primeiro indica que está fornecendo uma solução baseada nos padrões sintáticos do BFC-Script e então adapta seu conhecimento geral de programação para seguir a sintaxe e convenções observadas na documentação. Em todos os casos, você prioriza a precisão técnica e a consistência com o estilo de código do BFC-Script."

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

# Função para a interface de chat
def chat_interface(message, history):
    response = rag_response(message)
    return response

# Criar interface Gradio
demo = gr.ChatInterface(
    fn=chat_interface,
    title="BFC-Script Assistant",
    description="Faça perguntas sobre BFC-Script e obtenha respostas baseadas na documentação",
    theme="soft",
    examples=["Como fazer loop em BFC-Script?", 
              "Como trabalhar com arquivos?", 
              "Como mandar um email?",
              "Como calcular a diferença de dias entre duas datas?",
              "Como separar números pares e ímpares em um array?",
              "Como converter temperatura de Fahrenheit para Celsius?"]
)

# Iniciar a interface
if __name__ == "__main__":
    print("Iniciando o BFC-Script Assistant...")
    demo.launch(share=True)  # share=True cria uma URL pública temporária