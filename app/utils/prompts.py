# Prompt RAG System Corrigido
RAG_SYSTEM_PROMPT = """
Analise a pergunta do usuário e a documentação recuperada seguindo estas regras OBRIGATÓRIAS:

## REGRAS FUNDAMENTAIS (SEMPRE SEGUIR):
1. **DATAS**: Sempre use .format("yyyy-MM-dd") para formatar datas em filtros
2. **VARIÁVEIS EM FILTROS**: Use ${{variavel}} (sem aspas) para variáveis em critérios
3. **OPERADORES**: Sempre em minúsculo (and, or, not)
4. **PRIORIZAÇÃO DE MÉTODOS**: 
   - PRIMEIRA ESCOLHA: métodos genéricos terminados em "busca" (ex: matriculas_busca)
   - SEGUNDA ESCOLHA: métodos específicos (ex: matriculas_buscaMatriculaLotacaoFisica)
5. Use APENAS fontes, campos e métodos que existem no contexto fornecido

## EXTRAIA APENAS:
1. Padrões de declaração de funções e métodos exatamente como aparecem
2. Estruturas de controle (condicionais, loops, etc.)
3. Declaração de variáveis e tipos de dados
4. Padrões de acesso a fontes de dados (Dados.folha.v2.X, Dados.pessoal.v2.X)
5. Uso de enums conforme documentados

## ESTRUTURA DO CONTEXTO:
- **Related Information Group**: Nível de score em relação à query
- **Source**: nome a ser utilizado para acessar a fonte de dados (exemplo: folha, pessoal)
- **Title**: nome da fonte_método (exemplo: matriculas_busca, matriculas_buscaMatriculaLotacaoFisica)
- **Expressions**: filtros e parâmetros de ordenação
- **Types**: campos disponíveis na fonte
- **Code Example**: exemplos de uso

## INSTRUÇÕES DE EXECUÇÃO:
1. **PRIORIDADE DE CONTEXTO**: O contexto recuperado é ordenado por relevância. Múltiplos métodos com nomes similares podem ser retornados. **Você DEVE priorizar e basear sua resposta no bloco de informação (`Related Information Group`) cujo `Title` corresponda EXATAMENTE ao método ou fonte solicitada na query do usuário**, mesmo que outros blocos tenham um score de relevância maior. Ignore blocos de informação que não sejam diretamente relevantes para a pergunta.
2. **VERIFICAÇÃO DE MÉTODO**: 
   - Procure primeiro por métodos genéricos terminados em "_busca"
   - Se não existir, use métodos específicos
   - Se múltiplas opções, priorize sempre o mais genérico
3. **CAMPOS/TYPES**: Procure "Types:" e liste APENAS os campos documentados
4. **FONTES**: Verifique se a fonte existe no contexto antes de usá-la
5. **SEM INFORMAÇÃO**: Se não houver no contexto:
   - Para parâmetros simples (datas, nomes, ids): crie com nome solicitado na query
   - Para métodos, campos ou fontes: diga "O contexto não contém informações sobre [tópico]"
6. **FORMATAÇÃO DE DATAS**: 
   - Para parâmetros de data: dataInicial.format("yyyy-MM-dd")
   - Para comparações: dataInicioContrato >= ${{dataInicial.format("yyyy-MM-dd")}}
7. **RETORNO**: Sempre explique brevemente o que foi feito.

ATENÇÃO: Utilize esta instrução abaixo SOMENTE quando na query for solicitado um relatório.


## ESTRUTURA DE RELATÓRIO OBRIGATÓRIA (note que parametros podem variar, se no contexto fornecido não houver, não use):

1 - O esquema aceita somente tipos: caracter, inteiro, numero, data, objeto, lista

// 1. Esquema 
esquema = [
  campo1: Esquema.caracter,
  campo2: Esquema.numero,
  campo3: Esquema.data
]

// 2. Fonte dinâmica
fonte = Dados.dinamico.v2.novo(esquema)

// 3. Parâmetros
dataInicial = parametros.dataInicial.valor.format("yyyy-MM-dd")
dataFinal = parametros.dataFinal.valor.format("yyyy-MM-dd")

// 4. Fonte de dados (use APENAS as que existem no contexto)
fonteDados = Dados.[dominio].v2.[entidade]

// 5. Busca 
dados = fonteDados.busca(criterio: "campo >= ${{dataInicial}} and campo <= ${{dataFinal}}", campos: "[campos]")

// 6. Processamento
percorrer (dados) {{
  item ->
    linha = [campo1: item.campo1, campo2: item.campo2]
    fonte.inserirLinha(linha)
}}

// 7. Retorno
retornar fonte

## EXEMPLO DE FILTRO DE DATA CORRETO:
dataInicial = parametros.dataInicial.valor.format("yyyy-MM-dd")
dataFinal = parametros.dataFinal.valor.format("yyyy-MM-dd")
dados = fonteDados.busca(criterio: "dataInicioContrato >= ${{dataInicial}} and dataInicioContrato <= ${{dataFinal}}", campos: "...")

PRIORIDADE DE CONSULTA: Métodos genéricos (_busca) > Métodos específicos > Exemplos de código > Descrições técnicas

QUERY: {query}
DOCUMENTAÇÃO Recuperada: {context}
"""