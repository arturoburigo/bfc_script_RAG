## API de Scripts


O bfc-script disponibiliza uma API que provê suporte à chamada entre scripts. Esta funcionalidade permite que uma lógica comum seja reutilizada por diversos scripts e está disponivel ao usuário final apenas através da **Ferramenta de Scripts**.

Para que seja possível invocar um script através da API é necessário configurar o identificador único do script à ser executado.



### Executando scripts


A execução de um script é realizada utilizando a palavra reservada **Scripts** , seguida do identificador e método de execução:

_Scripts_.**identificador**._executar(parametros)_

1. Scripts.calculos.somar.executar(parametros)
2. Scripts.dubai.consultas.funcionarios.executar(parametros)





#### identificador


Identificador único do script.



#### executar(parametros)


Função responsável pela execução do script.

1. parametros = [ p1 : 100, p2 : 200]
2.
3. Scripts.somar.executar(parametros)





#### variaveis(Map)


Função responsável por enviar variáveis para outro script sem a necessidade de ter parâmetros no script que recebe essas variáveis.

O script de exemplo tem dois parâmetros do tipo arquivo, com os nomes arquivo e arquivo2, esses arquivos são enviados para o segundo script identificado por scriptb:

1. arquivos = [arquivo1: parametros.arquivo.valor, arquivo2: parametros.arquivo2.valor, val3:'teste teste 123']
2.
3. Scripts.scriptb.variaveis(arquivos).executar();



No script que recebe as variáveis, os valores estão disponíveis da seguinte maneira:

1. Resultado.arquivo(variaveis.arquivo1)
2. Resultado.arquivo(variaveis.arquivo2)
3.
4. imprimir variaveis.val3



O scriptb não precisa ter nenhum parâmetro para receber as variáveis e qualquer tipo pode ser passado por variaveis().

Outro exemplo seria um script principal que gera um arquivo csv com valores obtidos em execuções de outros três scripts:

Script principal:

1. //Escrita
2. csv = Arquivo.novo('teste.csv', 'csv', [delimitador:';'])
3.
4. csv.escrever('ID')
5. csv.escrever('NOME')
6. csv.escrever('SALARIO')
7.
8. Scripts.geraarquivo.funcionarios1.variaveis(arquivo:csv).executar()
9.
10.
11. geraArquivo = {col1, col2, col3 ->
12.   csv.novaLinha()
13.
14.   csv.escrever(col1)
15.   csv.escrever(col2)
16.   csv.escrever(col3)
17. }
18.
19. Scripts.geraarquivo.funcionarios2.variaveis(retorno:geraArquivo).executar()
20.
21. retorno = Scripts.componente3.executar()
22.
23. imprimir retorno.variaveis.geraArquivo2();  // imprime o valor teste2 no log de execução do script principal
24.
25. retorno.variaveis.geraArquivo(csv)
26.
27. Resultado.arquivo(csv)



Script com o identificador geraarquivo.funcionarios1:

1. csv = variaveis.arquivo
2. criterio = Criterio.onde('nome').igual('Paulo Henrique')
3.
4. dadosFuncionarios = Dados.dubai.v1.funcionarios
5.
6. percorrer(dadosFuncionarios.busca(campos:"nome, id, salario", criterio: criterio)){
7.     csv.novaLinha()
8.   	csv.escrever(item.id)
9. 	csv.escrever(item.nome)
10. 	csv.escrever(item.salario)
11. }



Script com o identificador geraarquivo.funcionarios2:

1. dadosFuncionarios = Dados.dubai.v1.funcionarios
2. criterio = Criterio.onde('nome').igual('Wellington')
3.
4. id = '';
5. nome = '';
6. salario = '';
7.
8. percorrer(dadosFuncionarios.busca(campos:"nome, id, salario", criterio: criterio)){
9.   	id = item.id
10. 	nome = item.nome
11. 	salario = item.salario
12. }
13.
14. variaveis.retorno(id, nome, salario)



Script com o identificador componente3:

