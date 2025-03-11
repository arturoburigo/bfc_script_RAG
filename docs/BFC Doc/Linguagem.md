### Linguagem


A linguagem possui poucos comandos e algumas similaridades com a linguagem Java, como os operadores (lógico, comparação, atribuição e aritimético), o uso de chaves para circundar blocos, sintaxe case sensitive, etc. Para simplificar os scripts, não é necessário usar ponto e vírgula no final de cada instrução e os comandos foram desenvolvidos no idioma português, para simplificar o seu uso à usuários sem experiência em linguagens de programação.



#### Comandos




    ##### imprimir


Exibe uma mensagem no console.

1. imprimir 'John Doe'





##### percorrer


Permite iterar valores e obter o índice atual da iteração.

1. percorrer(ate:5){
2.     imprimir indice
3. }



O comando disponibiliza uma variável implícita chamada indice que representa o índice corrente da iteração.

1. percorrer(de:3, ate:5){
2.     imprimir indice
3. }



A variável indice pode ser atribuída a uma outra variável com um nome personalizado, permitindo que a mesma seja acessada em diversos níveis do comando percorrer.

1. percorrer(de:3, ate:5){ idPrincipal ->
2.     imprimir idPrincipal
3.     percorrer(de:6, ate:8){ idSecundario ->
4.         imprimir 'ID princial: ' + idPrincipal
5.         imprimir 'ID secundário: ' + idSecundario
6.     }
7. }



É possível também iterar pelos valores de um lista informando ou não o índice inicial e final da iteração

1. numeros = [1,2,3]
2. percorrer(de:1, ate:3, itens: numeros){
3.     imprimir item
4. }
5. // Irá imprimir os números 1, 2 e 3



1. letras = ['A','B','C']
2. percorrer(de:2, ate:3, itens: letras){
3.     imprimir item
4. }
5. // Irá imprimir as letras B e C, ou seja, do índice 2 até o índice 3



* Caso o índice inicial não seja informado irá utilizar como padrão o valor 1 (primeiro item).
* Caso o índice final não seja informado irá utilizar como padrão o índice final da lista (último item).
###### Controle do fluxo de execução


O fluxo de execução de um comando percorrer pode ser alterado utilizando as funções **parar()** e **continuar()**. Este controle é especialmente útil quando se deseja interromper a execução de um comando percorrer devido à um condição específica ou avançar para um próximo item do laço.



###### **parar()**


A função parar interrompe um comando percorrer em determinada condição, e continua a execução do script sem passar pelas repetições seguintes.

O seguinte código irá imprimir os números 1, 2 e a palavra Ok:

1. numeros = [1,2,3,4]
2. percorrer(numeros){
3.   se(item == 3){
4.     parar()
5.   }
6.   imprimir item
7. }
8.
9. //As instruções fora do comando percorrer serão executadas normalmente, somente o comando percorrer
10. //será interrompido e não todo o script
11. imprimir 'Ok'





###### **continuar()**


A função continuar faz com que o comando percorrer passe para a próxima repetição/item. Este função é especialmente útil em situações em que se deseje ignorar o processamento de um item com base em uma condição.

O seguinte código irá imprimir os números 1, 2 e 4 ignorando o número 3:

1. numeros = [1,2,3,4]
2. percorrer(numeros){
3.   se(item == 3){
4.     continuar()
5.   }
6.   imprimir item
7. }





###### Nomeando os comandos percorrer


Em situações onde são utilizados mais de um comando percorrer aninhados e se deseje **_parar_** ou **_continuar_** um percorrer específico, a atribuição de um nome ao comando se faz necessário. Para nomear o comando basta preencher a propriedade **nome** na declaração da instrução:

1. numeros = [1,2,3,4]
2. percorrer(itens: numeros, nome: 'p1'){
3.   imprimir 'p1: ' + item
4.   percorrer(de: 1, ate: 5){
5.     se (indice == 3){
6.       parar 'p1'
7.     }
8.     imprimir 'p2: ' + indice
9.   }
10. }



A saída do script será:

1. p1: 1 // primeiro item da lista de números do percorrer 'p1'
2. p2: 1 // primeiro índice do segundo percorrer
3. p2: 2 // ...
4. p2: 3 // ...
5. p2: 4 // No índice 4 o comando parar 'p1' foi executado interrompendo a execução de todos os comandos percorrer até o 'p1'



A mesma regra se aplica ao comando **_continuar()_** , porém ao invés de interromper a execução do comando percorrer irá avançar para o próximo índice/item.

