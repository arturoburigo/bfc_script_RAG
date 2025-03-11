import json
from sentence_transformers import SentenceTransformer
import faiss
import os
from openai import OpenAI

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

# Teste da busca
query = "Como usar o comando percorrer?"
results = search(query)

for r in results:
    print(f"Documento: {r['document']} - Seção: {r['section']}")
    print(f"Trecho: {r['content']}\n")


client = OpenAI(api_key="OPENAI_API_KEY")

def rag_response(query):
    results = search(query)

    context = "\n".join([r["content"] for r in results])

    prompt = f"""
    Você é um assistente que responde perguntas com base no contexto fornecido. Você ira se basear na linguagem de programacao bfc-script, fornecida no contexto.
    
    Sempre procure por exemplos de codigo, funcoes, e documentacao no contexto fornecido.
    
    As respostas e os codigos de exemplos devem ser bem explicados sempre se baseado no contexto fornecido. Caso nao entenda a pergunta, responda de forma simples e direta.
    
    Baseando-se no seguinte contexto, responda à pergunta:

    Contexto:
    {context}

    Pergunta: {query}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Você é um assistente que responde perguntas com base no contexto fornecido, qualquer pergunta voce primeiramente vai se basear no contexto e depois vai responder a pergunta. Você ira se basear na linguagem de programacao bfc-script, pesquisar por toda a documentacao, funcoes, e exemplos fornecida no contexto."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Teste da resposta gerada
#query = "Como fazer uma requisicao para uma api?"
query = "Como calcular a diferenca de dias entre duas datas?"
print(rag_response(query))
