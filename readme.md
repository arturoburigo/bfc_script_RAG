# BFC Script Framework RAG Assistant

## O que é BFC Script?

O BFC Script é um framework desenvolvido pela [Betha Sistemas](https://www.betha.com.br/) para facilitar a integração de scripts com aplicações. Este framework fornece um ambiente completo que permite o desenvolvimento, compilação e execução de scripts de forma simplificada e eficiente.

## Sobre o Projeto

Este projeto é uma iniciativa acadêmica desenvolvida na SATC (Associação Beneficente da Indústria Carbonífera de Santa Catarina) que visa implementar um assistente de IA baseado em RAG (Retrieval-Augmented Generation) para o BFC Script, auxiliando assim os desenvolvedores da Betha sistemas, economizando tempo e melhorando a eficiência.

![RAG Assistant](https://miro.medium.com/v2/resize:fit:1400/1*J7vyY3EjY46AlduMvr9FbQ.png)

### Principais Características

- **Integração com Editor**: Assistente de IA integrado diretamente no editor de scripts
- **RAG System**: Utiliza toda a documentação existente do BFC Script e fonte de dados como base de conhecimento
- **Geração de Código**: Capacidade de gerar scripts automaticamente baseados em prompts em linguagem natural
- **Contextual**: Compreende o contexto do BFC Script e suas fontes de dados para gerar código relevante

### Como Funciona

O assistente funciona de forma similar à IA do Notion, onde os desenvolvedores podem:

1. Ativar o modo chat através de um comando específico
2. Fazer perguntas ou solicitar geração de código em linguagem natural
3. Receber respostas contextualizadas e código funcional baseado na documentação do BFC Script

## Instalação e Configuração

### Pré-requisitos

- Python 3.9 ou superior
- Poetry (gerenciador de dependências)

### Instalação do Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Configuração do Projeto

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd bfc_script_RAG
```

2. Instale as dependências usando Poetry:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp .env_example .env
# Edite o arquivo .env com suas configurações
```

4. Execute o projeto:
```bash
poetry run python run.py
```

## Documentação

[Seção para adicionar links para documentação detalhada]


