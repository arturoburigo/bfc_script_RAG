# 📌 Consultas em Fontes Dinâmicas utilizando Critérios, Campos e Parâmetros
---
Aqui iremos abordar o básico referente consultas em fontes dinâmicas.

# 🖥️ Características da Fonte Dinâmica
---
A fonte dinâmica nada mais é do que uma consulta ao banco de dados da entidade selecionada, existem alguns filtros e propriedades que podemos usar:

**🔍 - Critério:** é o filtro de consulta e pode ser utilizado de N maneiras, podemos representa-lo pelo comando WHERE do SQL.

- *Ex: "matricula.id = ${matricula} and competencia = '${competencia}'"*
- *Resumindo: consultar aonde o ID da matrícula seja igual a variável 'matricula' e a competência seja igual a variável 'competencia'*
```
// Parâmetro de entrada 
matricula = parametros.matricula?.selecionados?.valor
competencia = parametros.competencia?.valor

// Filtro para consulta no banco
filtroCriterio = "matricula.id = ${matricula} and competencia = '${competencia}'"

fonteRemuneracoes = Dados.folha.v2.remuneracoes;
fonteRemuneracoes.buscaComEventos(criterio: filtroCriterio).each{ folha -> 
    imprimir folha
}
```

**🖨️ - Campos:** campos consultados no banco de dados, podemos representa-lo pelas colunas das tabelas SQL.

- *Ex: campos: "id, situacao, pessoa(nome), dataInicioContrato"*
- *Resumindo: consultar as colunas ID, situacao, nome do cadastro de pessoa e dataInicioContrato*
```
// Parâmetro de entrada
matricula = parametros.matricula?.selecionados?.valor

// Filtro das Matrículas
filtroMatricula = ""
if(matricula){
  filtroMatricula = "id in (${matricula.join(',')})"
}

fonteMatriculas = Dados.pessoal.v2.matriculas;
fonteMatriculas.busca(campos: "id, situacao, pessoa(nome), dataInicioContrato").each{ item ->
    imprimir item.id
    imprimir item.situacao
    imprimir item.pessoa.nome
    imprimir item.dataInicioContrato
}
```

**🖋️ - Parametros:** parâmetros de consulta, normalmente são os atributos de relação (chaves estrangeiras).
```

```
