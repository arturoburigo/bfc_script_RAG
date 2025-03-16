import json
from sentence_transformers import SentenceTransformer
import faiss
import os
from openai import OpenAI
import gradio as gr

# Configurar o ambiente para evitar warning do tokenizer
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def search(query, top_k=5):
    # Carregar o modelo de embeddings e FAISS
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
    index = faiss.read_index("index/faiss_index.bin")

    # Criar o embedding da pergunta
    query_embedding = model.encode(query).astype("float32").reshape(1, -1)

    # Buscar os k resultados mais próximos
    distances, indices = index.search(query_embedding, top_k)

    # Carregar os chunks para retornar os textos
    with open("docs/chunks_embedded/documentation_chunks_with_embeddings.json", "r", encoding="utf-8") as file:
        document_chunks = json.load(file)

    # Retornar os chunks mais relevantes
    results = [document_chunks[idx] for idx in indices[0]]
    return results

client = OpenAI(api_key="")

def rag_response(query):
    results = search(query)
    context = "\n".join([r["content"] for r in results])

    prompt = f"""
    Consulte exclusivamente a documentação do BFC-Script fornecida abaixo para responder à pergunta do usuário.

    INSTRUÇÕES ESPECÍFICAS:
    1. Analise cuidadosamente toda a documentação fornecida no contexto
    2. Identifique seções relevantes, funções, exemplos de código e explicações técnicas
    3. Cite diretamente trechos relevantes da documentação ao responder
    4. Forneça exemplos de código específicos encontrados na documentação
    5. Se a documentação não contiver informações para responder completamente, indique claramente o que está faltando
    6. funções não utilizam acentos

    DOCUMENTAÇÃO (contexto recuperado):
    {context}

    PERGUNTA DO USUÁRIO: {query}

    Responda de forma detalhada usando APENAS as informações encontradas na documentação acima.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Você é um especialista em BFC-Script e sua função é responder perguntas consultando exclusivamente a documentação oficial fornecida no contexto. Priorize sempre encontrar e citar informações técnicas precisas da documentação, incluindo funções, sintaxe, exemplos de código e melhores práticas. Quando não encontrar a informação exata na documentação, indique claramente esta limitação e forneça a resposta mais próxima baseada apenas no material disponível. Nunca invente informações ou exemplos que não estejam presentes no contexto fornecido."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

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
              "Como calcular a diferença de dias entre duas datas?"]
)

# Iniciar a interface
if __name__ == "__main__":
    demo.launch(share=True)  # share=True cria uma URL pública temporária