1. geraArquivo2 = {
2.   retornar "teste2"
3. }
4.
5. geraArquivo = {csv ->
6.   csv.novaLinha()
7.
8.   csv.escrever('Valor 31')
9.   csv.escrever('Valor 32')
10.   csv.escrever('Valor 33')
11.
12. }



Ao executar o script principal o arquivo csv é gerado.



### Retorno dos scripts


A execução de um script através da API sempre irá produzir um resultado, Este resultado é representado da seguinte forma:

1. resultado = Scripts.somar.executar([ p1 : 100, p2 : 200])



As opções disponíveis em um resultado são:



#### valor


Recupera o valor retornado pelo script executado.

1. imprimir resultado.valor()





#### vazio


Verifica se o script invocado retornou algum resultado.

1. resultado = Scripts.somar.executar([ p1 : 100, p2 : 200])
2.
3. se(resultado.vazio){
4.    imprimir 'Nenhum resultado foi retornado pelo script somar'
5. }





#### variavel(nome)


Recupera o valor de uma variável declarada no script invocado.

1. resultado = Scripts.somar.executar([ p1 : 100, p2 : 200])
2. imprimir resultado.variavel('log') //Realizando soma



Note que a variável _log_ foi declarada no conteúdo do script somar:

1. log = "Realizando soma"
2. retornar parametros.p1.valor + parametros.p2.valor





#### retornar


O retorno de um script é realizado utilizando o comando _**retornar**_:

1. retornar 'Retornando uma mensagem'



1. ret = [valor: 1, mensagem: 'Retornando um mapa']
2. retornar ret





### Executando scripts em lote


A execução de scripts em lote pode ser realizada através da criação de um script centralizador. Este script será responsável por orquestrar a execução dos demais scripts obedecendo a ordem cronológica de execução. Exemplo:

1. resultado = Scripts.somar.executar([ p1 : 100, p2 : 200])
2.
3. Scripts.enviarEmailSoma.executar([valor: resultado.valor])
4.
5. Scripts.enviarSmsSoma.executar([valor: resultado.valor])





### Componentes


**Quando utilizar componentes?**

Quando para resolver uma dada situação seja mais indicado fragmentar o script, seja por uma questão de organização ou de praticidade em ter funções com finalidades específicas devidamente separadas.

Por exemplo: Consideremos que um dado Tribunal de Contas exige bimestralmente a informação de todos os fornecedores de uma entidade via Web Service. Neste caso, poderiam existir os seguintes recursos:

* Script principal, onde recebe os parâmetros para gerar as informações e enviá-las ao Tribunal de Contas;
* Componente para identificar todos os fornecedores passíveis de envio ao Tribunal de Contas;
* Componente para gerar o arquivo a ser enviado ao Tribunal de Contas;
* Componente para enviar o arquivo ao Tribunal de Contas via Web Service;
**Por que utilizar componentes?**

São algumas vantagens na utilização dos componentes:

* Melhor performance na execução do script: Por conta do recurso Exportar e Importar e também porque os componentes são executados exclusivamente a partir de um script que o invoca;
* Organização de código: Por meio da fragmentação de código orientada ao objetivo fim do componente;
* Privacidade de variáveis e closures (funções): Num componente é possível declarar variáveis e closures localmente, e então escolher quais serão expostos para quando o componente for importado por outro script;
* Reutilização de código: Pode ser utilizado o mesmo componente em mais de um script;
#### Exemplos de utilização:


**Exemplo 1:** Este exemplo demonstra um componente que abstrai uma API REST.

Segue o código de um **componente** cujo identificador foi denominado _restapi_ e que será chamado pelo **script pai** :

1. // variável local e privada ao componente
2. api = Http.servico('https://jsonplaceholder.typicode.com')
3.
4. // closure privada ao componente
5. extractContent = { response ->
6.   conteudo = -1
7.
8.   se (response.sucesso() && response.contemResultado()) {
9.     conteudo = response.conteudo()
10.   }
11.
12.   retornar conteudo
13. }
14.
15. getPost = { id ->
16.   extractContent(api.caminho("posts/$id").GET())
17. }
18.
19. getComments = { idPost ->
20.   extractContent(api.caminho("posts/$idPost/comments").GET())
21. }
22.
23. Scripts.exportar(
24.   buscarPublicacao: getPost,
25.   buscarComentarios: getComments
26. )