1. numeros = [1,2,3]
2. percorrer(itens: numeros, nome: 'p1'){
3.   imprimir 'p1: ' + item
4.   percorrer(de: 1, ate: 5, nome: 'p2'){
5.     se (indice == 2){
6.       continuar 'p1'
7.     }
8.     imprimir 'p2: ' + indice
9.   }
10. }



A saída do script será:

1. p1: 1 // primeiro item da lista de números do percorrer 'p1'
2. p2: 1 // primeiro índice do segundo percorrer
3.       // Ao passar pelo segundo ídice o comando continuar 'p1' foi execuado parando a execução do percorrer atual e avançando o item do
4.       // percorrer 'p1' para a próxima iteração, neste caso o número 2
5. p1: 2
6. p2: 1
7. p1: 3
8. p2: 1





##### retornar


Permite submeter dados como retorno de um script.

Conforme podemos observar, a variável valor é submetida como retorno do script utilizando o comando retornar.

1. valor = 10 * 2 * 3
2. retornar valor



No exemplo abaixo, os valores são retornados pelo comando retornar através de um mapa. As chaves valor e nome recebem seus respectivos valores e são submetidas ao comando retornar e serão resgatadas programaticamente através de um java.util.Map.

1. retornar valor:10 * 2 * 3, nome:'David Crosby'





##### se


Permite criar expressões condicionais.

1. se(10 == 10){
2.    imprimir 'verdadeiro'
3. }
4.
5. se(9 <= 20){
6.     imprimir 'verdadeiro'
7. }senao{
8.     imprimir 'falso'
9. }





##### tentar/tratar/finalizar


Às vezes, a execução de uma ação pode acarretar em uma exceção. Quando isto ocorre, é possível que seja realizado um tratamento para que o script continue sua execução realizando alguma outra ação, como por exemplo, notificar outros usuários, tratar alguns retornos conhecidos, tentar realizar a ação novamente, etc.

No bloco _tentar_ devem ser colocadas as ações onde pode ocorrer um erro. Por exemplo, chamar um serviço HTTP, SOAP, escrever em um arquivo, etc.

Dentro do bloco _tratar_ deve ser especificado o código que será executado em caso de erro dentro do bloco tentar. Nele, existe uma variável chamada excecao que é uma representação do erro ocorrido. Ela possui os seguintes atributos:

* _codigo_ \- É um identificador alfanumérico erro para facilitar sua localização nos manuais e documentações
* _mensagem_ \- Uma mensagem passada pela API ou linguagem que representa a descrição do erro ocorrido
* _linha_ \- Linha onde ocorreu o erro
1. tentar {
2.   resultado = Http.servico('https://endereco-nao-existe').GET()
3.   imprimir resultado.codigo()
4. } tratar {
5.    // Ao mandar imprimir o objeto excecao, será impresso o código, mensagem e linha (se existir)
6.    imprimir 'Estou tratando uma exceção: ' + excecao
7. }



Ainda é possível que independentemente de ocorrer uma falha ou não, ao final da execução do método seja executada alguma ação. Para isso, existe também o bloco _finalizar_. Onde tudo o que for definido neste bloco, será executado independentemente de ocorrer um erro ou não.

1. tentar {
2.   resultado = Http.servico('https://endereco-nao-existe').GET()
3.   imprimir resultado.codigo()
4. } tratar {
5.    // Ao mandar imprimir o objeto excecao, será impresso o código, mensagem e linha (se existir)
6.    imprimir 'Estou tratando uma exceção: ' + excecao
7. } finalizar {
8.     imprimir 'O conteúdo deste bloco sempre será executado'
9. }



Algumas observações referentes à este recurso:

* O bloco finalizar sempre é executado
* Dentro do bloco finalizar, a variável _excecao_ já não está disponível
* O comando _suspender_ não é tratado
##### suspender


Permite suspender a execução de um script com uma exceção.


* se(codigo != 10){
*    suspender "O código $codigo é inválido"
* }
##### esperar


O comando esperar permite que a execução de um script entre em modo de pausa por um determinado intervalo tempo.

Este comando se mostra útil quando o acesso a um serviço é limitado por um intervalo de tempo.

1. imprimir Datas.hoje()
2. esperar 2000 //O script irá pausar a execução neste ponto durante 2000 millisegundos
3. imprimir Datas.hoje()



É possível informar o intervalo de tempo utilizando a forma simplificada de tempo/datas da engine:

1. imprimir Datas.hoje()
2. esperar 1.segundo //O script irá pausar a execução neste ponto durante 1 segundo
3. imprimir Datas.hoje()



