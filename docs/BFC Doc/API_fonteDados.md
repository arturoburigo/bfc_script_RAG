## API de Fonte de Dados


O bfc-script disponibiliza uma API para consumo das fonte de dados registradas pelas aplicações no catálogo de dados da Betha Sistemas. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.

Uma fonte de dados é composta por um Ativo, um Tema, e as Operações propriamente ditas. A API de script utiliza a seguinte estrutura para representar estes componentes:

**Dados**.**ativo**._versao_.**tema**.**operacao()**



### Ativo


Um Ativo pode ser considerado como a fonte/origem das informações. É nele que as operações de busca e manipulação de dados serão executadas.



### Tema


Um tema pertence à um Ativo e representa um grupo de informação em comum. Exemplos de possíveis temas do Ativo folha seriam funcionarios, feriados, etc.



### Operações


Operações são funções de busca/manipulação de dados disponibilizadas através de um Tema. Considerando o exemplo do tema funcionário do ativo folha, teriamos como possíveis operações a criação de um funcionário, busca dos registros, cálculo da folha, etc.

As Operações básicas de um Tema são:

* Operação de busca
* Operação de criação
* Operação de atualização
* Operação de exclusão
**A disponibilidade de cada operação depende do ativo e tema utilizado.**



### Operação de busca


A operação de busca padrão conta com os seguintes parâmetros:

* **criterio** : Parâmetro utilizado para filtrar os dados da busca.
1. tema.busca(criterio:"nome = 'Maria' and idade > 18")



* **ordernacao** : Parâmetro utilizado para informar a ordem do resultado da busca. o valor deste parâmetro deve ser preenchido com o nome dos campos separados por virgula seguido da orientação (asc - Ascendente, desc - Descendente).
1. tema.busca(ordenacao:"nome,sobrenome asc, cidade desc")



* **campos** : Parâmetro utilizado para informar quais campos do registro devem estar no resultado da busca.
1. tema.busca(campos:"nome, sobrenome, cidade(nome, uf)")



* **parametros** : Utilizado para informar os valores dos parâmetros da operação. O nome dos parâmetros pode variar conforme ativo, tema e operação utilizada.
1. ativo.telefones.busca(parametros:[codigoFuncionario:15])



* **consolidado** : Utilizado para informar se os valores retornados devem ser consolidados de acordo com o cadastro de contextos compartilhados. Caso seja passado true, será executado uma consulta na fonte de dados para cada entidade e database configurados, ignorando a entidade e database atual.
1. ativo.telefones.busca(consolidado:true)



**Exemplo:**

1. dadosFuncionarios = Dados.dubai.v1.funcionarios
2.
3. percorrer(dadosFuncionarios.busca(ordenacao:"rg desc", campos:"nome, rg, id, dataAdmissao, dataNascimento")){
4.     imprimir "##Funcionario"
5.     imprimir item.dataNascimento
6.     imprimir item
7.
8.     imprimir "##Telefones: "
9.     percorrer(dadosFuncionarios.telefones.busca(parametros:[codigoFuncionario:item.id])){
10.         imprimir item
11.     }
12. }



Para retornar um único item, deve-se utilziar o parâmetro primeiro:true na operação de busca.

1. dadosFuncionarios.busca(ordenacao:"rg desc", campos:"nome, rg, id, dataAdmissao, dataNascimento", primeiro:true)



* **valorPadrao** : Parâmetro utilizado para ativar/desativar o valor padrão dos campos quando nulos. Caso este parâmetro seja _verdadeiro_ os registros das fontes de dados poderão conter propriedades nulas que deverão ser tratadas pelo próprio script.
1. tema.busca(valorPadrao: falso)





### Operação de criação


A operação de criação padrão conta com os seguintes parâmetros:

* **parametros** : Utilizado para informar os valores dos parâmetros da operação. O nome dos parâmetros pode variar conforme ativo, tema e operação utilizada.
* **conteudo** : Dados do registro a ser criado.
1. dadosFuncionarios = Dados.dubai.v1.funcionarios
2.
3. telefone = [
4.   sequencial: 10,
5.   telefone: '488817858',
6.   tipo: 'OUTRO',
7.   tipoNumero: 'CELULAR',
8.   descricao: "Outro Celular"
9. ]
10.
11. telefoneCriado = dadosFuncionarios.telefones.cria(parametros: [codigoFuncionario:12], conteudo: telefone)





### Operação de atualização


A operação de atualização padrão conta com os seguintes parâmetros:

* **parametros** : Utilizado para informar os valores dos parâmetros da operação. O nome dos parâmetros pode variar conforme ativo, tema e operação utilizada.
* **conteudo** : Dados do registro a ser atualizado.
1. dadosFuncionarios = Dados.dubai.v1.funcionarios
2.
3. telefone = [
4.   telefone: '488817858'
5. ]
6.
7. telefoneAlterado = dadosFuncionarios.telefones.atualiza(parametros: [codigoFuncionario: 12, codigoTelefone: 15], conteudo: telefone)





### Operação de exclusão


A operação de exclusão padrão conta com os seguintes parâmetros:

* **parametros** : Utilizado para informar os valores dos parâmetros da operação. O nome dos parâmetros pode variar conforme ativo, tema e operação utilizada.
1. dadosFuncionarios.telefones.exclui(parametros: [codigoFuncionario: 12, codigoTelefone: 15])