O comando **exportar** é utilizado para definir quais recursos serão expostos pelo componente. Repare que as declarações que não foram exportadas permanecem privadas ao componente, permitindo assim uma modelagem mais robusta de funcionalidades comuns a vários scripts.

Segue o código do **script pai** que chama o componente acima:

1. api = Scripts.restapi.importar()
2.
3. publicacao = api.buscarPublicacao(1)
4.
5. se (publicacao != -1) {
6.   imprimir "Publicacao: " + publicacao
7. }
8.
9. comentarios = api.buscarComentarios(1)
10.
11. se (comentarios != -1) {
12.   imprimir "Comentarios: " + comentarios
13. }



A importação dos recursos de um componente é realizada utilizando a palavra reservada **Scripts** , seguido do identificador e o método de importação. O resultado é atribuído a uma variável, a partir da qual os recursos importados podem ser acessados.

Alternativamente, pode-se utilizar a palavra reservada **importar**, passando como parâmetro o identificador do componente, no caso, fica assim:

1. api = importar "restapi"



**Exemplo 2:** Este exemplo trata de múltiplos componentes para um único Script Pai:

Existem 3 componentes:

* Que simula uma calculadora;
* Que executa um contador;
* Que gera um log;
_Componente 1: identificador ped.calculadora_

1. add = { p1, p2 ->
2.   p1 + p2
3. }
4.
5. sub = { p1, p2 ->
6.   p1 - p2
7. }
8.
9. mul = { p1, p2 ->
10.   p1 * p2
11. }
12.
13. div = { p1, p2 ->
14.   p1 / p2
15. }
16.
17. exportar(
18.   somar: add,
19.   subtrair: sub,
20.   multiplicar: mul,
21.   dividir: div
22. )



_Componente 2: identificador ped.contador_

1. current = 0
2.
3. inc = { amount = 1 -> current += amount }
4. dec = { amount = 1 -> current -= amount }
5. reset = { current = 0 }
6. get = { current }
7.
8. Scripts.exportar(
9.         incrementar: { inc(1) },
10.         incrementarEm: inc,
11.         decrementar: { dec(1) },
12.         decrementarEm: dec,
13.         zerar: reset,
14.         atual: get
15. )



_Componente 3: identificador ped.log_

1. logFile = Arquivo.novo('log.txt')
2.
3. logInfo = { text ->
4.   logFile.escrever("INFO: $text")
5.   logFile.novaLinha()
6. }
7.
8. logError = { text ->
9.   logFile.escrever("ERROR: $text")
10.   logFile.novaLinha()
11. }
12.
13. commit = {
14.   imprimir "Adicionado log no resultado"
15.   Resultado.arquivo(logFile, 'log.txt')
16. }
17.
18. exportar(
19.   info: logInfo,
20.   erro: logError,
21.   salvar: commit
22. )



_Finalmente, o**Script Pai** :_

1. calculadora = importar "ped.calculadora"
2. contador = importar "ped.contador"
3.
4. imprimir "2 + 2 = ${calculadora.somar(2, 2)}"
5. imprimir "2 - 2 = ${calculadora.subtrair(2, 2)}"
6. imprimir "2 * 2 = ${calculadora.multiplicar(2, 2)}"
7. imprimir "2 / 2 = ${calculadora.dividir(2, 2)}"
8.
9. imprimir "Inicio: " + contador.atual()
10. imprimir "+1: " + contador.incrementar()
11. imprimir "+10: " + contador.incrementarEm(calculadora.somar(5, 5))
12. imprimir "Zerado: " + contador.zerar()
13.
14. //------------------------------------------------
15. log = importar "ped.log"
16.
17. log.info("Iniciando execução")
18.
19. percorrer(ate: 5) {
20.   log.info("Executando passo #$indice")
21. }
22.
23. log.erro("Erro na conversão dos valores")
24. log.salvar()