O tempo máximo de espera permitido por comando é de 60 segundos. Essa função está disponíveis ao usuário final apenas através da **Ferramenta de Scripts**.



##### exportar


Comando utilizado para exportar símbolos declarados no escopo atual. Aceita como parâmetro um mapa com o nome externo e uma referência ao recursos exportado.

1. // exportando uma constante
2. exportar PI_APROXIMADO: 3.1415
3.
4. // exportando múltiplos símbolos
5. exportar(
6. 	nomeExterno: referencia,
7. 	outroNome: outraReferencia
8. )



Este comando está disponível apenas na **Ferramenta de Scripts**.



##### importar


Comando utilizado para importar recursos de um componente. Aceita como parâmetro uma String com o nome do identificador do componente desejado, e retorna um objeto com os recursos importados.

1. log = importar("log")
2. math = importar("calculadora")
3. counter = importar("contador")
4.
5. log.info("Iniciando execução")
6. acum = 0
7.
8. percorrer(ate: 20) {
9.   counter.incrementar()
10.   acum = math.somar(acum, indice)
11.   log.info("Executando operação #$indice")
12. }



Este comando está disponível apenas na **Ferramenta de Scripts**.



#### Listas


Também conhecida como Arrays, podemos trabalhar com listas de maneira bem simplificada.

1. //Instancia uma lista com valores
2. valores = [0, 1, 2, 3, 4]
3.
4. //Instancia uma lista vazia
5. nomes = []
6.
7. //Adiciona um item na lista
8. nomes << 'Chuck Norris'
9.
10. //Itera uma lista
11. percorrer(valores){
12.     imprimir item
13. }
14.



O comando percorrer possui uma variável implícita para obter o valor da iteração chamada **item**.

A variável item e indice podem ser atribuídas à outras variáveis com nomes personalizados utilizando a seguinte sintaxe do comando percorrer:

1. percorrer(valores){ valor ->
2.     imprimir valor
3. }
4.
5. percorrer(valores){ valor, posicao ->
6.     imprimir valor // Equivale a item
7.     imprimir posicao // Equivale a indice
8. }
9.
10. percorrer(valores){ item, posicao ->
11.     imprimir item
12.     percorrer(outros){
13.         imprimir item //Equivale ao item do percorrer principal pois utilizou o mesmo nome da variável implícita
14.     }
15. }



Obtendo e atribuindo valores em posições **específicas** da lista. A primeira posição da lista tem o índice **0 (zero)** , a segunda posição tem o índice **1** , e assim por diante. Os dados são acessados assim: **lista[indice]**

1. //Instancia uma lista com valores
2. nomes = ['Harrison Reid', 'Thomas Sharpe', 'Louie Hill']
3.
4. //nomes[0] contém o valor 'Harrison Reid'
5. //nomes[1] contém o valor 'Thomas Sharpe'
6. //nomes[2] contém o valor 'Louie Hill'
7.
8. //Obtendo o nome da segunda posição da lista:
9. nomeDaSegundaPosicao = nomes[1]





#### Mapas


É possível criar mapas simplificados e acessar seu valores de forma explicita.

1. pessoa = [nome:'João da Silva', idade:25, profissao: 'Contador']
2.
3. imprimir pessoa.nome
4. imprimir pessoa.idade
5. imprimir pessoa.profissao



Observe o exemplo abaixo, usando uma **lista de mapas** :

1. //Declaração da lista. Será composta por um mapa que contém o nome, a idade e a profissão.
2. dadosPessoais = []
3.
4. //Adicionando dados à lista
5. dadosPessoais << [nome:'Luca Ingram', idade:25, profissao: 'Process pipeline drafter']
6. dadosPessoais << [nome:'Jack Young', idade:30, profissao: 'Industrial economist']
7. dadosPessoais << [nome:'Jake Sullivan', idade:31, profissao: 'Gastroenterology nurse']
8.
9. //Imprimindo os dados...
10. percorrer(dadosPessoais) {
11.   imprimir 'Posição: ' + indice + ' -> Dados:' + item
12. }
13.
14. //Temos o resultado:
15. Posição: 0 -> Dados:[nome:Luca Ingram, idade:25, profissao:Process pipeline drafter]
16. Posição: 1 -> Dados:[nome:Jack Young, idade:30, profissao:Industrial economist]
17. Posição: 2 -> Dados:[nome:Jake Sullivan, idade:31, profissao:Gastroenterology nurse]
18.
19. //Agora, vamos alterar última posição da lista com novos dados.
20. //Jake Sullivan trocou de profissão e precisamos atualizar seu dado profissional. Fazemos isso substituindo um mapa por outro:
21. dadosPessoais[2] = [nome:'Jake Sullivan', idade:31, profissao: 'Administrative leader']
22.
23. //Voltamos a imprimir. Resultado:
24. Posição: 0 -> Dados:[nome:Luca Ingram, idade:25, profissao:Process pipeline drafter]
25. Posição: 1 -> Dados:[nome:Jack Young, idade:30, profissao:Industrial economist]
26. Posição: 2 -> Dados:[nome:Jake Sullivan, idade:31, profissao:Administrative leader]
27.
28. //Outro exemplo: Preciso saber a idade do segundo profissional da lista, Jack Young:
29. imprimir dadosPessoais[1].idade
30. //Resultado: 30





#### Intervalos


Intervalos permitem que você crie uma lista de valores sequenciais podendo serem utilizados como listas. A notação .. define um intervalo, do primeiro item até o último. Intervalos definidos com a notação ..< incluem o primeiro valor, mas não o último valor.

1. //Cria um intervalo
2. dias = 1..3
3.
4. //Percorre um intervalo
5. percorrer(dias){
6.     imprimir item
7. }
8.
9. //Percorre um intervalo
10. percorrer(4..7){
11.     imprimir item
12. }
13.
14. //Percorre um intervalo de forma decrescente
15. percorrer(8..7){
16.     imprimir item
17. }
18.
19. //Percorre um intervalo decrescente desconsiderando o último valor
20. percorrer(6..<4){
21.     imprimir item
22. }
23.



O comando percorrer possui uma variável implícita para obter o valor da iteração chamada item.



#### Datas


A linguagem permite trabalhar com datas de forma bem simplificada. Várias funções estão embutidas nos elementos de data facilitando muito o uso, além de tornar as implementações bem intuitivas. O exemplo abaixo demonstra o uso de algumas funções para datas da API padrão e como utilizar estas funções de forma simplificada, além de demonstrar formas nativas para somar datas/horas/etc.

1. //Funções para obter-se uma data/dataHora
2. hoje = Datas.hoje()
3. primeiroDiaDoAno = Datas.data(hoje.ano,1 ,1 )
4. ultimoDiaDoAno = Datas.dataHora(hoje.ano, 12, 31, 23, 59)
5.
6. imprimir Datas.adicionaSegundos(hoje, 10)
7. imprimir hoje + 10.segundos
8.
9. imprimir Datas.adicionaMinutos(hoje, 10)
10. imprimir hoje + 10.minutos
11.
12. imprimir Datas.adicionaHoras(hoje, 10)
13. imprimir hoje + 10.horas
14.
15. imprimir Datas.adicionaDias(hoje, 10)
16. imprimir hoje + 10.dias
17.
18. imprimir Datas.adicionaMeses(hoje, 10)
19. imprimir hoje + 10.meses
20.
21. imprimir hoje + 1.segundo
22. imprimir hoje + 1.minuto
23. imprimir hoje + 1.hora
24. imprimir hoje + 1.dia
25. imprimir hoje + 1.mes
26.
27. imprimir hoje + 10.anos + 9.meses + 8.semanas + 7.dias + 6.horas + 5.minutos + 4.segundos + 3.milesegundos
28.
29. imprimir Datas.ano(hoje)
30. imprimir hoje.ano
31. imprimir Datas.mes(hoje)
32. imprimir hoje.mes
33. imprimir Datas.dia(hoje)
34. imprimir hoje.dia
35. imprimir Datas.hora(hoje)
36. imprimir hoje.hora
37. imprimir Datas.minuto(hoje)
38. imprimir hoje.minuto
39. imprimir Datas.segundo(hoje)
40. imprimir hoje.segundo
41.
42. imprimir Datas.diaSemana(hoje)
43. imprimir hoje.diaSemana
44.
45. imprimir Datas.removeDias(hoje, 10)
46. imprimir hoje - 10.dias
47.
48. imprimir Datas.removeMeses(hoje, 10)
49. imprimir hoje - 10.meses
50.
51. imprimir Datas.extenso(hoje)
52. imprimir hoje.extenso
53.
54. imprimir Datas.nomeDiaSemana(hoje)
55. imprimir hoje.nomeDiaSemana
56.
57. imprimir Datas.nomeMes(hoje)
58. imprimir hoje.nomeMes
59.
60. imprimir Datas.ehData('01/01/2010')
61.
62. imprimir Datas.diferencaAnos(primeiroDiaDoAno, ultimoDiaDoAno)
63. imprimir Datas.diferencaDias(primeiroDiaDoAno, ultimoDiaDoAno)
64. imprimir Datas.diferencaHoras(primeiroDiaDoAno, ultimoDiaDoAno)
65. imprimir Datas.diferencaMeses(primeiroDiaDoAno, ultimoDiaDoAno)
66. imprimir Datas.diferencaMinutos(primeiroDiaDoAno, ultimoDiaDoAno)
67. imprimir Datas.diferencaSegundos(primeiroDiaDoAno, ultimoDiaDoAno)
68.
69. amanha = hoje + 1.dia
70.
71. //Podemos criar intervalos com datas
72. percorrer(hoje..amanha){
73.     imprimir item.extenso
74. }
75.
76. percorrer(hoje+1.semana..<amanha+2.semanas){
77.     imprimir item.extenso
78. }
79.
80. //Podemos obter uma data apartir de uma expressão como esta
81. semanaQueVem = 7.dias.apartirDe.hoje
82.
83. imprimir semanaQueVem + 5.dias



É importante notar que os valores numéricos informados nas funções de data para representar ano, mês, dias, horas e segundos, diferentemente da formatação Brasileira, não devem conter zeros à esquerda:

1. //Correto
2. Datas.data(2017, 8, 5)
3.
4. //Incorreto (Erro de compilação)
5. Datas.data(2017, 08, 05)





#### Valores nulos


Em programação de computadores, null é um valor especial para um ponteiro (ou qualquer outro tipo de referência) que indica que este ponteiro, intencionalmente, não se refere a um objeto (ponteiro nulo) - [Wikipedia](https://pt.wikipedia.org/wiki/Null_\(programa%C3%A7%C3%A3o\)\]\]).

Este recurso se mostra útil para identificar quando um valor não esta disponível, assumindo um valor próprio para este comportamento, o nulo ou vazio.

A palavra reservada `nulo` representa o valor para este comportamento, de modo que no exemplo abaixo estamos dizendo que a variável `valorCusto` é igual a nulo ou em outras palavras, que seu valor é vazio.

1.     valorCusto = nulo
2.



Um script pode receber variáveis com valores nulo, onde em certas ocasiões é necessário checar se o valor da variável é nulo ou não. Podemos realizar as checagens de duas formas:

1.     valorCusto = nulo
2.
3.     // Forma 1
4.     se (valorCusto != nulo){
5.         imprimir ("A variável valorCusto não está nula.")
6.     }
7.
8.     // Forma 2
9.     se (valorCusto){
10.         imprimir ("A variável valorCusto não está nula.")
11.     }
12.
13.     se (!valorCusto){
14.         imprimir ("A variável valorCusto está nula.")
15.     }
16.
17.     se (valorCusto && funcionario.agenciaBancaria){
18.         imprimir ("A variável valorCusto a a agência bancária do funcionário não estão nulas.")
19.     }
20.



O acesso à referências nulas gera erros durante a execução de um script. No exemplo abaixo, suponhamos que a agência bancária do funcionário esteja nula:

1.     nomeFuncionario = funcionario.agenciaBancaria.nome
2.



Ao tentar obter o nome de uma agência bancária nula, recebemos um erro de execução: A propriedade `nome` não é acessível em um elemento nulo. Para evitar este comportamento, podemos utilizar o operador de navegação segura (?):

1.     nomeFuncionario = funcionario.agenciaBancaria?.nome
2.



O operador deve ser utilizado em diversos níveis de uma referência, caso seja apropriado:

1.     nomeFuncionario = funcionario.agenciaBancaria?.municipio?.nome
2.
3.     // valor impresso 'null'
4.     imprimir(nomeFuncionario)
5.



No exemplo acima, caso não utilizassemos o operador (?) no município (municipio?.nome), receberiamos um erro durante a execução, devido ao fato de que a agenciaBancária esta nula. Como resultado final o valor da variável `nomeFuncionario` é nula.

Em algumas ocasiões, gostariamos de considerar um valor padrão onde o resultado seria nulo. Para este propósito utilizamos a expressão ternária (?:), como podemos observar abaixo:

1.     nomeFuncionario = funcionario.agenciaBancaria?.municipio?.nome
2.
3.     imprimir(nomeFuncionario?:'Sem nome')
4.



No exemplo acima, quando o valor da variável `nomeFuncionario` for nulo, o valor retornado será `Sem nome`.

Poderiamos usar esta expressão diretamente, conforme o exemplo abaixo:

1.     nomeFuncionario = funcionario.agenciaBancaria?.municipio?.nome?:'Sem nome'
2.
3.     imprimir(nomeFuncionario)
