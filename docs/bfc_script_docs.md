
## Introdução


O bfc-script é um framework que possibilita a integração de scripts com aplicações. O framework oferece um ambiente de desenvolvimento, compilação e execução de scripts, bem como uma linguagem amigável para usuários não técnicos e APIs utilitárias.



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
4.





### API Padrão


A engine padrão disponibiliza uma API com várias funções utilitárias para manipulação de datas, caracteres e números. As funções são separadas por classes e são invocadas como métodos. Alguns métodos para manipulação de datas e caracteres podem ser utilizados de maneira direta, invocando o método apartir do próprio elemento, não necessitando a invocação através da classe. Durante a explanação das funções, serão sinalizados, as que possuem alternativa de uso direta. Esta sessão abordará detalhes de cada função da API padrão. Essas funções estarão disponíveis ao usuário final, e serão absorvidas plenamente conforme a utilização. Sinta-se a vontade para pular esta sessão neste primeiro momento.



#### Caracteres




##### capitaliza


Por meio desta função é possível colocar a primeira letra de cada palavra de um texto em maiúsculo e as outras letras para minúsculo.

1. Caracteres.capitaliza(texto)



_Alternativa_

1. texto.capitaliza





##### direita


Obtem uma quantidade específica de caracteres iniciados da direita para esquerda.

1. Caracteres.direita(texto, quantidade)



_Alternativa_

1. texto.direita(quantidade)





##### equivalente


Verifica se uma expressão esta contida em um texto. Mais sobre [expressões regulares](http://guia-er.sourceforge.net/metacaracteres.html#2)

1. Caracteres.equivalente(texto, expressao)



_Alternativa_

1. texto.equivalente(expressao)





##### esquerda


Obtem uma quantidade específica de caracteres iniciados da esquerda para direita.

1. Caracteres.esquerda(texto, quantidade)



_Alternativa_

1. texto.esquerda(quantidade)





##### maisculo


Converte todos os caracteres de um texto em maiúsculo.

1. Caracteres.maiusculo(texto)



_Alternativa_

1. texto.maiusculo





##### minusculo


Converte todos os caracteres de um texto em minusculo.

1. Caracteres.minusculo(texto)



_Alternativa_

1. texto.minusculo





##### posicao


Obtem a posição onde um caracter se encontra em uma texto.

1. Caracteres.posicao(texto, expressao, posicaoInicio)



_Alternativa_

1. texto.posicao(expressao, posicaoInicio)





##### posicao


Obtem a posição inicial de uma [expressão regular](http://guia-er.sourceforge.net/metacaracteres.html#2) em uma texto.

1. Caracteres.posicao(texto, expressao regular, posicaoInicio)



_Alternativa_

1. texto.posicao(expressao regular, posicaoInicio)





##### posicaoFinal


Obtem a posição final de uma [expressão regular](http://guia-er.sourceforge.net/metacaracteres.html#2) em uma texto.

1. Caracteres.posicaoFinal(texto, expressao regular, posicaoInicio)



_Alternativa_

1. texto.posicaoFinal(expressao regular, posicaoInicio)





##### removeEspacos


Remover o excesso de espaços de um texto.

1. Caracteres.removeEspacos(texto)



_Alternativa_

1. texto.removeEspacos





##### removeEspacosDireita


Remove o excesso de espaços de um texto à esquerda.

1. Caracteres.removeEspacosDireita(texto)



_Alternativa_

1. texto.removeEspacosDireita





##### removeEspacosEsquerda


Remove o excesso de espaços de um texto à direita.

1. Caracteres.removeEspacosEsquerda(texto)



_Alternativa_

1. texto.removeEspacosEsquerda





##### repetir


Repete um texto especificado de acordo com uma quantidade definida.

1. Caracteres.repetir(texto, repeticao)



_Alternativa_

1. texto.repetir(repeticao)



Um exemplo prático de utilização é para completar os caracteres de um campo de um leiaute bancário. Por exemplo, no leiaute tem o campo nome com 100 caracteres, porém, se o nome não tiver 100 caracteres, então, o campo deve ser preenchido com espaços em branco à direita.

Segue um exemplo de preenchimento de um campo do tipo String:

1. //Script convencional
2. arquivo = Arquivo.novo('arq.txt', 'txt', [encoding: 'iso-8859-1']);
3.
4. dadosFuncionarios = Dados.dubai.v1.funcionarios
5.
6. percorrer(dadosFuncionarios.busca()){
7.   arquivo.escrever(item.nome)
8.   arquivo.escrever(Caracteres.repetir(" ", 100 - item.nome.tamanho()))
9.   arquivo.escrever(item.rg)
10.   arquivo.escrever(Caracteres.repetir(" ", 10 - item.rg.tamanho()))
11.   arquivo.escrever('ABCDE')
12.   arquivo.novaLinha()
13. }
14.
15. Resultado.arquivo(arquivo)
16.
17.
18. //Script otimizado
19. preencherComEspacos = { texto, tamanho ->
20.    texto + Caracteres.repetir(" ", tamanho - texto.tamanho())
21. }
22.
23. arquivo = Arquivo.novo('arq.txt', 'txt', [encoding: 'iso-8859-1']);
24.
25. dadosFuncionarios = Dados.dubai.v1.funcionarios
26.
27. percorrer(dadosFuncionarios.busca()){
28.   arquivo.escrever(preencherComEspacos(item.nome,100))
29.   arquivo.escrever(preencherComEspacos(item.rg, 10))
30.   arquivo.escrever('ABCDE')
31.   arquivo.novaLinha()
32. }
33.
34. Resultado.arquivo(arquivo)



Segue um outro exemplo, utilizando o mesmo leiaute bancário, de preenchimento com zeros à esquerda para um determinado campo do tipo numérico:

1. //Função para preencher os espaços do número
2. formatarNumero = { numero, tamanho ->
3.
4.   numeroTxt = "$item.id"
5.
6.   //Observe que o preenchimento do campo está à esquerda, no caso, antes do Código.
7.   Caracteres.repetir('X', tamanho - numeroTxt.tamanho()) + numeroTxt
8.
9.   //Observe que o preenchimento do campo está à direita, no caso, depois do Código.
10.   // numeroTxt + Caracteres.repetir('X', tamanho - numeroTxt.tamanho())
11. }
12.
13. arquivo = Arquivo.novo('arq.txt', 'txt', [encoding: 'iso-8859-1']);
14.
15. dadosFuncionarios = Dados.dubai.v1.funcionarios
16.
17. percorrer(dadosFuncionarios.busca()){
18.   idString = "$item.id"
19.   //Aqui os números são preenchidos com os caracteres desejados sem utilizar a função formatarNumero()
20.   imprimir item.nome + Caracteres.repetir(" ", 100 - item.nome.tamanho()) +
21.     Caracteres.repetir("X", 10 - idString.tamanho()) + item.id + '-ABCDE'
22.
23.
24.   arquivo.escrever(item.nome)
25.   arquivo.escrever(Caracteres.repetir(" ", 100 - item.nome.tamanho()))
26.   //Aqui é utilizado o recurso da função de preenchimento dos espaços - formatarNumero(a,b)
27.   arquivo.escrever(formatarNumero(item.id,10))
28.   arquivo.escrever('-ABCDE')
29.   arquivo.novaLinha()
30. }
31.
32. Resultado.arquivo(arquivo)





##### sobrepor


Sobrepõe um texto em outro em uma determinada posição e com uma quantidade especifica de caracteres.

1. Caracteres.sobrepor(texto, posicaoInicial, quantidadeSobrepor, textoSobrepor)



_Alternativa_

1. texto.sobrepor(posicaoInicial, quantidadeSobrepor, textoSobrepor)





##### substituir


Substitui as ocorrências de uma expressão localizada em um texto por outra expressão.

1. Caracteres.substituir(texto, textoLocalizar, textoSubstituir)



_Alternativa_

1. texto.substituir(textoLocalizar, textoSubstituir)





##### subTexto


Obtém um número específico de caracteres de uma posição especifica de um texto.

1. Caracteres.subTexto(texto, inicio, tamanho)



_Alternativa_

1. texto.subTexto(inicio, tamanho)





##### tamanho


Obtem o tamanho de um texto.

1. Caracteres.tamanho(texto)



_Alternativa_

1. texto.tamanho





##### vazio


Verifica se uma palavra esta vazia.

1. Caracteres.vazio(valor)



_Alternativa_

1. valor.vazio





##### dividir


Esta função divide um texto de acordo com a expressão regular informada.

1. Caracteres.dividir("boa|tarde", ~/\|/) //[boa, tarde]



_Alternativa_

1. valor.dividir(~/\|/)





#### Expressões regulares


A API de Caracteres suporta o uso de [expressões regulares](http://aurelio.net/regex/guia/) para realizar diversas operações baseadas em um padrão em textos.

1. Caracteres.expressao(texto, expressao)
2. //ou
3. "texto".expressao(expressao)



As expressões são representadas na linguagem de scripts utilizando o seguinte padrão: **~/expressão/**

Exemplo:

1. expNumeros = ~/\d+/
2. expLetras = ~/(?i)[a-z]/
3.
4. Caracteres.expressao("1235", ~/[a-z]/)
5. "1235".expressao(~/[a-z]/)



As operações disponíveis em um expressão são:



##### equivalente()


Verifica se o texto é totalmente equivalente a expressão.

1. //verdadeiro pois todo o texto equivale a expressão regular informada
2. Caracteres.expressao("123", ~/\d+/).equivalente()
3.
4. //falso pois apesar do texto conter números o valor não é totalmente equivalente à expressão.
5. "123AB".expressao(~/\d+/).equivalente()





##### totalGrupos()


Retorna o total de [grupos](http://aurelio.net/regex/guia/grupo.html#2_4_3) da expressão regular.

1. expBoasVindas = "boa-tarde".expressao(~/boa-(tarde|noite)/)
2. imprimir expBoasVindas.totalGrupos() // 1





##### dividir()


Esta função divide um texto de acordo com a expressão regular informada retornando uma lista com os valores separados.

1. partes = "boa|tarde".expressao(~/\|/).dividir()
2. percorrer(partes){
3.    imprimir item
4. }
5.
6. //Saída:
7. //boa
8. //tarde





##### substituirPor(valor)


Realiza a substituição de todos os valores da expressão encontrados no texto pelo valor informado no parâmetro.

1. valor = "A1B2".expressao(~/[0-9]+/).substituirPor("*")
2. imprimir valor // A*B*





##### substituirPrimeiroPor(valor)


Realiza a substituição do primeiro valor da expressão encontrado no texto pelo valor informado no parâmetro.

1. valor = "A1B2".expressao(~/[0-9]+/).substituirPrimeiroPor("*")
2. imprimir valor // A*B2





##### encontrouPadrao()


Indica se o padrão da expressão foi encontrado no texto.

1. encontrouAlgo = "1235A".expressao(~/[0-9]+/).encontrouPadrao()
2. imprimir encontrouAlgo // true





##### concatenarValoresEncontrados()


Retorna todos os valores encontrados no texto pela expressão concatenados.

1. imprimir "B30th45".expressao(~/[0-9]+/).concatenarValoresEncontrados() // 3045





##### concatenarValoresEncontrados(separador)


Retorna todos os valores encontrados no texto pela expressão concatenados com o separador informado no parâmetro.

1. imprimir "B30th45".expressao(~/[0-9]+/).concatenarValoresEncontrados(",") // 30,45





##### Caractere de escape


A seguinte linha de código provoca um erro de sintaxe:

1. imprimir "These "names" sets apply to this country: American"
2.
3. //Resultado:
4. Há um erro de sintaxe. (1:18)



Isto corre pois o compilador interpreta os caracteres de aspas duplas dentro da cadeia de caracteres como delimitadores. Para eliminar o problema emprega-se o caractere de escape \ (barra contrária, ou backslash) antes das aspas:

1. imprimir "These \"names\" sets apply to this country: American"
2.
3. //Resultado:
4. These "names" sets apply to this country: American



Veja este caso:

1. imprimir "C:\Temp\PDF\Leitura"
2.
3. //Resultado:
4. Há um erro de sintaxe. (1:13)



Isso ocorre porque o compilador interpreta as barras contrárias como caracteres de escape. Mas não é o que queremos. Queremos imprimir um caminho de pastas usando, literalmente, as barras contrárias:

1. //Adicione mais um caractere de escape em cada barra
2. imprimir "C:\\Temp\\PDF\\Leitura"
3.
4. //Resultado:
5. C:\Temp\PDF\Leitura



Dentro das expressões regulares, é necessário inserir, no caractere de escape, um **til** entre as barras contrárias:

1. ~\caractere de escape aqui~\



Veja abaixo um exemplo usando caractere de escape. Repare que, dentro do último comando "expressao", há uma solcitiação de substituir uma barra por uma string vazia.

1. //O código abaixo remove caracteres especiais
2. caracteres = "Caráctéres\$  Es\$,pêc-i_a*i/s. fôrám removídós\$: !@#¨&*^´()\n"
3.
4. caracteres.expressao(~/[à|á|ã]/).substituirPor("a")
5.           .expressao(~/[Á|Ã|À]/).substituirPor("A")
6.           .expressao(~/[é|ê]/).substituirPor("e")
7.           .expressao(~/[É|É]/).substituirPor("E")
8.           .expressao(~/[É|É]/).substituirPor("")
9.           .expressao(~/[í]/).substituirPor("i")
10.           .expressao(~/[Í]/).substituirPor("I")
11.           .expressao(~/[õ|ó|ô]/).substituirPor("o")
12.           .expressao(~/[Õ|Ó|Ô]/).substituirPor("O")
13.           .expressao(~/[ü|ú]/).substituirPor("u")
14.           .expressao(~/[Ú|Ü]/).substituirPor("U")
15.           .expressao(~/[ç]/).substituirPor("c")
16.           .expressao(~/[Ç]/).substituirPor("C")
17.           .expressao(~/  /).substituirPor(" ")
18.           .expressao(~/[,|~\\n~\|~\/~\|-|_|*|.|!|@|#|$|%|¨|&|*|^|´|.|~|:|;|)|(|%|~\-|]/).substituirPor("")
19.
20. //Resultado:
21. Caracteres Especiais foram removidos





#### Múltiplas ocorrências e grupos


Uma expressão pode encontrar diversas ocorrências de um padrão em um texto. Estes valores podem ser organizados por grupos ou simplesmente por valor localizado.

Percorrendo todas as ocorrências encontradas em um texto:

1. achaNumeros = "B30th45".expressao(~/[0-9]+/)
2. percorrer(achaNumeros){
3.   imprimir item.valorEncontrado()
4. }
5. //Saída:
6. // 30
7. // 45





##### posicaoInicial()


Retorna a posição inicial do texto que coincida com a expressão localizada. Caso o padrão não seja encontrado retorna -1.



##### posicaoFinal()


Retorna a posição final do texto que coincida com a expressão localizada. Caso o padrão não seja encontrado retorna -1.

1. achaNumeros = "B30th45".expressao(~/[0-9]+/)
2. percorrer(achaNumeros){
3.   valor = item.valorEncontrado()
4.   inicio = item.posicaoInicial()
5.   fim = item.posicaoFinal()
6.   imprimir "O valor $valor inicia na posição $inicio e termina na posição $fim"
7. }
8.
9. // Saída:
10. //O valor 30 inicia na posição 1 e termina na posição 3
11. //O valor 45 inicia na posição 5 e termina na posição 7





##### posicaoFinal()


Retorna a posição final do texto que coincida totalmente com a expressão utilizada. Caso não encontrado retorna -1.

1. imprimir "B30th".expressao(~/\d+/).posicaoFinal() //3





##### valoresGrupos()


Retorna uma lista com todos os valores encontrados pelos grupos especificados na expressão.

1. exp = "boa-tarde".expressao(~/boa-(tarde|noite)/)
2. percorrer(exp){
3.   imprimir item.valoresGrupos() // [tarde]
4. }





##### valorGrupo(indice)


Retorna o valor do grupo encontrado conforme índice e expressão.

1. exp = "bom-dia".expressao(~/(boa|bom)-(dia|tarde|noite)/)
2. percorrer(exp){
3.   imprimir item.valorGrupo(0) //bom
4.   imprimir item.valorGrupo(1) //dia
5. }
6.
7. exp2 = "boa-tarde".expressao(~/(boa|bom)-(dia|tarde|noite)/)
8. percorrer(exp2){
9.   imprimir item.valorGrupo(0) //boa
10.   imprimir item.valorGrupo(1) //tarde
11. }





##### valorEncontrado()


Retorna o conteúdo do texto encontrado de acordo com a expressão/grupo utilizado.

1. exp = "Muito boa-tarde respeitável público.. Ops, acho que seria boa-noite!".expressao(~/(boa|bom)-(dia|tarde|noite)/)
2. percorrer(exp){
3.     imprimir item.valorEncontrado()
4. }
5.
6. //Saída:
7. // boa-tarde
8. // boa-noite





##### concatenarValoresGrupos()


Retorna os valores dos grupos da expressão concatenados.

1. exp = "boa-Tarde".expressao(~/(boa|bom)-(dia|(t|T)arde|noite)/)
2. percorrer(exp){
3.   imprimir item.concatenarValoresGrupos() // boaTardeT
4. }





##### concatenarValoresGrupos(separador)


Retorna os valores dos grupos da expressão concatenados com o separador informado no parâmetro.

1. exp = "boa-Tarde".expressao(~/(boa|bom)-(dia|(t|T)arde|noite)/)
2. percorrer(exp){
3.   imprimir item.concatenarValoresGrupos("-") // boa-Tarde-T
4. }





#### Datas




##### adicionaDias


Adiciona uma quantidade especificada de dias à uma data.

1. Datas.adicionaDias(data, quantidadeDias)



_Alternativa_

1. data.adicionaDias(quantidadeDias)





##### adicionaHoras


Adiciona uma quantidade especificada de horas em uma data/hora.

1. Datas.adicionaHoras(data, quantidadeHoras)





##### adicionaMeses


Adiciona uma quantidade especificada de meses em uma data. Caso o dia da data especificadanão seja um dia válido para o mês resultante, Ex: 31/10/2011, adiciona 1 mês, valor inválido para nova data 31/11/2011, a diferença de dias será acrescentada na nova data, Ex:31/10/2011, adiciona 1 mês fica 01/12/2011.

1. Datas.adicionaMeses(data, quantidadeMeses)



_Alternativa_

1. data.adicionaMeses(quantidadeMeses)





##### adicionaMinutos


Adiciona uma quantidade especificada de minutos em uma data/hora.

1. Datas.adicionaMinutos(data, quantidadeMinutos)



_Alternativa_

1. data.adicionaMinutos(quantidadeMinutos)





##### adicionaSegundos


Adiciona uma quantidade especificada de segundos em uma data/hora.

1. Datas.adicionaSegundos(data, quantidadeMinutos)



_Alternativa_

1. data.adicionaSegundos(quantidadeMinutos)





##### ano


Obtem o ano em que se encontra uma determinada data.

1. Datas.ano(data)



_Alternativa_

1. data.ano





##### data


Gera uma data sem hora de acordo com o dia, mês e ano passados por parâmetro

1. Datas.data(ano, mes, dia)



_Alternativa_

1. ano.data(mes, dia)





##### dataHora


Gera uma data com a hora de acordo com o dia, mês, ano, hora e minuto passados por parâmetro

1. Datas.dataHora(ano, mes, dia, hora, minuto)



_Alternativa_

1. ano.dataHora(mes, dia, hora, minuto)





##### dia


Obtem o dia em que se encontra uma determinada data.

1. Datas.dia(data)



_Alternativa_

1. data.dia





##### diaSemana


Obtem o dia da semana em que se encontra uma determinada data, considerando-se o domingo comoprimeiro dia e o sábado como o sétimo dia.

1. Datas.diaSemana(data)



_Alternativa_

1. data.diaSemana





##### diferencaAnos


Calcula a diferença em anos entre duas datas.

1. Datas.diferencaAnos(menorData, maiorData)



_Alternativa_

1. menorData.diferencaAnos(maiorData)





##### diferencaDias


Calcula a diferença em dias entre duas datas.

1. Datas.diferencaDias(menorData, maiorData)



_Alternativa_

1. menorData.diferencaDias(maiorData)





##### diferencaHoras


Calcula a diferença em horas entre duas datas.

1. Datas.diferencaHoras(menorData, maiorData)



_Alternativa_

1. menorData.diferencaHoras(maiorData)





##### diferencaMeses


Calcula a diferença em meses entre duas datas.

1. Datas.diferencaMeses(menorData, maiorData)



_Alternativa_

1. menorData.diferencaMeses(maiorData)





##### diferencaMinutos


Calcula a diferença em minutos entre duas datas/hora.

1. Datas.diferencaMinutos(menorData, maiorData)



_Alternativa_

1. menorData.diferencaMinutos(maiorData)





##### diferencaSegundos


Calcula a diferença em segundos entre duas datas/hora

1. Datas.diferencaSegundos(menorData, maiorData)



_Alternativa_

1. menorData.diferencaSegundos(maiorData)





##### ehData


Verifica se um texto é uma data válida.

1. Datas.ehData(texto)



_Alternativa_

1. texto.ehData





##### extenso


Obtem a data por extenso.

1. Datas.extenso(data)



_Alternativa_

1. data.extenso





##### hoje


Obtem a data e hora do sistema operacional.

1. Datas.hoje()



_Alternativa_

1. Datas.hoje(data)





##### hora


Obtem a hora em que se encontra uma determinada data/hora.

1. Datas.hora(data)



_Alternativa_

1. data.hora





##### mes


Obtem o mês em que se encontra uma determinada data.

1. Datas.mes(data)



_Alternativa_

1. data.mes





##### minuto


Obtem os minutos referentes a uma determinada data/hora

1. Datas.minuto(data)



_Alternativa_

1. data.minuto





##### nomeDiaSemana


Obtem o nome do dia da semana.

1. Datas.nomeDiaSemana(data)



_Alternativa_

1. data.nomeDiaSemana





##### nomeMes


Obtem o nome do mês de uma data.

1. Datas.nomeMes(data)



_Alternativa_

1. data.nomeMes





##### periodo


Cria um período com data inicial e data final.

1. Datas.periodo(dataInicial, dataFinal)





##### removeDias


Remove uma quantidade especificada de dias de uma data.

1. Datas.removeDias(data, quantidadeDias)



_Alternativa_

1. data.removeDias(quantidadeDias)





##### removeMeses


Remove uma quantidade especificada de meses de uma data. Caso o dia da data especificada não seja um dia válido para o mês resultante, Ex: 31/12/2011, remove 1 mês, valor inválido para nova data 31/11/2011, a diferença de dias será acrescentada da nova data, Ex: 31/12/2011,remove 1 mês fica 01/12/2011.

1. Datas.removeMeses(data, quantidadeMeses)



_Alternativa_

1. data.removeMeses(quantidadeMeses)





##### segundo


Obtem os segundos referentes a uma determinada data/hora.

1. Datas.segundo(data)



_Alternativa_

1. data.segundo





##### formatar


Obtem o valor de uma data formatado de acordo com um padrão especificado.

1. Datas.formatar(data, formato)



_Alternativa_

1. data.formatar



Exemplos:

1. //data definida como dia 26/05/2017
2. imprimir data.formatar('yyyy-MM-dd') // 2017-05-26
3. imprimir data.formatar('MM/yyyy') // 05/2017
4. imprimir data.formatar('EEEE') // Sexta-feira



Padrões para formatação:

Letra  | Descrição  | Exemplos
---|---|---
y  | Ano  | 2009; 09
M  | Mês do ano  | Julho; Jul; 07
w  | Semana no ano  | 27
W  | Semana no mês  | 2
D  | Dia no ano  | 189
d  | Dia no mês  | 10
F  | Dia da semana no mês  | 2
E  | Nome do dia da semana  | Segunda-feira, Seg
u  | Número do dia da semana (1=Segunda.7=Domingo)  | 1
a  | Indicador de AM/PM  | AM
H  | Hora no dia (0-23)  | 0
k  | Hora no dia (1-24)  | 24
K  | Hora no dia (0-11)  | 0
h  | Hora no dia (1-12)  | 12
m  | Minuto na hora  | 55
s  | Segundos no minuto  | 30
S  | Milissegundo  | 978



#### Numeros




##### absoluto


Calcula o valor absoluto de um número.

1. Numeros.absoluto(valor)





##### arredonda


Arredonda um valor.

1. Numeros.arredonda(valor, casasDecimais)





##### coseno


Calcula o co-seno de um ângulo.

1. Numeros.coseno(valor)





##### decimal


Converte o valor de um texto em um número decimal de alta precisão.

1. Numeros.decimal(texto)





##### ehNumero


Verifica se um texto é um número válido.

1. Numeros.ehNumero(texto)





##### exponencial


Obtem o exponencial de um número específico.

1. Numeros.exponencial(numero)





##### fatorial


Obtem o fatorial de um número.

1. Numeros.fatorial(numero)





##### inteiro


Converte o valor de um texto em um número inteiro. Caso o texto represente um número decimal, este será truncado para um inteiro, ou seja, a parte decimal será descartada.

1. Numeros.inteiro(texto)





##### logaritmo


Informa o logaritmo natural de um número.

1. Numeros.logaritmo(valor)





##### logaritmo10


Informa logaritmo de base 10 de um número.

1. Numeros.logaritmo10(valor)





##### maximo


Obtem o maior valor entre dois números.

1. Numeros.maximo(valor1, valor2)





##### minimo


Obtem o menor valor entre dois números.

1. Numeros.minimo(valor1, valor2)





##### numero


Converte o valor de um texto em um número, retornando o tipo Long para números inteiros e Double para números decimais.

IMPORTANTE! Esta função NÃO deve ser utilizada para trabalhar com valores monetários. O tipo Double não é adequado para esse fim e vai resultar em imprecisões que ao longo de um cálculo podem alterar de forma significativa o resultado. A função adequada para este fim é a Numeros.decimal.

1. Numeros.numero(texto)





##### pi


Multiplica o valor de PI pelo número especificado.

1. Numeros.pi(valorMultiplicar)





##### piso


Obtem o maior número que é menor ou igual ao número espedificado, sendo este número inteiro.

1. Numeros.piso(valor)





##### raiz


Calcula a raiz quadrada de um número.

1. Numeros.raiz(valor)





##### randomico


Obtem um número aleatório entre 1 a um valor limite especificado.

1. Numeros.randomico(numeroDelimitador)





##### resto


Retorna o resto da divisão realizada entre o dividendo e o divisor, que são passados porparâmetro.

1. Numeros.resto(valorDividendo, valorDivisor)





##### seno


Calcula o seno de um ângulo.

1. Numeros.seno(valor)





##### seZero


Testa os valores passados como parâmetro e retorna o primeiro diferente de zero.

1. Numeros.seZero(valor1, valor2, valorN)





##### tangente


Calcula a tangente de um ângulo.

1. Numeros.tangente(valor)





##### teto


Obtem o menor número que é maior ou igual ao número espedificado, sendo este número inteiro.

1. Numeros.teto(valor)





##### trunca


Trunca um valor de acordo com o número de casas decimais especificadas.

1. Numeros.trunca(valor, casasDecimais)





#### JSON




##### ler


Converte um json em um mapa

1. pessoa = JSON.ler('{"nome":"João da Silva"}')
2. imprimir pessoa.nome // imprimie João da Silva





##### escrever


Converte um objeto em json

1. json = JSON.escrever([nome: "João da Silva"])
2. imprimir json // imprimie {"nome":"João da Silva"}





## API de Arquivos


O bfc-script disponibiliza uma API para leitura e escrita de arquivos. As funções são separadas por tipo de arquivo e são invocadas como métodos. Esta sessão abordará o uso de cada função da API de arquivos e os detalhes de cada implementação. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.



#### Leitura de arquivos


A leitura de arquivos está disponível através da função _Arquivo.ler()_. Esta função irá retornar uma implementação específica com operações distintas para realizar a leitura do arquivo conforme tipo. Esta função contém algumas variações para permitir diferentes origens e a passagem de parâmetros para as implementações:

* Arquivo.ler(_arquivo ou conteúdo_): Realiza a leitura do arquivo utilizando a implementação padrão para arquivos texto.
* Arquivo.ler(_arquivo ou conteúdo, tipo do arquivo_): Realiza a leitura do arquivo utilizando a implementação própria para o tipo de arquivo informado.
* Arquivo.ler(_arquivo ou conteúdo, tipo do arquivo, parametros_): Realiza a leitura de arquivo utilizando a implementação própria para o tipo do arquivo informado permitindo a passagem de parâmetros específicos da implementação.
Exemplo de utilização:

1.     arquivoTxt = Arquivo.ler(origem, 'txt');
2.     arquivoCsv = Arquivo.ler('Bob|Esponja', 'csv', [delimitador:'|']);





#### Escrita de arquivos


A criação de um novo arquivo está disponível através da função _novo_. Esta função irá retornar uma implementação específica com operações distintas para realizar a escrita do arquivo conforme tipo. A função _novo_ contem algumas variações:

* Arquivo.novo(_nome do arquivo_): Cria um novo arquivo utilizando a implementação padrão para arquivos texto.
* Arquivo.novo(_nome do arquivo, tipo do arquivo_): Cria um novo arquivo arquivo utilizando a implementação própria para o tipo de arquivo informado.
* Arquivo.novo(_nome do arquivo, tipo do arquivo, parametros_): Cria um novo arquivo utilizando a implementação própria para o tipo de arquivo informado permitindo a passagem de parâmetros específicos da implementação.
Exemplo de utilização:

1.     arquivoTxt = Arquivo.novo('Jones.txt')
2.     arquivoCsv = Arquivo.novo('Spencer.csv', 'csv', [entreAspas: 'N'])





#### Download dos arquivos


Por padrão a API de arquivos não disponibiliza para download os arquivos criados pelas implementações. Para que os mesmos sejam incluídos no arquivo zip de resultado da execução de um script através da **Ferramenta de Scripts** é necessário adicionar estes arquivos ao resultado.

1. txt = Arquivo.novo('teste.txt', 'txt')
2.
3. //Adiciona o arquivo txt no zip do resultado
4. Resultado.arquivo(txt)
5.
6. //Personaliza o nome do arquivo no zip do resultado
7. Resultado.arquivo(txt, 'meu_arquivo.txt')
8.
9. //Personaliza o nome do arquivo e do diretório no zip do resultado
10. Resultado.arquivo(txt, 'meu_arquivo.txt', 'Arquivos texto')
11.
12. //Personaliza o nome do arquivo
13. Resultado.nome('meu_resultado.zip')





## Implementações




### Arquivos Texto (txt)




#### Leitura


1. arquivo = Arquivo.ler(arquivo, 'txt')



Lendo um arquivo com um Encoding específico (Por padrão utiliza UTF-8):

1. arquivo = Arquivo.ler(arquivo, 'txt', [ encoding: 'iso-8859-1' ]);





##### lerLinha()


Realiza a leitura de uma linha do arquivo e retorna o conteúdo lido.

1. texto = arquivo.lerLinha()





##### contemProximaLinha()


Verificar se o arquivo sendo lido contém uma próxima linha

1. percorrer(enquanto: { arquivo.contemProximaLinha() }) {
2.     imprimir arquivo.lerLinha()
3. }





#### Escrita


1. arquivo = Arquivo.novo('FendaDoBiquine.txt')



Criando um novo arquivo com um Encoding específico (Por padrão utiliza UTF-8):

1. arquivo = Arquivo.novo('FendaDoBiquine.txt', 'txt', [ encoding: 'iso-8859-1' ]);





##### escrever(texto)


Realiza a escrita de um conteúdo no arquivo

1. arquivo.escrever('Jonathan Peters')





##### novaLinha()


Realiza a escrita de uma quebra de linha no arquivo

1. arquivo.escrever('Jonathan Peters')
2. arquivo.novaLinha()
3. arquivo.escrever('Oscar Randall')





### Arquivos CSV (csv)




#### Leitura


1. arquivo = Arquivo.ler(arquivo, 'csv')



Lendo um arquivo com um Encoding específico (Por padrão utiliza UTF-8):

1. arquivo = Arquivo.ler(arquivo, 'txt', [ encoding: 'iso-8859-1' ]);



**Parâmetros de leitura:**

* _delimitador_ : Caracter que delimita os valores do arquivo CSV. Por padrão utiliza uma virgula.
* _encoding_ : Determina o encoding a ser usado na leitura do arquivo. Por padrão utiliza UTF-8.
##### lerLinha()


Realiza a leitura de uma linha do arquivo e retorna o conteúdo lido.

1. texto = arquivo.lerLinha()





##### contemProximaLinha()


Verificar se o arquivo sendo lido contém uma próxima linha

1. percorrer(enquanto: { arquivo.contemProximaLinha() }) {
2.     imprimir arquivo.lerLinha()
3. }





##### pularLinhas(int linhas)


Ignora a leitura da quantidade de linhas informado no parâmetro com base na linha atual

1. arquivo = Arquivo.ler('Nome,Endereco\nBob,Fenda do biquine', 'csv')
2. arquivo.pularLinhas(1)
3. imprimir arquivo.lerLinha() //Bob,Fenda do biquine





##### lerProximoValor()


Realiza a leitura do próximo valor do arquivo considerando o delimitador. Esta função realiza a leitura de todo o arquivo e não somente da linha atual.

1. arquivo = Arquivo.ler('Plancton,Mar\nBob,Fenda do Biquine', 'csv')
2. arquivo.lerProximoValor() //Plancton
3. arquivo.lerProximoValor() //Mar
4. arquivo.lerProximoValor() //Bob





##### contemProximoValor()


Indica se existe um próximo valor a ser lido no arquivo atual.

1. se(arquivo.contemProximoValor()){
2.     arquivo.lerProximoValor()
3. }





#### Escrita


1. arquivo = Arquivo.novo('FendaDoBiquine.csv', 'csv')



Criando um novo arquivo com um Encoding específico (Por padrão utiliza UTF-8):

1. arquivo = Arquivo.novo('FendaDoBiquine.csv', 'csv', [ encoding: 'iso-8859-1' ]);



**Parâmetros de escrita:**

* _delimitador_ : Caracter para delimitar os valores do arquivo CSV. Por padrão utiliza uma virgula.
* _entreAspas_ : Indica se os valores escritos no arquivo deverão estar entre aspas duplas. Utilizar _S_ para Sim e _N_ para Não.
* _encoding_ : Determina o encoding a ser usado na criação do arquivo. Por padrão utiliza UTF-8.
##### escrever(texto)


Realiza a escrita de um conteúdo no arquivo utilizando o delimitador parametrizado.

1. arquivo.escrever('Jonathan Peters')





##### novaLinha()


Realiza a escrita de uma quebra de linha no arquivo

1. arquivo.escrever('Jonathan Peters')
2. arquivo.novaLinha()
3. arquivo.escrever('Oscar Randall')





### Arquivos XML (xml)


Os documentos XML são lidos e escritos por item/evento. Cada parte do documento é considerado um item e possui caracteristicas diferentes. No exemplo abaixo podemos afirmar que o documento XML possui 5 itens/eventos:

1. <pessoa completo="N">João da Silva</pessoa>



dos quais:

1. Início de documento

2. `<pessoa` : Início do elemento. Este tipo de item contem um nome(pessoa), pode conter atributos, namespaces etc.

3. `João da Silva`: Texto do elemento. Este é um tipo de item considerado TEXTO. Diferente de um início de elemento ele não possui um nome e nem atributos.

4. `</pessoa>` : Fim do elemento

5. Fim de documento



### Implementação




#### Leitura


1. arquivo = Arquivo.ler(arquivo, 'xml')





##### tipo()


Retorna o tipo do item sendo lido. Os valores disponíveis são:

* INICIO_DOCUMENTO
* FIM_DOCUMENTO
* INICIO_ELEMENTO
* FIM_ELEMENTO
* ATRIBUTO
* DTD
* CDATA
* NAMESPACE
* TEXTO
* COMENTARIO
* ESPACO
* DECLARACAO_NOTACAO
* DECLARACAO_ENTIDADE
* REFERENCIA_ENTIDADE
##### valor()


Retorna o valor texto do item corrente. Caso o item seja um elemento complexo irá retornar em branco. Tipos suportados: _INICIO_ELEMENTO_ , _FIM_ELEMENTO_ , _ATRIBUTO_ , _REFERENCIA_ENTIDADE_ , _DECLARACAO_ENTIDADE_.



##### contemValor()


Indica se o item atual contém um valor do tipo texto e se o mesmo é diferente de vazio.

1. se(arquivo.contemValor()){
2.     imprimir arquivo.valor()
3. }





##### contemNome()


Indica se o item atual contém um nome e se o mesmo é diferente de vazio.



##### nome()


Retorna o nome do item atual. Caso o item não seja suportado irá retornar em branco. Tipos suportados: _INICIO_ELEMENTO_ , _FIM_ELEMENTO_ , _ATRIBUTO_ , _REFERENCIA_ENTIDADE_ , _DECLARACAO_ENTIDADE_.



##### xml()


Retorna o item atual no formato XML.



##### namespaces()


Retorna uma lista contendo os namespaces presentes no item atual. Tipos suportados: _INICIO_ELEMENTO_ , _FIM_ELEMENTO_ , _ATRIBUTO_ , _NAMESPACE_

Um Namespace contem as seguintes informações:

* prefixo(): Prefixo do namespace
* namespace(): Valor do namespace



##### contemNamespace(namespace)


Indica se o item atual contém um namespace declarado igual ao informado por parâmetro.



##### contemNamespace(namespace, prefixo)


Indica se o item atual contém um namespace declarado com valor e prefixo igual aos parâmetros.



##### atributos()


Retorna uma lista contendo os atributos presentes no item atual. Tipos suportados: _INICIO_ELEMENTO_

Um Atributo contem as seguintes informações:

* prefixo(): Prefixo do namespace
* namespace(): Namespace do atributo

* nome(): nome do atributo
* valor(): valor do atributo


1. percorrer(arquivo.atributos()){
2.     imprimir item.nome()
3. }





##### contemAtributo(nome)


Indica se o elemento atual contém um atributo com o nome informado no parâmetro. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### contemAtributo(nome, namespace)


Indica se o elemento atual contém um atributo com o nome e namespace informado no parâmetro. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### contemAtributo(nome, namespace, prefixo)


Indica se o elemento atual contém um atributo com o prefixo, nome e namespace informado no parâmetro. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### atributo(nome)


Retorna o [atributo](index.html#apiArquivosImplementacoesXmlTiposAtributo) do elemento com base no nome informado no parâmetro. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### atributo(nome, namespace)


Retorna o [atributo](index.html#apiArquivosImplementacoesXmlTiposAtributo) do elemento com base no namespace e nome informado nos parâmetros. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### atributo(nome, namespace, prefixo)


Retorna o [atributo](index.html#apiArquivosImplementacoesXmlTiposAtributo) do elemento com base no prefixo, namespace e nome informado nos parâmetros. Tipos suportados: _INICIO_ELEMENTO_ , _ATRIBUTO_



##### ehTipoInicioDocumento


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a INICIO_DOCUMENTO



##### ehTipoFimDocumento


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a FIM_DOCUMENTO



##### ehTipoTexto


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a TEXTO



##### ehTipoComentario


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a COMENTARIO



##### ehTipoFimElemento


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a FIM_ELEMENTO



##### ehTipoInicioElemento


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a INICIO_ELEMENTO



##### ehTipoEspaco


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a ESPACO



##### ehTipoCData


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a CDATA



##### ehTipoAtributo


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a ATRIBUTO



##### ehTipoNamespace


Indica se o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do item atual é igual a NAMESPACE



##### contemProximo()


Indica se o documento atual contem um próximo item a ser lido.



##### tipoProximo()


Retorna o [tipo](index.html#apiArquivosImplementacoesXmlTipos) do próximo item caso a leitura do documento não tenha sido finalizada.



##### proximo()


Itera no documento passando a leitura para o próximo item. Tem como retorno o tipo do novo item.

1. percorrer(enquanto: { xml.contemProximo() }) {
2.
3.   xml.proximo()
4.
5.   imprimir '#Dados do elemento: ' + conta
6.   imprimir 'Tipo: ' + xml.tipo()
7.
8.   se(xml.contemValor()){
9.   	 imprimir 'Valor: ' + xml.valor()
10.   }
11.
12.   se(xml.contemProximo()){
13. 	imprimir 'Tipo do proximo elemento: ' + xml.tipoProximo()
14.   }
15.
16.   se(xml.ehTipoInicioElemento()){
17.       imprimir 'Nome: ' + xml.nome()
18.       percorrer(xml.atributos()){
19.   		imprimir 'Atributo: ' + item.nome() + '=' + item.valor()
20.   	}
21.   }
22. }





##### proximaTag()


Itera no documento passando a leitura para o próxima tag encontrada (INICIO_ELEMENTO ou FIM_ELEMENTO). Tem como retorno o tipo do novo item atual.



##### contemProximoElemento()


Indica se o documento atual contem um próximo elemento a ser lido.



##### proximoElemento()


Itera no documento passando a leitura para o próximo elemento (INICIO_ELEMENTO). Tem como retorno um valor booleano indicando se a leitura do próximo elemento foi realizada ou se o documento chegou ao fim.

1. xml = Arquivo.ler('<root><!-- Nomes dos colaboradores --><nome completo="N" composto="S">Marcos da Silva</nome><nome completo="S">Maria Joana Amaral</nome></root>', 'xml');
2.
3. //Leitura baseada em elementos
4. percorrer(enquanto: { xml.proximoElemento() }) {
5.
6.   imprimir '#Dados do elemento:'
7.   imprimir 'Tipo: ' + xml.tipo()
8.   imprimir 'Nome: ' + xml.nome()
9.   imprimir 'Valor: ' + xml.valor()
10.
11.   percorrer(xml.atributos()){
12. 	imprimir 'Atributo: ' + item.nome() + '=' + item.valor()
13.   }
14. }





##### proximoElemento(nome)


Itera no documento passando a leitura para o próximo elemento cujo nome seja igual ao valor informado no parâmetro. Tem como retorno um valor booleano indicando se a leitura do elemento foi realizada ou se o documento chegou ao fim e o mesmo não foi encontrado.



##### proximoElemento(nome, namespace)


Itera no documento passando a leitura para o próximo elemento cujo nome e namespace sejam iguais aos valores informados nos parâmetros. Tem como retorno um valor booleano indicando se a leitura do elemento foi realizada ou se o documento chegou ao fim e o mesmo não foi encontrado.



#### Escrita


1. arquivo = Arquivo.novo('FendaDoBiquine.xml', 'xml')



**Parâmetros de escrita:**

* _encoding_ : Encoding do documento XML. Por padrão utiliza UTF-8.
* _indentar_ : Indica se o documento será escrito indentado ou de forma linear. Utilizar _S_ para Sim e _N_ para Não.
##### namespacePadrao(namespace)


Define o namespace padrão do elemento XML.



##### prefixo(prefixo, uri)


Define o prefixo de uma URI.



##### escreverAtributo(nome, valor)


Escreve um novo atributo no elemento atual.

1. xml.escreverInicioElemento('pessoa')
2. xml.escreverAtributo('idade', '18')
3. //Saída: <pessoa idade="18">





##### escreverAtributo(nome, valor, namespace)


Escreve um novo atributo no elemento atual informando também o namespace.



##### escreverAtributo(nome, valor, namespace, prefixo)


Escreve um novo atributo no elemento atual informando também o namespace.



##### escreverCData(data)


Escreve uma área com conteúdo CDATA no documento XML.



##### escreverTexto(texto)


Escreve texto no item atual.

1. xml.escreverInicioElemento('pessoa')
2. xml.escreverTexto('João')
3. xml.escreverFimElemento('pessoa')
4.
5. //Saída: <pessoa>João</pessoa>





##### escreverComentario(comentario)


Escreve um comentário no documento XML.

1. <!-- comentário -->





##### escreverNamespace(namespace)


Escreve um namespace no elemento atual.



##### escreverNamespace(namespace, prefixo)


Escreve um namespace com prefixo no elemento atual.



##### escreverDTD(dtd)


Escreve um [DTD](http://www.w3schools.com/xml/xml_dtd_intro.asp) no documento XML.



##### escreverElementoVazio(elemento)


Escreve um elemento vazio no documento XML:

1. xml.escreverElementoVazio('vazio')
2. //Saída: <vazio />





##### escreverElementoVazio(elemento, namespace)


Escreve um elemento vazio e namespace no documento XML.



##### escreverElementoVazio(elemento, namespace, prefixo)


Escreve um elemento vazio e namespace com prefixo no documento XML.



##### escreverInicioDocumento()


Escreve a declaração de um documento XML.



##### escreverInicioDocumento(encoding)


Escreve a declaração de um documento XML informando o encoding.



##### escreverInicioDocumento(encoding, versao)


Escreve a declaração de um documento XML informando o encoding e versão.

1. xml.escreverInicioDocumento('UTF-8', '1.0')
2. //Saída: <?xml version='1.0' encoding='UTF-8'?>





##### escreverInicioDocumento(encoding, versao, standalone)


Escreve a declaração de um documento XML informando o encoding, versão e standalone.



##### escreverFimDocumento()


Escreve o fim do documento XML.



##### escreverInicioElemento(nome)


Escreve o início de um elemento no documento XML.

1. xml.escreverInicioElemento('pessoa')
2. //Saída: <pessoa>





##### escreverInicioElemento(nome, namespace)


Escreve o início de um elemento com namespace no documento XML.



##### escreverInicioElemento(nome, namespace, prefixo)


Escreve o início de um elemento com namespace e prefixo no documento XML.



##### escreverFimElemento()


Escreve o fim do elemento atual.



##### nomeElementoAtual()


Retorna o nome do elemento sendo editado.

1. xml.escreverInicioElemento('pessoa')
2. xml.escreverInicioElemento('endereco')
3. imprimir xml.nomeElementoAtual() //Saída: endereco
4. xml.escreverFimElemento()
5. imprimir xml.nomeElementoAtual() //Saída: pessoa





##### escreverFimElementos()


Escreve o fim de todos os elementos atualmente abertos.

1. xml.escreverInicioElemento('pessoa')
2. xml.escreverInicioElemento('endereco')
3. xml.escreverFimElementos()
4.
5. //Saída: <pessoa><endereco></endereco></pessoa>





##### escreverFimElementos(elementoParar)


Escreve o fim de todos os elementos abertos abaixo do elemento informado no parâmetro.

1. xml.escreverInicioElemento('pessoa')
2. xml.escreverInicioElemento('endereco')
3. xml.escreverInicioElemento('cidade')
4. xml.escreverInicioElemento('bairro')
5.
6. xml.escreverFimElementos('endereco')
7.
8. //Saída: <pessoa><endereco><cidade><bairro></bairro></cidade></endereco>





##### escreverElementoTexto(nome, valor)


Escreve um elemento texto no documento XML.

1. xml.escreverElementoTexto('nome', 'Maria')
2. //Saída: <nome>Maria</nome>





##### escreverElementoTexto(nome, valor, namespace)


Escreve um elemento texto com namespace.



##### escreverElementoTexto(nome, valor, namespace, prefixo)


Escreve um elemento texto com namespace e prefixo.



##### escrever(xml)


Escreve um bloco XML no arquivo atual.

1. xml.escrever('<nome>José</nome>')





##### contemElementoAberto()


Indica se o documento atual contém algum início de elemento sem um fim declarado.



##### escreverReferencia(nome, id, valor)


Escreve a referência à uma [entidade](http://www.w3schools.com/xml/xml_dtd_entities.asp) no documento XML.



##### escreverInstrucaoProcessamento(target, conteudo)


Escreve as instruções de processamento no documento.



##### escreverEspaco(conteudo)


Escreve um item texto do [tipo](index.html#apiArquivosImplementacoesXmlTipos) ESPACO



##### escreverEspacoIgnoravel(conteudo)


Escreve um item texto do [tipo](index.html#apiArquivosImplementacoesXmlTipos) ESPACO ignorável.



### Arquivos JSON (json)


Os documentos JSON são lidos e escritos por item/evento. Cada parte do documento é considerado um item e possui caracteristicas diferentes. No exemplo abaixo podemos afirmar que o documento JSON possui 4 itens:

1. {
2.     "nome": "João da Silva"
3. }



dos quais:

1. `{` : Início do objeto. Este tipo de item pode conter propriedades.

2. `"nome"`: Nome do campo. Este é um tipo de item considerado TEXTO.

3. `"João da Silva""` : Valor do campo

4. `}` Fim de objeto



### Implementação




#### Leitura


1. json = Arquivo.ler('''
2. {
3.     "nome": "João da Silva",
4.     "telefones": [
5.             "4899999999999",
6.             "4899999999992"
7.     ]
8. }
9. ''', 'json')
10.
11. json.proximo() // inicio do objeto
12. json.proximo() // nome do primeiro campo
13.
14. nomePessoa = ""
15. telefonesPessoa = []
16.
17. percorrer(enquanto: { !json.ehFimObjeto() }) {
18.
19.     nomeCampo = json.texto()
20.
21.     se(nomeCampo == "nome"){
22.         nomePessoa = json.proximo().texto()
23.     }
24.
25.     se(nomeCampo == "telefones"){
26.
27.         json.proximo() // inicio do array
28.         json.proximo() // primero item do array
29.
30.         telefones = []
31.         percorrer(enquanto: { !json.ehFimMatriz() }) {
32.             telefonesPessoa<<json.texto()
33.             json.proximo() // proximo item
34.         }
35.     }
36.
37.     json.proximo() // avança para o proximo campo
38. }
39.
40. pessoa = [nome: nomePessoa, telefones: telefonesPessoa]
41.





##### proximo()


Avança a leitura para o próximo item



##### ehInicioObjeto()


Retorna um valor booleano indicando se o item atual é o inicio de um objeto



##### ehInicioMatriz()


Retorna um valor booleano indicando se o item atual é o inicio de uma matriz (array)



##### ehFimObjeto()


Retorna um valor booleano indicando se o item atual é o fim de um objeto



##### ehFimMatriz()


Retorna um valor booleano indicando se o item atual é o fim de uma matriz (array)



##### ehNomeCampo()


Retorna um valor booleano indicando se o item atual é o nome de um campo



##### ehTexto()


Retorna um valor booleano indicando se o item atual é um texto



##### ehNumero()


Retorna um valor booleano indicando se o item atual é um número



##### ehBooleano()


Retorna um valor booleano indicando se o item atual é um booleano



##### ehNulo()


Retorna um valor booleano indicando se o item atual é nulo



##### texto()


Retorna o valor do item atual como texto



##### numero()


Retorna o valor do item atual como número



##### booleano()


Retorna o valor do item atual como booleano



##### jsonParser()


Retorna a implementação nativa do parse que está sendo usado, para possibilitar implementações avançadas, acesse <https://fasterxml.github.io/jackson-core/javadoc/2.5/com/fasterxml/jackson/core/JsonParser.html> para mais informações.



#### Escrita


1. json = Arquivo.novo('pessoa.json', 'json')
2.
3. json.escreverInicioObjeto()
4. json.escreverNomeCampo("nome")
5. json.escreverTexto("João da Silva")
6.
7. json.escreverNomeCampo("telefones")
8. json.escreverInicioMatriz()
9.
10. json.escreverTexto("4899999999999")
11. json.escreverTexto("4899999999992")
12.
13. json.escreverFimMatriz()
14. json.escreverFimObjeto()
15.





##### escreverInicioMatriz()


Escreve o inicio de uma matriz (array)



##### escreverFimMatriz()


Escreve o fim de uma matriz (array)



##### escreverInicioObjeto()


Escreve o inicio de um objeto



##### escreverFimObjeto()


Escreve o fim de um objeto



##### escreverNomeCampo(nome)


Escreve o nome do campo

1. {
2.     "valor": ""
3. }





##### escreverTexto(texto)


Escreve um texto

1. {
2.     "valor": "abc"
3. }





##### escreverNumero(numero)


Escreve um número

1. {
2.     "valor": 123
3. }





##### escreverBooleano(booleano)


Escreve um boolenao

1. {
2.     "valor": true
3. }





##### escreverNulo()


Escreve o valor nulo

1. {
2.     "valor": null
3. }





##### escreverObjeto(objeto)


Escreve um objeto completo

1. json.escreverObjeto([nome: "AAA"])



1. {
2.     "valor": {
3.         "nome": "AAA"
4.     }
5. }





##### escreverCampoTexto(nome, texto)


Escreve o nome e o valor de campo do tipo texto



##### escreverCampoBooleano(nome, booleano)


Escreve o nome e o valor de campo do tipo booleano



##### escreverCampoNulo(nome)


Escreve o nome e o valor de campo nulo



##### escreverCampoNumero(nome, numero)


Escreve o nome e o valor de campo do tipo numero



##### escreverCampoInicioMatriz(nome)


Escreve o nome e o inicio de um campo do tipo matriz (array)



##### escreverCampoInicioObjeto(nome)


Escreve o nome e o inicio de um campo do tipo objeto



##### escreverCampoObjeto(nome, objeto)


Escreve o nome e o valor de um campo do tipo objeto



##### jsonGenerator()


Retorna a implementação nativa do jsonGenerator que está sendo utilizado, para mais informações acesse <https://fasterxml.github.io/jackson-core/javadoc/2.8/com/fasterxml/jackson/core/JsonGenerator.html>



### Arquivos ZIP (zip)




#### Leitura


A leitura de arquivos .zip está disponível através da seguinte chamada:

1. zip = Arquivo.ler('arquivo.zip', 'zip')



Onde iterando, é possível navegar entre os arquivos:

1. percorrer(zip) {
2.
3.     //Imprime o nome do arquivo, sem considerar extensão
4.     imprimir item.nome;
5.
6.     imprimir item.extensao;
7.
8.     //Imprime o nome inteiro do arquivo, incluindo extensão e a sua estrutura de pastas
9.     imprimir item.nomeAbsoluto;
10.
11.     //É possivel identificar se o item em questão representa um diretório
12.     imprimir item.ehDiretorio();
13.
14.     //Recupera uma referência de um arquivo ao conteúdo do zip.
15.     arquivo = item.arquivo;
16.
17.     //Pode ser utilizado outras apis para trabalhar no arquivo descompactado...
18.     Arquivo.ler(arquivo, 'txt');
19. }



**Obs:** Caso durante a geração do zip, seja utilizado um encoding diferente do UTF-8, o valor deve ser informado. Por exemplo:

1. zip = Arquivo.ler('arquivo.zip', 'zip', [encoding: 'CP437'])





#### Escrita


1. arquivo = Arquivo.novo('relatorios.zip', 'zip')





##### criarDiretorio


Realiza a criação de um diretório em branco no arquivo zip

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.criarDiretorio('2016')



1. relatorios.zip
2. └─ 2016





##### adicionar(Arquivo)


Adiciona um arquivo no diretório raiz do arquivo zip

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar(parametros.arquivo.valor)





##### adicionar(Arquivo, Nome do arquivo no zip)


Adiciona um arquivo no diretório raiz do arquivo zip utilizando o nome informado no segundo parâmetro

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar(parametros.arquivo.valor, 'despesas.pdf')



1. relatorios.zip
2. └─ despesas.pdf





##### adicionar(Arquivo, Nome do arquivo no zip, Diretório)


Adiciona um arquivo em um determinado diretório do arquivo zip utilizando o nome informado como parâmetro. Caso o diretório não exista no arquivo zip o mesmo será criado.

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar(parametros.arquivo.valor, 'despesas.pdf', '2016')



1. relatorios.zip
2. └─ 2016
3.     └─ despesas.pdf



É possível criar subdiretórios utilizando o separador **/** no nome do diretório:

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar(parametros.arquivo.valor, 'despesas.pdf', '2016/Despesas')



1. relatorios.zip
2. └─ 2016
3.     └─ Despesas
4.         └─ despesas.pdf





##### adicionar(Lista de arquivos)


Adiciona um ou mais arquivos no diretório raiz do arquivo zip.

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar([parametros.despesas.valor, parametros.receitas.valor])



1. relatorios.zip
2. ├─ Despesas.pdf
3. └─ Receitas.pdf





##### adicionar(Lista de arquivos, Diretório)


Adiciona um ou mais arquivos no diretório informado no parâmetro do arquivo zip. Caso o diretório não exista o mesmo será criado.

1. arquivo = Arquivo.novo('relatorios.zip', 'zip')
2. arquivo.adicionar([parametros.despesas.valor, parametros.receitas.valor], 'Arquivos')



1. relatorios.zip
2. └─ Arquivos
3.    ├─ Despesas.xml
4.    └─ Receitas.xml





##### comentario(Comentário)


Adiciona um comentário às informações do arquivo zip

1. Arquivo.novo('relatorios.zip', 'zip').comentario('Arquivo contendo os relatórios')





## API de E-mail


O bfc-script disponibiliza uma API para envio de mensagens de e-mails. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.

Para criar uma nova mensagem de e-mail a ser enviada deve-se utilizar a função Email.**novo()** :

1. msg = Email.novo()



Uma mensagem contem diversas caracteristicas que serão apresentadas a seguir, uma vez configurada a mensagem, o envio é realizado através da função **enviar()** da mensagem.

1. msg = Email.novo()
2. //configurações da mensagem
3. msg.enviar()





### Mensagem




#### de(email)


Define o email do remetente da mensagem



#### de(email, nome)


Define o email e nome do remetente da mensagem



#### para(email)


Adiciona um email de destinatário na mensagem



#### para(email, nome)


Adiciona um email e nome de destinatário na mensagem



#### copiaPara(email)


Adiciona um email de cópia na mensagem



#### copiaPara(email, nome)


Adiciona um email e nome de cópia na mensagem



#### copiaOcultaPara(email)


Adiciona um email de cópia oculta na mensagem



#### copiaOcultaPara(email, nome)


Adiciona um email e nome de cópia oculta na mensagem



#### responderPara(email)


Adiciona um email no qual a mensagem deverá ser respondia pelos destinatários



#### responderPara(email, nome)


Adiciona um email e nome no qual a mensagem deverá ser respondia pelos destinatários



#### mensagem(mensagem)


Define o conteúdo da mensagem



#### mensagemHtml(mensagem)


Define o conteúdo da mensagem como HTML



#### assunto(assunto)


Define o assunto da mensagem



#### cabecalho(nome, valor)


Adiciona um cabecalho no e-mail



#### autenticacao([usuario, senha, porta, host])


Autentica o envio do email. Exemplo de uso:

.autenticacao([ usuario: joao, senha: joao, porta: 587, host: smtp.live.com])



#### enviar()


Envia a mensagem de e-mail



### Anexos


A API conta com 2 tipos de anexos disponíveis, sendo um baseado em fonte de arquivos e outro em URL. Exemplos de fonte de arquivos são os parâmetros do script do tipo Arquivo e artefatos gerados pela API de arquivos.



#### Criando anexos:


A criação de anexos pode ser realizada através de funções específicas da API ou de forma simplificada pela mensagem. Anexos criados pelas funções da API devem ser manualmente adicionados à mensagem. Por motivo de performance, caso o mesmo anexo do tipo Arquivo tenha que ser enviado para vários destinatários em mensagens diferentes, este deverá ser criado pela API uma única vez no processo.



#### Funções de anexo da API




##### Email.criarAnexoUrl()


Cria um novo anexo do tipo URL.



##### Email.criarAnexoUrl(url)


Cria um novo anexo do tipo URL informando o endereço.



##### Email.criarAnexoUrl(url, nome)


Cria um novo anexo do tipo URL informando o endereço e o nome a ser utilizado na mensagem.



##### Email.criarAnexoArquivo()


Cria um novo anexo do tipo arquivo.



##### Email.criarAnexoArquivo(arquivo)


Cria um anexo do tipo arquivo com base em uma fonte de arquivos.

1.  csv = Arquivo.novo('teste.csv', 'csv')
2.  csv.escrever('Valor')
3.  csv.fechar()
4.
5.  //Arquivo criado pela API de arquivos
6.  anexoArquivo = Email.criarAnexoArquivo(csv)
7.
8.  //Parâmetro do script tipo Arquivo
9.  anexoParametro = Email.criarAnexoArquivo(parametros.xml.valor)
10.
11.  Email.novo()
12.     .anexar(anexoArquivo)
13.     .anexar(anexoParametro)
14.





##### Email.criarAnexoArquivo(arquivo, nome)


Cria um anexo do tipo arquivo com base em uma fonte de arquivos. O nome do anexo será o mesmo informado no parâmetro nome.



#### Propriedades dos anexos




##### nome(nome)


Nome do anexo



##### descricao(descricao)


Descrição do anexo



##### dispostoParaVisualizacao()


Define a disposição do anexo para visualização INLINE no corpo do e-mail.



##### dispostoComoAnexo()


Define a disposição do anexo como ATTACHMENT (arquivo anexado).



##### incorporado()


Define o anexo como incorporado. Esta opção irá gerar um CID com base no nome do anexo e poderá ser utilizado no corpo da mensagem para referenciar o anexo.



##### naoIncorporado()


Define o anexo como não incorporado. Por padrão todos os anexos criados não são incorporados.



##### url(url)


Define a url para anexos do tipo URL.



##### arquivo(arquivo)


Define a fonte do arquivo para anexos do tipo Arquivo.



#### Funções de anexo da Mensagem




##### anexar(anexo)


Adiciona um anexo criado a partir das funções Email.criarAnexoXX() à mensagem

1.  anexo = Email.criarAnexoUrl('http://cnd.fgv.br/sites/cnd.fgv.br/files/teste_2.pdf', 'Nome do arquivo.pdf')
2.  msg.anexar(msg)





##### anexarArquivo(origem)


Adiciona um anexo à mensagem com base em uma fonte de arquivo. Exemplos de fontes são o valor de um parâmetro do script do tipo arquivo e um arquivo criado pela API de arquivos.

1.  csv = Arquivo.novo('teste.csv', 'csv')
2.  csv.escrever('Valor')
3.  csv.fechar()
4.
5.  //Arquivo criado pela API de arquivos
6.  msg.anexarArquivo(csv)
7.
8.  //Parâmetro do script tipo Arquivo
9.  msg.anexarArquivo(parametros.xml.valor)





##### anexarArquivo(origem, nome)


Adiciona um anexo à mensagem com base em uma fonte de arquivo. O nome do anexo na mensagem será o mesmo informado no parâmetro nome.



##### anexarArquivo(anexoArquivo)


Adiciona um anexo criado a partir da função Email.criarAnexoArquivo à mensagem



##### anexarUrl(url)


Adiciona um anexo à mensagem com base em uma URL. O download do anexo será realizado e adicionado a mensagem.



##### anexarUrl(url, nome)


Adiciona um anexo à mensagem com base em uma URL. O download do anexo será realizado e um anexo com o nome parametrizado será adicionado.

1.  msg.anexarUrl('http://cnd.fgv.br/sites/cnd.fgv.br/files/teste_2.pdf', 'Nome do arquivo.pdf')





##### anexarUrl(anexoUrl)


Adiciona um anexo criado a partir da função Email.criarAnexoUrl à mensagem



### Exemplos




#### Envio de e-mail autenticado


1. Email.novo()
2. 	.autenticacao([ usuario: 'usuario', senha: 'senha', porta: 'porta', host: 'smtp.live.com' ])
3. 	.de('betha@betha.com.br','Betha Sistemas')
4. 	para(destinatario, 'Destinatário')
5. 	.mensagem('Testando envio de email')
6. 	.assunto('Envio cloud job')
7. 	.enviar();





#### Envio de e-mail com anexos


1. email = Email.novo()
2.
3. imagemAssinatura = Email.criarAnexoUrl('http://www.betha.com.br/site/images/betha-2.png', 'logo.png')
4.                         .dispostoParaVisualizacao()
5.                         .incorporado()
6.
7. destinatario = 'destinatario@betha.com.br'
8.
9. email.de('betha@betha.com.br','Betha Sistemas')
10.      .para(destinatario, 'Destinatário')
11.      .copiaPara(destinatario, 'Destinatário de cópia')
12.      .copiaOcultaPara(destinatario)
13.      .responderPara(destinatario, 'Nome para Resposta')
14.      .assunto('Teste de e-mail')
15.      .mensagemHtml('Este é um teste de e-mail. <br/><br/>' +
16.                       'Att, <br/><br/>' +
17.                       'Betha Sistemas <p/><p/>' +
18.                       '<img src="cid:logo.png" width="319" height="51" />')
19.      .anexar(imagemAssinatura)
20.      .anexarUrl('http://cnd.fgv.br/sites/cnd.fgv.br/files/teste_2.pdf', 'Nome do arquivo.pdf')
21.      .enviar()
22.
23.
24. imprimir 'E-mail enviado com sucesso!'





#### Enviar arquivos dos parâmetros do script e API de Arquivos


1. csv = Arquivo.novo('teste.csv', 'csv')
2. csv.escrever('Valor')
3.
4. anexoCsv = Email.criarAnexoArquivo(csv, 'teste.csv')
5.
6. Email.novo()
7.      .de('betha@betha.com.br','Betha Sistemas')
8.      .para('destinatario@betha.com.br', 'Destinatário')
9.      .assunto('Teste de e-mail')
10.      .mensagem('Novo arquivo enviado.')
11.      .anexar(anexoCsv)
12.      .anexarArquivo(parametros.arquivo.valor, 'Arquivo.xml')
13.      .enviar()





## API de Notificações


O bfc-script disponibiliza uma API para envio de notificações aos usuários do sistema. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.

Para criar uma nova notificação deve-se utilizar a função Notificacao.**nova()** :

1. msg1 = Notificacao.nova()
2. msg2 = Notificacao.nova('Seja bem vindo!') //Define a mensagem na inicialização



Uma mensagem contem diversas caracteristicas que serão apresentadas a seguir, uma vez configurada a mensagem, o envio é realizado através da função **enviar()** da mensagem.

1. msg = Notificacao.nova()
2. //configurações da mensagem
3. msg.enviar()





### Mensagem




#### para(usuarios)


Adiciona um usuário como destinatário da notificação. É possível adicionar vários usuários:

1. Notificacao.nova('Seja bem vindo!')
2.            .para('joao.silva', 'maria.silva')
3.            .enviar()



Também é possível adicionar o usuário logado como destinatário da notificação usando o identificador `usuario.id`:

1. Notificacao.nova('Seja bem vindo!')
2.            .para(usuario.id)
3.            .enviar()



Mais um exemplo, usando o usuário logado e outros usuários:

1. Notificacao.nova('Seja bem vindo!')
2.            .para(usuario.id, 'joao.silva', 'maria.silva')
3.            .enviar()





#### mensagem(mensagem)


Define a mensagem a ser enviada pela notificação



#### link(href)


Define o link a ser enviado pela notificação



#### link(href, titulo)


Define o link com título a ser enviado pela notificação



#### link(href, titulo, label)


Define o link, titulo e label a ser enviado pela notificação



#### enviar()


Realiza o envio da notificação aos destinatários.



### Exemplos


1. Notificacao.nova('Seja bem vindo!')
2.            .para('usuario.betha', 'suite.betha')
3.            .enviar()



1. Notificacao.nova()
2.            .para('suite.betha')
3.            .mensagem('Obrigado!')
4.            .enviar()





## API de Mensagens


O bfc-script disponibiliza uma API para envio de mensagens aos usuários do sistema. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Eventos** , e serão absorvidas plenamente conforme a utilização.

A API possibilita o envio de quatro tipos de mensagens: erro, aviso, informação e sucesso, conforme o exemplo abaixo::

1. Mensagens.erro('Mensagem de erro')
2. Mensagens.aviso('Mensagem de aviso')
3. Mensagens.info('Mensagem de informação')
4. Mensagens.sucesso('Mensagem de sucesso')



É possível ainda adicionar mensagens parametrizadas:

1. Mensagens.erro('Mensagem de %s %s', 'erro', 'parametrizada')





## API de SOAP


O bfc-script disponibiliza uma API para consumo de serviços web no padrão SOAP. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.

A API conta com algumas representações básicas de funcionamento sendo elas o **Serviço** , a **Mensagem** e a **Resposta**. O **Serviço** trata-se de um webservice SOAP a ser consumido, cada interação com esse webservice é realizado através de uma **Mensagem**. O produto desta mensagem quando executada é uma **Resposta** , essa resposta pode ser transformada em vários tipos de saídas, sendo elas um Leitor de XML da API de arquivo, Uma fonte de arquivo para utilização em conjunto com outras APIs (E-mail, Arquivos), O conteúdo XML da resposta em sí ou simplesmente a impressão da resposta no console do script.


### Serviço


Para criar um novo serviço SOAP à ser consumido deve-se utilizar a função Soap.**servico** , as opções disponíveis para criação e configurações dos serviços são:



#### Soap.servico(url)


Cria um novo servico com base na URL informada por parâmetro.

1. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx')





#### Soap.servico(url, namespace, prefixo)


Cria um novo serviço com base na URL informada por parâmetro. O namespace e prefixo (target namespace) informados serão utilizados como padrão na montagem da mensagem e manipulação dos elementos.

1. Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx',
2.              'http://ws.cdyne.com/',
3.              'ws')





#### Soap.servico(url, namespace, prefixo, usuario, senha)


Esta opção dá suporte a criação de serviços que utilizem mecanismos de autenticação HTTP básico permitindo informar também o usuário e senha de conexão como parâmetros.



#### Soap.criarNamespace(namespace, prefixo)


Cria uma representação de um namespace e prefixo para ser reutilizado nas funções da API, desta forma não é necessário informar namespace e prefixo a cada função.

Os valores podem ser acessados através das funções: **namespace()** e **prefixo()** da representação criada.

1. namespace = Soap.criarNamespace('http://ws.cdyne.com/', 'ws')
2. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx', namespacePadrao)
3.
4. imprimir namespace.namespace()
5. imprimir namespace.prefixo()





#### cabecalho(nome, valor)


Adiciona um cabeçalho(header) HTTP na requisição SOAP do serviço.

1. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx')
2. servico.cabecalho('Authorization','Bearer 239e3d8e-1e93-4f2b-beff-c430103b9287')





#### cookie(nome, valor, path)


Adiciona um cookie na requisição SOAP do serviço.

1. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx')
2. servico.cookie('nome', 'valor', 'path')



**detalhe:** path é opcional e pode ser omitido.



#### mensagem()


Cria uma nova mensagem (envelope) à ser enviado ao serviço.



#### mensagem(namespace, prefixo)


Cria uma nova mensagem (envelope) à ser enviado ao serviço sobrescrevendo o namespace e prefixo padrão informados na criação do serviço.



#### mensagem([namespace](index.html#apiSoapServicoCriarNamespace))


Cria uma nova mensagem (envelope) à ser enviado ao serviço sobrescrevendo o namespace e prefixo padrão informados na criação do serviço. Esta opção deve ser utilizada com namespaces criados com a função [Soap.criarNamespace](index.html#apiSoapServicoCriarNamespace).



#### tempoLimite(valor)


Define o tempo limite para a execução das requisições. O valor deve ser informado em milissegundos.



### Mensagem


A representação de uma mensagem é composta basicamente de um cabeçalho e de um corpo. Ambos podem conter diversos [elementos](index.html#apiSoapMensagemElemento) que por sua vez podem possuir outros [elementos](index.html#apiSoapMensagemElemento). Esta estrutura de árvore é baseada no padrão XML e é através dela que os parâmetros de entrada da funcionalidade do webservice são informados. Em resumo, uma mensagem destina-se à execução de um método/função de um serviço SOAP.

As opções disponíveis para montagem da mensagem são:



#### namespace(namespace, prefixo)


Adiciona um namespace a mensagem. Este namespace será adicionado ao envelope SOAP da mensagem e poderá ser utilizado na declaração dos [elementos](index.html#apiSoapMensagemElemento).



#### namespace([namespace](index.html#apiSoapServicoCriarNamespace))


Adiciona um namespace a mensagem. Este namespace será adicionado ao envelope SOAP da mensagem e poderá ser utilizado na declaração dos [elementos](index.html#apiSoapMensagemElemento).



#### namespaces()


Retorna uma lista com os [namespaces](index.html#apiSoapServicoCriarNamespace) declarados na mensagem.



#### namespacePadrao()


Retorna o [namespaces](index.html#apiSoapServicoCriarNamespace) definido como padrão da mensagem.



#### corpo()


Retorna o [elemento](index.html#apiSoapMensagemElemento) do corpo da mensagem.



#### corpo(conteudo)


Escreve o conteúdo XML no corpo da mensagem. É importante lembrar que o conteúdo deverá ser um XML válido e utilizar os namespaces declarados na mensagem/corpo.

1. servico.mensagem().corpo('<ws:VerifyEmail><ws:email>teste@test.com</ws:email><ws:LicenseKey>example</ws:LicenseKey></ws:VerifyEmail>')





#### corpo(arquivo)


Escreve o conteúdo XML no corpo da mensagem com base em uma fonte de arquivo. É importante lembrar que o conteúdo do arquivo deverá ser um XML válido e utilizar os namespaces declarados na mensagem/corpo.

1. xml = Arquivo.novo('msg.xml', 'xml')
2. xml.fechar()
3.
4. servico.mensagem().corpo(xml)





#### cabecalho()


Retorna o [elemento](index.html#apiSoapMensagemElemento) do cabeçalho da mensagem.



#### cabecalho(conteudo)


Escreve o conteúdo XML no cabeçalho da mensagem. É importante lembrar que o conteúdo deverá ser um XML válido e utilizar os namespaces declarados na mensagem/corpo.

1. servico.mensagem().cabecalho('<ws:VerifyEmail><ws:email>teste@test.com</ws:email><ws:LicenseKey>example</ws:LicenseKey></ws:VerifyEmail>')





#### cabecalho(arquivo)


Escreve o conteúdo XML no cabecalho da mensagem com base em uma fonte de arquivo. É importante lembrar que o conteúdo do arquivo deverá ser um XML válido e utilizar os namespaces declarados na mensagem/corpo.

1. xml = Arquivo.novo('msg.xml', 'xml')
2. xml.fechar()
3.
4. servico.mensagem().cabecalho(xml)





#### operacao(operacao)


Define a operação/método/função a ser executada no webservice. Este valor será informado no cabeçalho HTTP SOAPAction da mensagem.



#### executar()


Executa a chamada ao método/função do serviço SOAP e retorna uma representação da [resposta](index.html#apiSoapResposta).



#### executar(operacao)


Executa a chamada ao método/função do serviço SOAP e retorna uma representação da [resposta](index.html#apiSoapResposta). Esta opção permite que o a operação à ser executada seja informada diretamente pela função executar() sem a necessidade de pré-definir o valor através da função operacao().



#### requisicao()


Retorna uma representação para leitura da requisição SOAP realizada. Esta leitor de mensagem contém as mesmas funcionalidades da [resposta](index.html#apiSoapResposta) e poderá ser utilizado para fins de depuração.



#### Elementos


Um elemento pode ser considerado como uma representação baseada em árvore para descrever uma informação na mensagem. Os elementos de uma mensagem (corpo, cabeçalho) SOAP utilizam o padrão XML.

As opções disponíveis para manipulação dos elementos são:

**nome()**

Retorna o nome do elemento.

**namespace()**

Retorna o [namespace](index.html#apiSoapServicoCriarNamespace) do elemento.

**adicionarElemento(nome)**

Adiciona/cria um novo elemento. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

1. elemEnderecos = servico.mensagem()
2.                        .corpo()
3.                        .adicionarElemento('endereco')
4.
5. elemEnderecos.adicionarElemento('residencial')
6. elemEnderecos.adicionarElemento('comercial')



O elemento _elemEnderecos_ irá produzir o seguinte XML na mensagem:

1. <endereco>
2.     <residencial></residencial>
3.     <comercial></comercial>
4. </endereco>



**adicionarElemento(nome, namespace, prefixo)**

Adiciona/cria um novo elemento informando também o namespace e prefixo de declaração do elemento. É importante lembrar que o namespace utilizado deve estar declarado na mensagem ou elemento pai. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarElemento(nome,[namespace](index.html#apiSoapServicoCriarNamespace))**

Adiciona/cria um novo elemento informando também o namespace de declaração do elemento. É importante lembrar que o namespace utilizado deve estar declarado na mensagem ou elemento pai. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarTexto(texto)**

Adiciona conteúdo do tipo texto à um elemento. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

1. elemEnderecos.adicionarElemento('residencial')
2.              .adicionarTexto('Rua geral')



produzirá:

1. <residencial>Rua geral</residencial>



**adicionarElementoTexto(nome, texto)**

Adiciona um novo elemento com conteúdo do tipo texto. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

1. elemEnderecos.adicionarElementoTexto('residencial', 'Rua geral')



produzirá:

1. <residencial>Rua geral</residencial>



**adicionarElementoTexto(nome, texto, namespace, prefixo)**

Adiciona um novo elemento com conteúdo do tipo texto indicando também o namespace e prefixo que o elemento está vinculado. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarElementoTexto(nome, texto,[namespace](index.html#apiSoapServicoCriarNamespace))**

Adiciona um novo elemento com conteúdo do tipo texto indicando também o namespace e prefixo que o elemento está vinculado. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarAtributo(nome, valor)**

Adiciona um novo atributo ao elemento atual. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

1. elemEnderecos.adicionarElemento('residencial')
2.              .adicionarAtributo('principal','N')



produzirá:

1. <residencial principal="N">Rua geral</residencial>



**adicionarAtributo(nome, valor, namespace, prefixo)**

Adiciona um novo atributo ao elemento atual indicando também o namespace e prefixo ao qual o atributo está vinculado. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarAtributo(nome, valor,[namespace](index.html#apiSoapServicoCriarNamespace))**

Adiciona um novo atributo ao elemento atual indicando também o namespace e prefixo ao qual o atributo está vinculado. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarNamespace(namespace, prefixo)**

Adiciona a declaração de um namespace ao elemento atual. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**adicionarNamespace([namespace](index.html#apiSoapServicoCriarNamespace))**

Adiciona a declaração de um namespace ao elemento atual. O retorno desta função é a representação do novo elemento criado e poderá ser utilizado para adicionar elementos filhos caso necessário.

**elementoAnterior()**

Utilizado para navegação entre os elementos criados de uma mesma família. Esta opção contém a representação do elemento pai do elemento corrente.

1. servico.mensagem()
2.        .corpo()
3.        .adicionarElemento('pessoas')
4.        .adicionarElementoTexto('nome', 'João')
5.        .elementoAnterior() //O elemento pai do elemento nome é pessoas
6.        .adicionarElementoTexto('nome', 'Maria')
7.



produzirá:

1. <pessoas>
2.     <nome>João</nome>
3.     <nome>Maria</nome>
4. </pessoas>



**contemElementoAnterior()**

Indica se o elemento atual possui um próximo elemento.

**proximoElemento()**

Utilizado para navegação entre os elementos criados de uma mesma família. Esta opção contém a representação do primeiro elemento filho do item corrente.

**contemProximoElemento()**

Indica se o elemento atual possui um elemento anterior.

1. elemPessoas = servico.mensagem()
2.                      .corpo()
3.                      .adicionarElemento('pessoas')
4.
5. imprimir elemPessoas.contemElementoAnterior() // true pois corpo() e cabecalho() são elementos da mensagem
6. imprimir elemPessoas.contemProximoElemento() // false
7.
8. elemPessoas.adicionarElementoTexto('nomePessoa', 'João')
9.
10. imprimir elemPessoas.contemProximoElemento() // true
11. elemPessoas.proximoElemento().nome() // nomePessoa





#### Métodos


Métodos são representações auxiliares para simplificar a montagem dos elementos da mensagem nos casos em que o webservice contém apenas parâmetros simples como entrada.

**_As opções disponíveis para criação de métodos a partir da mensagem são:_**

**metodo(operacao)**

Cria um novo método para a operação/função informado no parâmetro.

**metodo(operacao, namespace, prefixo)**

Cria um novo método utilizando a operação, namespace e prefixo informados nos parâmetros.

**metodo(operacao,[namespace](index.html#apiSoapServicoCriarNamespace))**

Cria um novo método utilizando a operação e [namespaces](index.html#apiSoapServicoCriarNamespace) informados nos parâmetros.

**Exemplo:**

1. metodoVerificaEmail = servico.mensagem().metodo('VerifyEmail')



**_As funções disponíveis na representação de métodos são:_**

**parametro(nome, valor)** Adiciona um parâmetro de entrada ao método atual.

**parametro(nome, valor, namespace)** Adiciona um parâmetro de entrada ao método atual utilizando o namespace informado.

**operacao()**

Retorna a operação do método atual.

**namespace()**

Retorna o namespace do método atual.

**elemento()**

Retorna o [elemento](index.html#apiSoapMensagemElemento) que representa o método atual.

**requisicao()**

Retorna uma representação para leitura da requisição SOAP realizada. Esta leitor de mensagem contém as mesmas funcionalidades da [resposta](index.html#apiSoapResposta) e poderá ser utilizado para fins de depuração.

**executar()**

Executa a chamada do método atual e retorna uma representação da [resposta](index.html#apiSoapResposta).

**mensagem()**

Retorna a representação da mensagem em que o método foi criado.

**Exemplo:**

1. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx',
2.                        'http://ws.cdyne.com/', 'ws')
3.
4. resposta = servico.mensagem()
5.                   .metodo('VerifyEmail')
6.                   .parametro('email', parametros.email.valor)
7.                   .parametro('LicenseKey', '123')
8.                   .executar()





### Resposta


Uma mensagem quando executada tem como retorno uma representação de resposta. Esta resposta pode ser processada/lida de maneiras distintas conforme necessidade.

As opções de processamento disponíveis são:



#### imprimir()


Imprime o conteúdo XML da resposta no console do editor de scripts.



#### conteudo()


Retorna o conteúdo XML da resposta no formato caracter.

1. resposta = servico.metodo('VerifyEmail')
2.        .parametro('email', parametros.email.valor)
3.        .parametro('LicenseKey', '123')
4.        .executar()
5.
6. imprimir resposta.conteudo()





#### arquivo()


Retorna uma fonte de arquivo que contém o conteúdo da resposta. Esta opção deverá ser utilizada em conjunto com as demais APIs da engine de scripts.

1. resposta = servico.metodo('VerifyEmail')
2.        .parametro('email', parametros.email.valor)
3.        .parametro('LicenseKey', '123')
4.        .executar()
5.
6. //Utilizando com a API de arquivos
7. xml = Arquivo.ler(resposta.arquivo(), 'xml')
8.
9. //Utilizando o retorno como anexo da API de Email
10. Email.novo()
11.      .de('webservice@betha.com.br')
12.      .para('usuarios@betha.com.br')
13.      .assunto('Arquivo de resposta do webservice!')
14.      .anexarArquivo(resposta.arquivo(), 'resposta.xml')
15.      .enviar()





#### xml()


Retorna um [leitor de arquivos XML da API de Arquivos](index.html#apiArquivosImplementacoesXml) para o conteúdo da resposta.

1. resposta = servico.metodo('VerifyEmail')
2.        .parametro('email', parametros.email.valor)
3.        .executar()
4.
5. xml = resposta.xml()
6. xml.proximoElemento('GoodEmail')
7.
8. se(xml.valor() == 'true'){
9.   imprimir 'O endereço ' + parametros.email.valor + ' é um e-mail válido!'
10. } senao {
11.   imprimir 'O endereço ' + parametros.email.valor + ' é inválido!'
12. }





#### anexos()


Retorna uma lista com os anexos presentes na mensagem de retorno do serviço.

1. retorno = servico.mensagem().corpo(xml).executar()
2. anexos = retorno.anexos()
3.
4. percorrer(anexos) {
5.     imprimir item.id()
6.     imprimir item.tipo()
7.     imprimir item.cabecalho("Content-Type") // mesmo valor do item.tipo()
8.
9.     arquivo = item.arquivo()
10. }





#### anexo(id)


Localiza e retorna um anexo de acordo com o seu id

1. retorno = servico.mensagem().corpo(xml).executar()
2.
3. anexo = retorno.anexo(xmlRetorno.atributo("href").valor());
4. Resultado.arquivo(anexo.arquivo());





### Base64


Base64 é um método para codificação de dados para transferência na Internet. É utilizado frequentemente para transmitir dados binários por meios de transmissão que lidam apenas com texto, como por exemplo para enviar arquivos anexos por e-mail. Uma abordagem muito comum, inclusive praticada por alguns tribunais de contas, é o uso do Base64 para envio de arquivos binários em webservices SOAP.

Segue um exemplo de como utilizar a API provida no BFCScript para este propósito:

1. textoCodificado = BaseCodec.padrao64().codifica('Meu texto').texto()
2. textoDecodificado = BaseCodec.padrao64().decodifica(textoCodificado).texto()



É possível codificar um arquivo zip gerado em um script:

1. xml = Arquivo.novo('teste.xml', 'xml', [indentar:'S'])
2.
3. xml.escreverInicioDocumento("UTF-8")
4. xml.escreverInicioElemento('root')
5.
6. xml.escreverComentario('Nomes dos colaboradores sem setor')
7. xml.escreverInicioElemento('nome')
8. xml.escreverAtributo('completo', 'N')
9. xml.escreverAtributo('composto', 'S')
10. xml.escreverTexto('Marcos da Silva')
11. xml.escreverFimElemento()
12.
13. xml.escreverInicioElemento('nome')
14. xml.escreverAtributo('completo', 'S')
15. xml.escreverTexto('Maria Joana Amaral')
16. xml.escreverFimElemento()
17.
18. xml.escreverInicioElemento('setor')
19. xml.escreverAtributo('nome', 'Desenvolvimento')
20. xml.escreverInicioElemento('pessoas')
21. xml.escreverElementoTexto('nome', 'Javanildo Soares')
22. xml.escreverFimElemento()
23. xml.escreverFimElemento()
24.
25. xml.escreverFimElemento()
26. xml.escreverFimDocumento()
27.
28. arquivo = Arquivo.novo('arquivo.zip', 'zip')
29. arquivo.adicionar(xml)
30.
31. arquivoCodificado = BaseCodec.padrao64().codifica(arquivo).texto()
32. arquivoDecodificado = BaseCodec.padrao64().decodifica(arquivoCodificado).texto()



Ou ainda codificar um arquivo recebido por parâmetro:

1. arquivoCodificado = BaseCodec.padrao64().codifica(parametros.arquivo.valor).texto()
2. arquivoDecodificado = BaseCodec.padrao64().decodifica(arquivoCodificado).texto()



É possível ainda definir o encoding para codificação e/ou decodificação (o encoding padrão é UTF-8):

1. textoCodificado = BaseCodec.padrao64().codifica('áé', 'iso-8859-1').texto()
2. textoDecodificado =  BaseCodec.padrao64().decodifica(textoCodificado).texto('iso-8859-1')



Também é possível decodificar para um arquivo de forma que o mesmo possa ser utilizado na API de Arquivos:

1. conteudoDecodificado = BaseCodec.padrao64().decodifica(zipCodificado)
2. zip = Arquivo.ler(conteudoDecodificado.arquivo(), 'zip')
3.
4. pecorrer(zip) { item ->
5. 	imprimir item.nome
6. }



A função BaseCodec está disponível ao usuário final apenas através da **Ferramenta de Scripts**.

**Atenção** : existe um limite cumulativo de **30MB** para codificar/decodificar conteúdo Base64 durante uma execução de script. A soma de todo o conteúdo processado deve ficar sempre abaixo deste limite. Lembrando que este limite incinde sobre a saída gerada pela API, e não sobre as entradas utilizadas.



#### Contornando a limitação cumulativa


Caso seja necessário codificar ou decodificar diversos conteúdos e esteja sendo esbarrado no limite cumulativo, pode-se utilizar métodos que não retornam como o resposta o conteúdo (não alocando no contexto global), e sim disponibilizam ele dentro de uma closure, que acaba liberando a memória alocada mais rapidamente:

1. input = 'Meu texto'; //poderia ser um arquivo
2. BaseCodec.padrao64().codifica(input) { conteudo ->
3.    imprimir conteudo.texto();
4. }
5.
6. inputEncoded = 'YWJjZGVmZ2hp'; //poderia ser um arquivo
7. BaseCodec.padrao64().decodifica(inputEncoded) { conteudo ->
8.    imprimir conteudo.texto();
9. }



Fazendo o uso dessas chamadas, o limite passa a ser de 30mb de forma individual e não descontando do limite cumulativo global.

**É recomendado que não se atríbua essa variável interna para um contexto maior, permitindo assim que a memória alocada seja liberada**



### Hash


Uma função de hash pode ser utilizada para verificar a integridade de arquivos, uma vez que uma hash é gerada com base em um texto ou arquivo, não existe uma maneira de fazer o caminho contrário. Uma abordagem muito comum, inclusive praticada por alguns tribunais de contas, é o uso de verificações de integridade de arquivos binários enviados em webservices SOAP.

Existem alguns algoritmos popularmente utilizados para gerar uma hash de algo, são eles MD5, SHA-1, SHA-256 e SHA-512:

**padraoMD5()**

1. hashMD5 = Hash.padraoMD5().codifica("qualquer texto").texto()



Quando utilizado um texto, é possível definir o charset para codificação (o charset padrão é UTF-8):

1. hashMD5 = Hash.padraoMD5().codifica("ë", "iso-8859-1").texto()



Quando utilizado um arquivo, não é possível definir o charset para codificação, o charset utilizado é o do arquivo:

1. xml = Arquivo.novo('teste.xml', 'xml', [indentar:'S'])
2.
3. xml.escreverInicioDocumento("UTF-8")
4. xml.escreverInicioElemento('root')
5.
6. xml.escreverComentario('Nomes dos colaboradores sem setor')
7. xml.escreverInicioElemento('nome')
8. xml.escreverAtributo('completo', 'N')
9. xml.escreverAtributo('composto', 'S')
10. xml.escreverTexto('Marcos da Silva')
11. xml.escreverFimElemento()
12.
13. xml.escreverInicioElemento('nome')
14. xml.escreverAtributo('completo', 'S')
15. xml.escreverTexto('Maria Joana Amaral')
16. xml.escreverFimElemento()
17.
18. xml.escreverInicioElemento('setor')
19. xml.escreverAtributo('nome', 'Desenvolvimento')
20. xml.escreverInicioElemento('pessoas')
21. xml.escreverElementoTexto('nome', 'Javanildo Soares')
22. xml.escreverFimElemento()
23. xml.escreverFimElemento()
24.
25. xml.escreverFimElemento()
26. xml.escreverFimDocumento()
27.
28. hashMD5 = Hash.padraoMD5().codifica(xml).texto()



**padraoSHA1()**

1. hashSHA1 = Hash.padraoSHA1().codifica("qualquer texto").texto()



Quando utilizado um texto, é possível definir o charset para codificação (o charset padrão é UTF-8):

1. hashSHA1 = Hash.padraoSHA1().codifica("ë", "iso-8859-1").texto()



Quando utilizado um arquivo, não é possível definir o charset para codificação, o charset utilizado é o do arquivo:

1. imprimir Hash.padraoSHA1().codifica(parametros.arquivo.valor).texto()



**padraoSHA256()**

1. hashSHA256 = Hash.padraoSHA256().codifica("qualquer texto").texto()



Quando utilizado um texto, é possível definir o charset para codificação (o charset padrão é UTF-8):

1. hashSHA256 = Hash.padraoSHA256().codifica("ë", "iso-8859-1").texto()



Quando utilizado um arquivo, não é possível definir o charset para codificação, o charset utilizado é o do arquivo:

1. zip = Arquivo.novo('arquivos.zip', 'zip');
2.
3. zip.adicionar(parametros.arquivo.valor, 'teste.xml');
4.
5. imprimir Hash.padraoSHA256().codifica(zip).texto()
6.



**padraoSHA512()**

1. hashSHA512 = Hash.padraoSHA512().codifica("qualquer texto").texto()



Quando utilizado um texto, é possível definir o charset para codificação (o charset padrão é UTF-8):

1. hashSHA512 = Hash.padraoSHA512().codifica("ë", "iso-8859-1").texto()



Quando utilizado um arquivo, não é possível definir o charset para codificação, o charset utilizado é o do arquivo:

1. zip = Arquivo.novo('arquivos.zip', 'zip');
2.
3. zip.adicionar(parametros.arquivo.valor, 'teste.xml');
4.
5. imprimir Hash.padraoSHA512().codifica(zip).texto()



**padraoHex()**

1. hexadecimal = Hash.padraoHex().codifica("qualquer texto").texto()



Quando utilizado um texto, é possível definir o charset para codificação (o charset padrão é UTF-8):

1. hexadecimal = Hash.padraoHex().codifica("ë", "iso-8859-1").texto()



Quando utilizado um arquivo, não é possível definir o charset para codificação, o charset utilizado é o do arquivo:

1. zip = Arquivo.novo('arquivos.zip', 'zip');
2.
3. zip.adicionar(parametros.arquivo.valor, 'teste.xml');
4.
5. imprimir Hash.padraoHex().codifica(zip).texto()
6.





### Exemplos


**Exemplo 1:**

1. servico = Soap.servico('http://ws.cdyne.com/emailverify/Emailvernotestemail.asmx',
2.                        'http://ws.cdyne.com/', 'ws')
3.
4. resposta = servico.mensagem()
5.                   .metodo('VerifyEmail')
6.                   .parametro('email', parametros.email.valor)
7.                   .parametro('LicenseKey', '123')
8.                   .executar()
9.
10. xml = resposta.xml()
11. xml.proximoElemento('GoodEmail')
12.
13. se(xml.valor() == 'true'){
14.   imprimir 'O endereço ' + parametros.email.valor + ' é um e-mail válido!'
15. } senao {
16.   imprimir 'O endereço ' + parametros.email.valor + ' é inválido!'
17. }



**Exemplo 2:**

1. servico = Soap.servico('https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS',
2.                        'http://publico.ws.casosdeuso.sgs.pec.bcb.gov.br', 'ws')
3.
4. resposta = servico.mensagem()
5.                   .metodo('getUltimoValorVO')
6.                   .parametro('in0', '1')
7.                   .executar()
8.
9. xml = resposta.xml()
10. xml.proximoElemento('svalor')
11.
12. notificacao = 'A cotação do dolar para hoje é de R$ ' + Caracteres.substituir(xml.valor(), '.', ',')
13.
14. Notificacao.nova()
15.            .mensagem(notificacao)
16.            .para('usuario')
17.            .enviar()



**Exemplo 3:**

1. servico = Soap.servico('https://demo.voxtecnologia.com.br/servicos/ws-consulta-previa-localizacao',
2.                        'https://demo.voxtecnologia.com.br/servicos/ws-consulta-previa-localizacao', 'ws')
3.
4. mensagem = servico.mensagem()
5. elemDadosConsulta = mensagem.corpo().adicionarElemento('dadosConsultaPreviaLocalizacao')
6. elemMensagem = elemDadosConsulta.adicionarElemento('mensagem')
7.
8. elemMensagem.adicionarElemento('controle')
9.             .adicionarElementoTexto('hash', '6cd61adb859800aa565d97290f798e01')
10.             .elementoAnterior()
11.             .adicionarElementoTexto('categMens', 'dadosConsultaPreviaLocalizacao')
12.             .elementoAnterior()
13.             .adicionarElementoTexto('data', '2015-10-28 09:54:44')
14.             .elementoAnterior()
15.             .adicionarElementoTexto('versao', '1.0')
16.
17. elemMensagem.adicionarElemento('dadosConsultaPreviaLocalizacao')
18.             .adicionarElementoTexto('co_protocolo', 'PRP1512623548')
19.             .elementoAnterior()
20.             .adicionarElementoTexto('dt_evento', '2016-05-23 12:00:00')
21.             .elementoAnterior()
22.             .adicionarElementoTexto('is_indeferido', 'false')
23.
24. resposta = mensagem.executar()
25.
26. email = Email.novo()
27.              .de('remetente@betha.com.br')
28.              .para('destinatario@betha.com.br')
29.              .assunto('Arquivo de resposta do webservice!')
30.              .mensagem('Segue arquivo em anexo do retorno do webservice')
31.              .anexarArquivo(mensagem.requisicao().arquivo(), 'envio.xml')
32.              .anexarArquivo(resposta.arquivo(), 'resposta.xml')
33.              .enviar()



**Exemplo 4:**

Armazenar o retorno em formato de anexo de um serviço.

1. xml = """
2.       <ser:entregarManifestacaoProcessual>
3.          <tip:idManifestante></tip:idManifestante>
4.          <tip:senhaManifestante></tip:senhaManifestante>
5.          <tip:numeroProcesso></tip:numeroProcesso>
6. 	 <tip:documento idDocumento="27" tipoDocumento="13" mimetype="application/pdf" descricao="Petição Inicial" tipoDocumentoLocal="14">
7. 	 	<int:conteudo></int:conteudo>
8. 	 </tip:documento>
9. 	 	<tip:documento idDocumento="28" tipoDocumento="14" mimetype="application/pdf" descricao="Petição Inicial" tipoDocumentoLocal="14">
10. 	 	<int:conteudo></int:conteudo>
11.  		</tip:documento>
12.          <tip:dataEnvio></tip:dataEnvio>
13.       </ser:entregarManifestacaoProcessual>
14. """;
15.
16. imprimir xml;
17.
18. servico = Soap.servico("https://eproc1ghml.tjsc.jus.br/homologa1g/ws/controlador_ws.php?srv=intercomunicacao2.2",
19.             "http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/", "ser")
20.
21. retorno = servico.mensagem()
22.                 .namespace("http://www.cnj.jus.br/tipos-servico-intercomunicacao-2.2.2", "tip")
23.                 .namespace("http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/", "ser")
24.   				.namespace("http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/", "int")
25.                 .corpo(xml)
26.                 .executar()
27.
28. xmlRetorno = retorno.xml()
29.
30. se (xmlRetorno.proximoElemento("Body") && xmlRetorno.proximoElemento("entregarManifestacaoProcessualResposta") && xmlRetorno.proximoElemento("recibo") && xmlRetorno.proximoElemento("Include")) {
31.   anexo = retorno.anexo(xmlRetorno.atributo("href").valor());
32.   Resultado.arquivo(anexo.arquivo());
33. }
34.
35. imprimir retorno.conteudo()





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





## API de HTTP


O bfc-script disponibiliza uma API para consumo de serviços web HTTP. Essas funções estarão disponíveis ao usuário final apenas através da **Ferramenta de Scripts** , e serão absorvidas plenamente conforme a utilização.

A API conta com algumas representações básicas de funcionamento sendo elas a **Requisição** e a **Resposta**. A **Requisição** trata-se da definição de uma ou várias chamadas à um serviço HTTP comum, cada interação com esse serviço é realizado através dos métodos/verbos padrões do HTTP. O produto desta interação quando executada é uma **Resposta** , essa resposta pode ser transformada em vários tipos e saídas, sendo elas um JSON no formato de Mapa (quando a resposta do serviço for JSON), Uma fonte de arquivo para utilização em conjunto com outras APIs (E-mail, Arquivos), O conteúdo da resposta no formato de texto em sí ou simplesmente a impressão da resposta no console do script.

![Fluxo da API de HTTP](images/fluxo-api-http.png)



### Requisição


Para criar uma nova requisição HTTP deve-se utilizar a função Http.**servico** , a função recebe como parâmetro a URL do serviço a ser consumido:

1. servico = Http.servico('https://jsonplaceholder.typicode.com/posts')



A URL informada pode conter marcadores, estes marcadores serão substituídos por um determinado valor no momento da execução de um método HTTP.

1. servico = Http.servico('https://jsonplaceholder.typicode.com/posts/{ano}/{id}')



As opções disponíveis na API para interagir com um serviço são:



#### cookie(nome, valor)


Adiciona um cookie na requisição HTTP.



#### cookie(nome, valor, caminho, domínio, versão)


Adiciona um cookie na requisição HTTP informando também o caminho/path, domínio e versão do cookie.



#### cookie(Mapa[nome, valor])


Adiciona um ou vários cookies (nome/valor) na requisição HTTP com base em uma mapa.

1. servico = Http.servico('https://jsonplaceholder.typicode.com/posts')
2. servico.cookie('Usuario', 'João da Silva')
3. servico.cookie('Usuario', 'João da Silva', '/usuarios', 'betha.com.br', 1)
4. servico.cookie([ Usuario: 'João da Silva', Accesso: 'sim' ])





#### cabecalho(nome, valor)


Adiciona um cabeçalho/header na requisição HTTP.



#### cabecalho(nome, lista de valores)


Adiciona um cabeçalho/header com vários valores na requisição HTTP.



#### cabecalho(Mapa[nome, valor])


Adiciona um ou vários cabeçalhos/headers (nome/valor) na requisição HTTP com base em uma mapa.

1. servico.cabecalho('Authorization', 'Basic ABCF5065FGC==')
2. servico.cabecalho('User', ['murphy', 'luiz.silva'])
3. servico.cabecalho([ User: 'alex.o.leao'])



**Parâmetros e caminhos**

Para permitir que um mesmo serviço atenda as mais diversas situações encontradas em APIs HTTP, as funções caminho() e parametro() possuem um comportamento diferenciado das demais. Estas funções quando executadas criam uma cópia da requisição atual adicionado os respectivos parâmetro(s)/caminho(s). Desta forma a requisição original não é alterada e pode ser reutilizada para outras invocações no mesmo serviço.

Exemplo:

1. servico = Http.servico('https://jsonplaceholder.typicode.com')
2.
3. //Gera uma chamada GET ao endereço https://jsonplaceholder.typicode.com/posts?id=5
4. servico.caminho('posts')
5.        .parametro('id', 5)
6.        .GET()
7.
8. //Gera uma chamada GET ao endereço https://jsonplaceholder.typicode.com/users/admins?id=5
9. servico.caminho('users')
10.        .caminho('admins')
11.        .parametro('id', 2)
12.        .GET()
13.
14. //Caso se deseje alterar a requisição original basta associar a cópia ao serviço original, desta forma
15. //todas as requisições criadas à partir deste serviço utilizaram estes caminhos
16. servico = servico.caminho('users')
17.                  .caminho('admins')
18.
19. //Gera uma chamada GET ao endereço https://jsonplaceholder.typicode.com/users/admins/ativos?id=5
20. servico.caminho('ativos')
21.        .parametro('id', 5)
22.        .GET()





#### parametro(nome, valor)


Cria uma cópia da requisição atual adicionando um parâmetro de query.



#### parametro(nome, lista de valores)


Cria uma cópia da requisição atual adicionando um ou mais parâmetros de query na requisição.



#### parametro(Mapa[nome, valor])


Cria uma cópia da requisição atual adicionando um ou mais parâmetros de query na requisição com base no mapa informado no parâmetro.

1. servico.parametro('id', '1') //posts?id=1
2. servico.parametro('id', ['1', '2', '5']) //posts?id=1&id=2&id=5
3. servico.parametro([ id: '5', nome: 'joao']) //posts?id=1&nome=joao



1. servico = Http.servico(...)
2. servico.parametro('id', 1)
3. servico.parametro('id', 2)
4.
5. imprimir servico.parametros() //[] - Vazio pois como cria uma cópia o serviço original não é alterado
6. servico = servico.parametro('id', 1)
7.                  .parametro('id', 2)
8.
9. imprimir servico.parametros() //[id : [1,2]] - pois atribuímos a cópia o serviço original





#### caminho(caminho)


Cria uma cópia da requisição atual adicionando um caminho/path na URL corrente.

1. servico = Http.servico('https://jsonplaceholder.typicode.com')
2.
3. servico.caminho('posts')
4.        .caminho('listar') //URL: https://jsonplaceholder.typicode.com/posts/listar





#### aceitarTipoMidia(midias)


Informa qual tipo de mídia é aceito pela requisição. O valor padrão é Http.TODOS.

1. servico.aceitarTipoMidia('application/json')



A API conta com algumas constantes para os tipos de mídia comuns:

* Http.JSON: _application/json_
* Http.XML: _application/xml_
* Http.TEXTO_XML: _text/xml_
* Http.XHTML: _application/xhtml+xml_
* Http.TEXTO_HTML: _text/html_
* Http.TEXTO: _text/plain_
* Http.FORMULARIO: _application/x-www-form-urlencoded_
* Http.MULTIPART: _multipart/form-data_
* Http.ARQUIVO: _application/octet-stream_
* Http.TODOS: _*/*_
1. servico.aceitarTipoMidia(Http.JSON)
2. servico.aceitarTipoMidia([Http.JSON, Http.XML])





#### credenciais(usuario, senha)


Configura a autenticação básica HTTP no serviço.

1. servico.credenciais('user', '123')





#### tempoLimite(valor)


Define o tempo limite para requisições executadas a partir do serviço. O valor deve ser informado em milissegundos.

1. // define timeout de 30 segundos
2. servico.tempoLimite(30000)





#### GET (Mapa[marcadores])


Executa uma chamada do tipo GET ao serviço retornando uma representação de resposta.

1. resposta = Http.servico('https://www.betha.com.br/users').GET()
2.
3. svcUsuarios = Http.servico('https://www.betha.com.br/usuarios/{uf}/{nome}')
4. svcUsuarios.GET([uf: 'SC', nome: 'joao'])
5. svcUsuarios.GET([uf: 'SP', nome: 'maria'])





#### OPTIONS (Mapa[marcadores])


Executa uma chamada do tipo OPTIONS ao serviço retornando uma representação de resposta.

1. resposta = Http.servico('https://www.betha.com.br/users').OPTIONS()





#### HEAD (Mapa[marcadores])


Executa uma chamada do tipo HEAD ao serviço retornando uma representação de resposta.

1. resposta = Http.servico('https://www.betha.com.br/users').HEAD()





#### TRACE (Mapa[marcadores])


Executa uma chamada do tipo TRACE ao serviço retornando uma representação de resposta.

1. resposta = Http.servico('https://www.betha.com.br/users').TRACE()





#### DELETE ()




#### DELETE (Mapa[marcadores])




#### DELETE (dados, Mapa[marcadores])




#### DELETE (dados, Tipo de mídia)




#### DELETE (dados, Tipo de mídia, Mapa[marcadores])


Executa uma chamada do tipo DELETE ao serviço retornando uma representação de resposta. Os dados da requisição são enviados conforme tipo de mídia informado no parâmetro sendo Http.JSON (_application/json_) o valor padrão.

1. dados = [
2.     id: "5",
3.     author: "Uncle Bob",
4. ]
5.
6. resposta = Http.servico('https://www.betha.com.br/users').DELETE()
7. resposta = Http.servico('https://www.betha.com.br/users/{id}').DELETE([id: '5'])
8. resposta = Http.servico('https://www.betha.com.br/users/{id}').DELETE(dados, [id: '5'])
9. resposta = Http.servico('https://www.betha.com.br/users/{id}').DELETE(dados, Http.JSON)
10. resposta = Http.servico('https://www.betha.com.br/users/{id}').DELETE(dados, Http.JSON, [id: '5'])





#### POST (dados)




#### POST (dados, Mapa[marcadores])




#### POST (dados, Tipo de mídia)




#### POST (dados, Tipo de mídia, Mapa[marcadores])




#### POST (formulário)




#### POST (formulário, Mapa[marcadores])


Executa uma chamada do tipo POST ao serviço retornando uma representação de resposta. Os dados/formulário da requisição são enviados conforme tipo de mídia informado no parâmetro sendo Http.JSON (_application/json_) o valor padrão.

1. conteudo = [
2.     title: "The rabbit in the topper",
3.     author: "Mr. M",
4. ]
5.
6. resposta = Http.servico('https://www.betha.com.br/users')
7.                .POST(conteudo, Http.JSON)
8.
9. resposta = Http.servico('https://www.betha.com.br/users')
10.                .POST('{"nome":"Test"}', Http.JSON)
11.
12. resposta = Http.servico('https://www.betha.com.br/users/{id}')
13.                .POST(conteudo, Http.JSON, [id: 5])





#### PUT (dados)




#### PUT (dados, Mapa[marcadores])




#### PUT (dados, Tipo de mídia)




#### PUT (dados, Tipo de mídia, Mapa[marcadores])




#### PUT (formulário)




#### PUT (formulário, Mapa[marcadores])


Executa uma chamada do tipo PUT ao serviço retornando uma representação de resposta. Os dados/formulário da requisição são enviados conforme tipo de mídia informado no parâmetro sendo Http.JSON (_application/json_) o valor padrão.

1. conteudo = [
2.     title: "The rabbit in the topper",
3.     author: "Mr. M",
4. ]
5.
6. resposta = Http.servico('https://www.betha.com.br/users')
7.                .PUT(conteudo, Http.JSON)
8.
9. resposta = Http.servico('https://www.betha.com.br/users')
10.                .PUT('{"nome":"Test"}', Http.JSON)
11.
12. resposta = Http.servico('https://www.betha.com.br/users/{id}')
13.                .PUT(conteudo, Http.JSON, [id: 5])





#### PATCH (dados)




#### PATCH (dados, Mapa[marcadores])




#### PATCH (dados, Tipo de mídia)




#### PATCH (dados, Tipo de mídia, Mapa[marcadores])




#### PATCH (formulário)




#### PATCH (formulário, Mapa[marcadores]


Executa uma chamada do tipo PATCH ao serviço retornando uma representação de resposta. Os dados/formulário da requisição são enviados conforme tipo de mídia informado no parâmetro sendo Http.JSON (_application/json_) o valor padrão.

1. conteudo = [
2.     title: "The rabbit in the topper",
3.     author: "Mr. M",
4. ]
5.
6. resposta = Http.servico('https://www.betha.com.br/users')
7.                .PATCH(conteudo, Http.JSON)
8.
9. resposta = Http.servico('https://www.betha.com.br/users')
10.                .PATCH('{"nome":"Test"}', Http.JSON)
11.
12. resposta = Http.servico('https://www.betha.com.br/users/{id}')
13.                .PATCH(conteudo, Http.JSON, [id: 5])





#### METODO (método)




#### METODO (Mapa[marcadores], método)




#### METODO (método, dados)




#### METODO (método, dados, Mapa[marcadores])




#### METODO (método, tipo de mídia)




#### METODO (método, dados, tipo de mídia)




#### METODO (método, dados, tipo de mídia, Mapa[marcadores])




#### METODO (formulário)




#### METODO (formulário, Mapa[marcadores]


A função METODO é utilizada para realizar chamadas utilizando métodos personalizados. Tem como retorno uma representação de resposta. Os dados/formulário da requisição quando existentes são enviados conforme tipo de mídia informado no parâmetro sendo Http.JSON (_application/json_) o valor padrão.

1. dados = [
2.     title: "The rabbit in the topper",
3.     author: "Mr. M",
4. ]
5.
6. resp = Http.servico('https://www.betha.com.br/users')
7.            .METODO('GET'); //GET sem corpo
8.
9. resp = Http.servico('https://www.betha.com.br/users/{id}')
10.            .METODO([id: 'joao'], 'GET'); //Marcadores de URL
11.
12. resp = Http.servico('https://www.betha.com.br/users')
13.            .METODO('POST', dados)





#### Formulários


Para permitir o uso de serviços web onde os dados são recebidos no formato de formulários (form), a API conta com os seguintes facilitadores:



##### Formulario


Para criar um novo formulário de dados deve-se utilizar as funções **criarFormulario()** ou **criarFormulario(tipo de mídia formulário)**. Estas funções criam um novo formulário utilizando como tipo de mídia o valor Http.FORMULARIO (application/x-www-form-urlencoded). A mídia pode ser alterada informando no parâmetro da função o tipo de mídia desejada.

1. servico = Http.servico('https://www.betha.com.br/users')
2. formulario = servico.criarFormulario()





###### parametro(nome, valor)


Adiciona um parâmetro ao formulário atual.

1. formulario = servico.criarFormulario()
2.                     .parametro("nome", "Betha")





###### parametro(Mapa[nome, valor])


Adiciona um ou mais parâmetros ao formulário atual bom base em uma mapa.

1. parametros = [nome: "Betha", site: "www.betha.com.br"]
2.
3. formulario = servico.criarFormulario()
4.                     .parametro(parametros)





###### POST()




###### POST(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo POST.

1. parametros = [nome: "Betha", site: "www.betha.com.br"]
2.
3. resposta  = servico.criarFormulario()
4.                     .parametro(parametros)
5.                     .POST()





###### PUT()




###### PUT(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo POST.

1. resposta  = servico.criarFormulario().PUT()





###### PATCH()




###### PATCH(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo POST.

1. resposta  = servico.criarFormulario().PATCH()





###### METODO(método)




###### METODO(método, Mapa[marcadores])


Envia o formulário utilizando como tipo de método um valor personalizado.

1. resposta  = servico.criarFormulario().METODO('POST')





##### Formulario Multipart


Para criar um novo formulário multipart deve-se utilizar as funções **criarFormularioMultipart()** ou **criarFormularioMultipart(tipo de mídia formulário)**. Estas funções criam um novo formulário multipart utilizando como tipo de mídia o valor Http.MULTIPART (multipart/form-data). A mídia padrão pode ser alterada informando no parâmetro da função o tipo de mídia desejada.

Formulários multipart geralmente são utilizados para envio de dados e arquivos (upload) em um requisição.

1. servico = Http.servico('https://www.betha.com.br/users')
2. formulario = servico.criarFormularioMultipart()





###### parametro (nome, valor)




###### parametro (nome, valor, tipo de mídia)




###### parametro (Mapa[nome:valor])




###### parametro (Mapa[nome:valor])


Adiciona um ou mais parâmetro(s) ao formulário atual. Este parâmetro pode conter um tipo de mídia diferente ao do formulário.

1. servico = Http.servico('https://www.betha.com.br/users')
2. formulario = servico.criarFormularioMultipart()
3.                     .parametro("nome", "João")
4.                     .parametro("foto", arquivo, Http.ARQUIVO) //Fonte de arquivo da API de arquivos
5.                     .parametro([nome: "Betha", site: "www.betha.com.br"]) //valores baseados em um mapa





###### POST()




###### POST(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo POST.

1. resposta  = servico.criarFormularioMultipart().POST()





###### PUT()




###### PUT(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo PUT.

1. resposta  = servico.criarFormularioMultipart().PUT()





###### PATCH()




###### PATCH(Mapa[marcadores])


Envia o formulário utilizando como tipo de método o verbo PATCH.

1. resposta  = servico.criarFormularioMultipart().PATCH()





###### METODO(método)




###### METODO(método, Mapa[marcadores])


Envia o formulário utilizando como tipo de método um valor personalizado.

1. resposta  = servico.criarFormularioMultipart().METODO('POST')





### Resposta


Uma chamada à um serviço web quando executada tem como retorno uma representação de resposta. Esta resposta pode ser processada/lida de maneiras distintas conforme necessidade.

As opções disponíveis são:



#### codigo()


Retorna o código HTTP da resposta.

1. resposta = ...
2.
3. se (resposta.codigo() == 404) {
4.     imprimir 'Servidor não encontrado';
5. }





#### tipoMidia()


Retorna o tipo de mídia da resposta

1. imprimir 'A resposta é do tipo ' + resposta.tipoMidia()





#### ehJson()


Indica se o tipo de mídia da resposta é do tipo JSON

1. se (resposta.ehJson()){
2.     imprimir 'A resposta é um JSON'
3. }





#### sucesso()


Indica se o código resposta é considerado como sucesso segundo o padrão HTTP.

1. se (resposta.sucesso()){
2.     imprimir 'Tudo OK com a chamada HTTP'
3. }





#### tamanho()


Retorna o tamanho do conteúdo segundo o cabeçalho da resposta (Content-Length) recebido. Caso o valor não seja retornado pelo servidor ou seja inválido retorna -1.



#### contemResultado()


Indica se a requisição retornou algum resultado. Esta verificação é realizada com base no conteudo() e no tamanho() da mensagem e pode ou não estar presente dependendo de cada serviço utilizado.



#### ultimaModificacao()


Retorna a data da ultima modificação do resultado. Este valor é obtido do resultado da requisição e pode ou não estar presente dependendo de cada serviço utilizado.



#### cookie(nome)


Recupera um cookie da resposta com base no nome. Um cookie pode conter as seguintes informações:

* **nome()** : Nome do cookie
* **valor()** : Valor do cookie
* **valorCodificado()** : Valor do cookie codificado no padrão URL
* **valorDecodificado()** : Valor do cookie no padrão URL decodificado
* **caminho()** : Caminho/Path do cookie
* **dominio()** : Domínio do cookie
* **versao()** : Versão do cookie (número)
* **comentario()** : Comentário do cookie
* **idadeLimite()** : Idade limite/tempo de duração do cookie (maxAge)
* **expira()** : Data de expiração do cookie
* **ehSeguro()** : Indica se é seguro
* **ehSomenteHttp()** : Indica se é somente HTTP
1. usaEnterComoTab = resposta.cookie('UsaEnterComoTab')
2. imprimir 'O usuário utiliza enter como TAB: ' + usaEnterComoTab.valor()





#### contemCookie(nome)


Indica se a resposta contém um cookie com o nome informado no parâmetro.



#### cookies()


Recupera uma lista contendo os cookies retornados na resposta.

1. percorrer(resposta.cookies()){
2.     imprimir item.nome() + ':' + item.valor()
3. }





#### cabecalho(nome)


Recupera um cabeçalho(Header) da resposta com base no nome. Um cabeçalho poder conter as seguintes informações:

* **nome()** : Nome do cabeçalho
* **valores()** : Uma lista contendo todos os valores do cabeçalho
* **valor()** : O primeiro valor encontrado do cabeçalho
1. imprimir resposta.cabecalho('Authorization').valor()





#### contemCabecalho(nome)


Indica se a resposta contém um cabeçalho (Header) com o nome informado no parâmetro.



#### cabecalhos()


Recupera uma lista contendo os cabeçalhos retornados na resposta.

1. percorrer(resposta.cabecalhos()){
2.     imprimir item.nome() + ':' + item.valor()
3. }





#### cookie(nome)


Retorna o cookie (caso definido)

1. resposta.cookie('nome').valor();





#### imprimir()


Imprime o conteúdo da resposta no console do editor de scripts.



#### conteudo()


Retorna o conteúdo da resposta no formato de caracteres.

1. resposta = Http.servico('https://www.betha.com.br/users').GET()
2. imprimir resposta.conteudo()





#### arquivo()


Retorna uma fonte de arquivo que contém o conteúdo da resposta. Esta opção deverá ser utilizada em conjunto com as demais APIs da engine de scripts.

1. resposta = Http.servico('https://www.betha.com.br/users').GET()
2.
3. //Utilizando com a API de arquivos
4. texto = Arquivo.ler(resposta.arquivo(), 'txt')
5.
6. //Utilizando o retorno como anexo da API de Email
7. Email.novo()
8.      .de('webservice@betha.com.br')
9.      .para('usuarios@betha.com.br')
10.      .assunto('Arquivo de resposta do webservice!')
11.      .anexarArquivo(resposta.arquivo(), 'resposta.txt')
12.      .enviar()





#### json()


Retorna o resultado de uma serviço JSON como Mapa/Lista de mapa.

1. resposta = Http.servico('https://www.betha.com.br/users/5').GET()
2.
3. json = resposta.json()
4.
5. imprimir json.id
6. imprimir json.nome
7.





## API de Assinatura


A assinatura de um documento por meio do script pode ser feita por arquivo ou por lote, apenas documentos xml e pdf podem ser assinados. Todo processo de assinatura envolve a criação de dois scripts, um para chamada da api de assinatura e outro de callback que é executado após a assinatura e pode receber o arquivo assinado e o arquivo original como parâmetro.

* **Observação:** Para assinar qualquer documento, é necessário que a ferramenta de assinatura esteja rodando na maquina do usuário.
### Assinando Documento


Exemplo de script de assinatura de um documento pdf:



###### assinar(arquivo, opcoes)


1. arquivo = parametros.arquivo.valor;
2.
3. opcoes = [
4.     nome: 'pdfassinado', // nome do arquivo enviado por parâmetro para o script de callback
5.     tipo: 'pdf',
6.     lote: false,  // indica se é lote ou não
7.     retorno: [
8.         script: 'callback_assinatura',  // identificador do script de callback que deve ser executado após assinar o documento/lote
9.         parametro: 'assinado', // nome do parâmetro do tipo arquivo no script de callback que recebe o arquivo assinado
10.         notificacao: true
11.     ],
12.     parametros: [
13.         original: arquivo
14.     ]
15. ];
16.
17. Assinador.assinar(arquivo, opcoes);



Exemplo de script de assinatura de um documento xml:

1. arquivo = parametros.arquivo.valor;
2.
3. opcoes = [
4.     nome: 'xmlassinado', // nome do arquivo enviado por parâmetro para o script de callback
5.     tipo: 'xml',
6.     lote: false,  // indica se é lote ou não
7.     tagAssinatura: 'TEXTO', // nome da tag do xml que deve ser assinada
8.     retorno: [
9.         script: 'callback_assinatura',  // identificador do script de callback que deve ser executado após assinar o documento/lote
10.         parametro: 'assinado', // nome do parâmetro do tipo arquivo no script de callback que recebe o arquivo assinado
11.         notificacao: true
12.     ],
13.     parametros: [
14.         original: arquivo
15.     ]
16. ];
17.
18. Assinador.assinar(arquivo, opcoes);





### Assinando lote de documentos


Exemplo de script de assinatura de um lote de documentos xml:



###### assinar(arquivo, opcoes)


1. arquivo = parametros.arquivo.valor;
2. zip = Arquivo.novo('arquivos.zip', 'zip');
3. zip.adicionar(arquivo, 'a.xml');
4. zip.adicionar(arquivo, 'b.xml');
5.
6. opcoes = [
7.     nome: 'xmlassinado', // nome do arquivo enviado por parâmetro para o script de callback
8.     tipo: 'xml',
9.     lote: true,  // indica se é lote ou não
10.     tagAssinatura: 'TEXTO', // nome da tag do xml que deve ser assinada
11.     retorno: [
12.         script: 'callback_assinatura',  // identificador do script de callback que deve ser executado após assinar o documento/lote
13.         parametro: 'assinado', // nome do parâmetro do tipo arquivo no script de callback que recebe o arquivo assinado
14.         notificacao: true
15.     ],
16.     parametros: [
17.         original: zip
18.     ]
19. ];
20.
21. Assinador.assinar(zip, opcoes);





### Múltiplos assinantes


Exemplo de script de assinatura de um documento PDF com múltiplos assinantes:

* **Observação:** Apenas documentos do tipo PDF podem utilizar o recurso de múltiplos assinantes.
###### assinar(arquivo, opcoes)


1. arquivo = parametros.arquivo.valor;
2.
3. opcoes = [
4.     nome: 'pdfassinado',
5.     tipo: 'pdf',
6.     lote: false,
7.     assinantes: [
8.         incluirUsuarioCorrente: true, //indica se o usuário que solicitou a execução do script deve assinar o documento
9.         usuarios: [ // lista de assinantes
10.             'joao',
11.             'maria.silva'
12.         ]
13.     ],
14.     retorno: [
15.         script: 'callback_assinatura',
16.         parametro: 'assinado',
17.         notificacao: true
18.     ],
19.     parametros: [
20.         original: arquivo
21.     ]
22. ];
23.
24. Assinador.assinar(arquivo, opcoes);





### Script de callback


O script de callback é o script executado automaticamente após o a execução do script que chama a api de assinatura com Assinador.assinar(arquivo, opcoes).

Com base no script de assinatura do exemplo anterior, o script de callback deve ter dois parâmetros do tipo arquivo, que são:

* **assinado** que foi definido no script de assinatura no item retorno.parametro do objeto de opcoes
* **original** que também foi definido no script de assinatura no item parametros do objeto de opcoes
E por último o identificador que também foi definido no script de assinatura no item script do objeto de opcoes



## API de Critério




### Criação


A criação de um novo critério acontece das seguintes maneiras:



###### Iniciando uma expressão


1. Criterio.onde(campo);​



​Esse é o caso mais comum, onde a configuração padrão do critério já atende. Através dessa forma, o critério é criado já se iniciando uma expressão.

1. Criterio.onde('nome').igual('João');​





###### Configurando o critério


Configuração de parâmetro obrigatório:

1. Criterio.​novo( [ parametros: Criterio.obrigatorio() ] );



Configuração padrão:

1. Criterio.​novo( [ parametros: Criterio.​opcional() ] );​



Aceita um template que vai ser utilizado na geração da mensagem de erro quando um parâmetro de uma condição não tiver seu valor informado:

1. Criterio.​novo( [ parametros: Criterio.obrigatorio(​template_mensagem_validacao​) ] );​



​Por padrão, os valores utilizados como parâmetros, são opcionais, e caso seu valor seja nulo, a expressão é desconsiderada na geração do filtro:

1. ​valorIdade = nulo;
2. ​valorNome = 'João';​
3. Criterio.onde('idade').igual(valorIdade).e('nome').igual(valorNome);



​O critério a acima geraria o seguinte filtro:

1. 'nome = "João"'





### Operações


Após a criação do critério, é possível fazer uso um conjunto de operações de comparação.



###### Operações de comparação


* igual(valor)
* diferenteDe(valor)
* maiorQue(valor)
* maiorOuIgualQue(valor)
* menorQue(valor)
* menorOuIgualQue(valor)
* ehNulo() `nome is null`
* naoEhNulo() `nome is not null`
* ehVerdadeiro() `responsavel is true`
* ehFalso() `responsavel is false`
* naoEhVerdadeiro() `responsavel is false`
* naoEhFalso() `responsavel is true`
* comecaCom(valor) `nome like "P%"`
* naoComecaCom(valor) `nome not like "P%"`
* terminaCom(valor) `nome like " %P"`
* naoTerminaCom(valor) `nome not like " %P"`
* contem(valor) `nome like "%João%"`
* naoContem(valor) `nome not like "%João%"`
* contidoEm(valores) `nome in ("João", "Maria")`
* naoContidoEm(valores) `nome not in ("João", "Maria")`
Exemplo de utilização:

1. Criterio.onde('idade').igual(40);
2. Criterio.onde('casado).ehFalso();
3. Criterio.padrao().onde('agencia').ehNulo();
4. ​Criterio.novo([ parametros: Criterio.obrigatorio('É necessário informar um valor para o campo ${campo}') ]).onde('idade').igual(27);





#### Obrigatoriedade dos valores


Caso seja necessário configurar a obrigatoriedade dos valores de forma pontual, é possível configurar em qualquer operação que aceite um valor como parâmetro:

1. Criterio.onde('idade').igual(valor, [ parametro: Criterio.obrigatorio() ]);
2. Criterio.novo([ parametros: Criterio.obrigatorio('É necessário informar um valor para o campo ${campo}') ]).onde('idade').igual(27).e('nome').igual(valorNome, [ parametro: Criterio.opcional() ]);



Quando se configura a obrigatoriedade para todos os parâmetros do critério, a propriedade se chama **parametros**. Porém quando é configurado a nível de operação, se chama **parametro**.



### Delimitador nas operações contidoEm/naoContidoEm


Para as operações **contidoEm** e **naoContidoEm** pode ser informado um delimitador para os valores que não são String.



#### Com delimitador


1. numero = [1,2,5]
2. criterio = Criterio.onde('idade').contidoEm(numero, [delimitador: '"']);



O critério acima, gera o seguinte filtro:

1. idade in ("1", "2", "5")





#### Sem delimitador


1. numero = [1,2,5]
2. criterio = Criterio.onde('idade').contidoEm(numero);



O critério acima, gera o seguinte filtro:

1. idade in (1, 2, 5)





#### Com formatação e delimitador


1. data1 = Datas.data(2017, 1, 11)
2. data2 = Datas.data(2016, 1, 10)
3. datas = [ data1, data2 ]
4. criterio = Criterio.onde('aniversario').contidoEm(datas, [formatacao: "data", delimitador: "'"])



O critério acima, gera o seguinte filtro:

1. aniversario in ('2017-01-11', '2016-01-10')





### Filtros compostos


Os filtros podem ser utilizados de forma composta, fazendo uso do **e** ou do **ou** :

1. Criterio.onde('idade').igual(40).e('nome').igual('João').ou('bairro').igual('centro');



O critério acima, gera o seguinte filtro:

1. 'idade = 40 and nome = "João" ou bairro = "Centro"'





### Agrupamento


O critério tem suporte a **grupos** , através da seguinte chamada:

1. Criterio.grupo(CriterioInterno);
2. Criterio.onde('a').igual(12).e(Criterio.grupo(Criterio.onde('b').igual(24).ou('c').igual(30)));



O critério acima, gera o seguinte filtro:

1. a = 12 e (b = 24 or c = 30)





### Datas


Atualmente a engine de scripts tem suporte a **datas** através de seu formato completo (data e hora), e no critério ela é representada através do formato [ISO 8601](https://pt.wikipedia.org/wiki/ISO_8601)

1. Criterio.onde('dataNascimento').igual(Datas.hoje());



O critério acima, gera um filtro parecido com:

1. dataNascimento = 2018-02-05T09:37:09.009



Caso queira submeter a data no filtro utilizando outros formatos, as seguintes opções estão disponíveis:



#### ​Informar uma das formatações pré-definidas (data e hora)


1. ​​Criterio.onde('dataNascimento').igual(Datas.hoje()​, [formatacao: 'data']​);
2. Criterio.onde('​horaAlmoco').igual(Datas.hoje()​, [formatacao: 'hora']​);​ ​​



Os critérios acima, geram os seguintes filtros:

1. dataNascimento = ​2018-02-05
2. horaAlmoco = 09:43:45.045





#### ​Informar uma ​formatação customizada


1. ​​Criterio.onde('dataNascimento').igual(Datas.hoje(), [ formatacao: 'dd/MM/yyyy']);





## API de Execução


O bfc-script disponibiliza uma API para a consulta das informações relacionadas a execução.



#### Consultar o protocolo da execução


1. Execucao.atual.protocolo





#### Consultar se a execução foi cancelada pelo usuário


1. Execucao.atual.foiCancelada





### Exemplos


Monitorar o cancelamento e interromper a execução:

1. percorrer(...) {
2.
3.   // processamento da aplicação
4.
5.   // verifica e interompe caso a execução atual foi cancelada
6.   se(Execucao.atual.foiCancelada){
7.     interomper 'Execucao cancelada'
8.   }
9.
10. }





## API de Cache


O bfc-script disponibiliza uma API para armazenar valores pequenos em cache (máximo de 10kb), como dados de autenticação de serviços externos. O valor é armazenado usando o contexto de sistema, database e entidade.



#### Cache.adicionar(chave, valor)


Adiciona um novo valor no cache, com a chave informada e o tempo de expiração padrão de 12 horas.

1. Cache.adicionar('meu-token', 'aaabbbccc')





#### Cache.adicionar(chave, valor, expirarEm)


Adiciona um novo valor no cache, com a chave informada e o tempo de expiração (opicional).

1. Cache.adicionar('meu-token', 'aaabbbccc', 2.horas)





#### Cache.recuperar(chave, valorPadrao)


Recupera um valor colocado previamente no cache, ou retorna o valor padrão.

1. Cache.recuperar('meu-token', '')





#### Cache.contem(chave)


Verifica se o cache ontem algum valor para a chave informada.



#### Cache.remover(chave)


Remove o valor para chave informada.



## Integrando com uma aplicação


O bfc-script pode ser integrado em qualquer aplicação Java SE ou EE.



### Configurando a aplicação


A configuração pode variar de acordo com a stack utilzada.



#### Stack Dubai


O bfc-script esta disponível desde a versão 1.7.0 da stack.

Deve-se mapear as seguintes dependências:

1.         <dependency>
2.             <groupId>com.betha.bfc.commons</groupId>
3.             <artifactId>bfc-rest-script</artifactId>
4.         </dependency>
5.         <dependency>
6.             <groupId>com.betha.bfc.core</groupId>
7.             <artifactId>bfc-script-standard-engine</artifactId>
8.         </dependency>
9.         <dependency>
10.             <groupId>com.betha.bfc.commons</groupId>
11.             <artifactId>bfc-script-standard-engine-production</artifactId>
12.         </dependency>



Para projetos web, não é necessário mapear a dependência bfc-rest-script.

Em projetos que possuem explicitamente o uso do cglib, ou alguma dependência que o utiliza, é necessário remove-la do projeto, para não gerar conflito com o bfc-script.



### Executando um script


A execução de scripts em uma aplicação ocorre pela utilização da API do bfc-script. A classe ScriptManager contem os métodos necessários para executarmos nossos scripts, isso pode ser feito de duas formas:

1 - Para executarmos um script literal, basta utilizarmos o método evaluate da classe ScriptEngineContext conforme veremos abaixo.

1. ScriptEngineContext engineContext = ScriptManager.createContext();
2. engineContext.evaluate("imprimir 'Ola!!'");



2 - Porem em um ambiente real, nossos scripts não estarão transcritos estaticamente no código, conforme vimos no exemplo acima, mas estarão armazenados em um banco de dados, havendo a possibilidade desses serem editados a qualquer momento.

O armazenamento dos scripts deve ser realizado pela aplicação, que deverá apenas implementar uma interface de acesso ao script, para que a engine saiba como resgata-lo durante a execução. É indicado que a aplicação possua uma tabela para armazenamento de scripts independente do caso de uso, onde esta se relacionará com a tabela que representa o caso de uso.

Vejo o exemplo das tabelas abaixo:

A tabela SCRIPTS armazena scripts de qualquer natureza.

1. SCRIPTS
2. ------------------
3. ID NUMBER PRIMARY KEY
4. SCRIPT CLOB
5. DH_ALTERACAO TIMESTAMP



A tabela EVENTOS representa possíveis eventos do cálculo da folha de pagamento, onde cada evento tem respectivamente um script. Esta tabela é aplicavel para o caso de uso calculo da folha.

1. EVENTOS
2. ------------------
3. ID NUMBER PRIMARY KEY
4. DESCRICAO VARCHAR2
5. I_SCRIPT NUMBER FOREIGN KEY SCRIPTS



A tabela CRITICAS_USUARIOS representa possíveis critérios de validação configurados pelo usuário final. As criticas podem ser definidas para diversos cadastros, onde para cada crítica há um script. Esta tabela é aplicavel para o caso de uso críticas de usuário.

1. CRITICAS_USUARIOS
2. ------------------
3. ID NUMBER PRIMARY KEY
4. ID_SCRIPT NUMBER FOREIGN KEY SCRIPTS
5. DESTINO NUMBER (0 - CLIENTE, 1 - BAIRROS, ..)



Embora as tabelas EVENTOS e CRITICAS_USUARIOS representam casos de usos distintos, a tabela SCRIPTS, armazena scripts de ambas naturezas.

No momento da execução dos scripts, a aplicação deve informar o id do script persistido, onde a engine se encarregará de carregar o script do banco de dados, compilar e executar. A engine ainda controla todo mecanismo de cache e reload de scripts, caso esses tenham sido alterados.

Digamos que o script abaixo esta armazenado na tabela SCRIPTS e o seu id é 25.

1. valor = 10 * 3
2.
3. imprimir valor / 2



Para executarmos o script acima, basta invocar o método run passando o id do script por parâmetro.

1. ScriptEngineContext engineContext = ScriptManager.createContext();
2. engineContext.run("25");



A engine carregará o script do banco de dados, compilará, executará e armazenará o script compilado em cache para ser usado posteriormente.



##### Stack Dubai


Os scripts devem ser persistidos no banco da própria aplicação. Para execução de um script é necessário definir a entidade JPA que representa o script bem como seu respectivo repositório, estendendo as seguintes classes, com.betha.bfc.script.engine.standard.AbstractScript e com.betha.bfc.script.engine.standard.AbstractScriptRepository.

Segue um exemplo de implementação da entidade Script e seu repositório, estendendo as devidas classes:

1. @Entity
2. @Table(schema = "esquema da app", name = "VW_SCRIPTS")
3. @SequenceGenerator(name = "SEQ_SCRIPTS", schema = "BFCIT_OWNER", sequenceName = "SEQ_SCRIPTS", allocationSize = 1)
4. public class Script extends AbstractScript {
5.
6.     @Id
7.     @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "SEQ_SCRIPTS")
8.     private Long id;
9.
10.     @Column(name = "DESCRICAO", length = 50)
11.     private String descricao;
12.
13.     @Lob
14.     private String script = "//inicio";
15.
16.     protected Script() {
17.     }
18.
19.     public String getDescricao() {
20.         return descricao;
21.     }
22.
23.     public String getScript() {
24.         return script;
25.     }
26.
27.     @Override
28.     public Long getId() {
29.         return id;
30.     }
31.
32.     protected void setDescricao(String descricao) {
33.         this.descricao = descricao;
34.     }
35.
36.     protected void setScript(String script) {
37.         this.script = script;
38.     }
39.
40.     @Override
41.     public InputStream getScriptAsStream() {
42.         return new ByteArrayInputStream(getScript().getBytes(StandardCharsets.UTF_8));
43.     }
44.
45.     public static final class Builder extends AbstractEntityBuilder<Script> {
46.
47.         private Builder(final Script entity, final AbstractEntityBuilder.EntityState state) {
48.             super(entity, state);
49.         }
50.
51.         public static Script.Builder create() {
52.             return new Script.Builder(new Script(), AbstractEntityBuilder.EntityState.NEW);
53.         }
54.
55.         public static Script.Builder from(final Script entity) {
56.             return new Script.Builder(entity, AbstractEntityBuilder.EntityState.BUILT);
57.         }
58.
59.         public Builder descricao(String descricao) {
60.             entity.setDescricao(descricao);
61.             return this;
62.         }
63.
64.         public Builder script(String script) {
65.             entity.setScript(script);
66.             return this;
67.         }
68.
69.         @Override
70.         protected void validate(Validator validator) {
71.             super.validate(validator);
72.         }
73.     }
74. }
75.



É necessário definir na implementação do repositório, a tipagem da entidade que representa o script, neste caso Script.

1. @Dependent
2. public class ScriptRepository extends AbstractScriptRepository\<Script\> {
3.
4. }



A classe AbstractScript, contém o método execute, que possibilita sua execução a partir de um contexto no o ambiente de produção para engine padrão:

1.     VariaveisScriptFolha = variaveisScript = new VariaveisScriptFolha(funcionario, evento, usuarioLogado);
2.
3.     ScriptEngineContext engineContext = ScriptManager.createContext();
4.
5.     engineContext.inject(Injectables.byAnnotation(variaveisScript));
6.
7.     CriticasUsuario criticasUsuarioCliente = criticasUsuarioRepository.findByDestino(Destino.CLIENTE);
8.
9.     Script script = criticasUsuarioCliente.getScript();
10.     script.execute(engineContext);





#### Passando parâmetros para um script


Para passar informações para nossos scripts, precisamos seta-las como variáveis dentro da engineContext. Observe o script abaixo. Daremos um id à este script, 30.

1. valor = valorSalarioHora * 8 * 22
2.
3. imprimir valor



Executamos o script acima passando o id do script para o método run.

1. ScriptEngineContext engineContext = ScriptManager.createContext();
2.
3. engineContext.setVariable("valorSalarioHora", 66.35);
4. engineContext.run("30");



O script de código 30 utiliza uma variável chamada valorSalarioHora para efetuar um calculo, esta variável é setada no momento da execução desse script, conforme vimos acima.



##### Beans


É possível ainda passar um objeto como parâmetro. Este objeto deve seguir as convenções JavaBean, como seus atributos privados e métodos de leitura e gravação.

1. valor = funcionario.valorSalarioHora * 8 * 22
2.
3. imprimir valor



Executamos o script acima, porem precisamos passar uma instância de uma classe Funcionario como podemos ver abaixo.

1. Funcionario funcionario = new Funcionario();
2. funcionario.setValorSalarioHora(66.35);
3.
4. ScriptEngineContext engineContext = ScriptManager.createContext();
5.
6. engineContext.setVariable("funcionario", funcionario);
7. engineContext.run("30");



Objetos passados por parâmetros podem ser simples pojos bem como, objetos que realizam acesso a um banco de dados, etc.



##### Coleções


Podemos passar coleções de JavaBeans. O comando percorrer itera coleções e disponibiliza uma variável implícita que representa o item iterado chamada **item**.

1. percorrer(funcionarios){
2.     valor = item.valorSalarioHora * 8 * 22
3.
4.     imprimir valor
5. }



Executamos o script acima passando uma instância de classe que implemente a interface java.util.Collection ou alguma de suas subclasses. É necessário que os objetos dentro da coleção sejam JavaBeans.

1. Funcionario funcionario1 = new Funcionario();
2. funcionario.setValorSalarioHora(66.35);
3.
4. Funcionario funcionario2 = new Funcionario();
5. funcionario.setValorSalarioHora(70.23);
6.
7. List<Funcionario> funcionarios = new ArrayList<Funcionario>();
8. funcionarios.add(funcionario1);
9. funcionarios.add(funcionario2);
10.
11. ScriptEngineContext engineContext = ScriptManager.createContext();
12.
13. engineContext.setVariable("funcionarios", funcionarios);
14. engineContext.run("30")





##### NullsafeProxy


A engine por padrão, não permite que valores nulos sejam utilizados dentro dos scripts. Caso tentar passar um parâmetro nulo como variável, a engine irá disparar um NullpointerException e caso alguma propriedade dentro de um JavaBean estiver nula, mesmo que este bean esteja dentro de uma coleção, este atributo assumira um valor padrão:

* 0 para números,
* vazio para caracteres
* 01/01/1800 para datas
A engine encapsula os objetos complexos passados como variáveis em um nullsafeProxy. Este proxy atua recursivamente para qualquer possível atributo de tipo complexo, encapsulando este também como um nullsafeProxy. É importante que classes dos objetos passados por parâmetro para um script, não sejam final e possuam um construtor público.

Esse comportamento pode ser desabilitado de duas maneiras.



###### @NoProxy


É possível anotar uma classe com @NoProxy, onde esta não herdará o comportamento NullSafeProxy.

1.     @ScriptInjectable.NoProxy
2.     public class Funcionario{
3.         // ...
4.     }



Funcionario funcionario = new Funcionario();

engineContext.setVariable(funcionario, funcionario);



###### $nullSafe


É possível setar uma variável para desabilitar o comportamento NullSafeProxy para um contexto por setar uma variável boleana atribuída à chave $nullSafe.

engineContext.setVariable($nullSafe, false);

Funcionario funcionario = new Funcionario();

engineContext.setVariable(funcionario, funcionario);



##### Anotações


Com o objetivo de simplificar a manipulação de variáveis injetadas em um script e ainda trazer mais integridade, é possível utilizar anotações.

1. @ScriptInjectable
2. public class VariaveisScriptFolha {
3.
4.     @ScriptInjectable.Variable
5.     private Funcionario funcionario;
6.
7.     @ScriptInjectable.Variable(name = "eventoFolha")
8.     private Evento evento;
9.
10.     @ScriptInjectable.Variable(name = "usuarioLogado")
11.     private String usuario;
12.
13.     public VariaveisScriptFolha(Funcionario funcionario, Evento evento, String usuario) {
14.         this.funcionario = funcionario;
15.         this.evento = evento;
16.         this.usuario = usuario;
17.     }
18.
19. }



A classe VariaveisScriptFolha por exemplo, relaciona todas as variáveis que devem ser injetadas na execução do script de um suposto processo de calculo da folha.

A anotação @ScriptInjectable qualifica a classe como portadora de atributos passíveis de serem injetados em um script. A anotação @ScriptInjectable.Variable, marca um atributo da classe, para ser escaneado e o configura como uma variável em um script. O atributo name, define o nome que será utilizado para a variável no script. Se o valor do atributo não for setado, será utilizado como nome da variável dentro do script, o próprio nome do atributo com a anotação @ScriptInjectable.Variable.

Para setar na engine as variáveis baseadas na configuração da classe VariaveisScriptFolha, é necessário antes, submeter a instancia da classe para o utilitário Injectables.byAnnotation, retornando uma instância de Injectables, que poderá ser setado no contexto, conforme o exemplo abaixo:

1. 	Funcionario funcionario = ...;
2. 	Evento evento = ...;
3. 	String usuarioLogado = ...;
4.
5. 	VariaveisScriptFolha = variaveisScript = new VariaveisScriptFolha(funcionario, evento, usuarioLogado);
6.
7. 	ScriptEngineContext engineContext = ScriptManager.createContext();
8.
9. 	engineContext.inject(Injectables.byAnnotation(variaveisScript));
10.



A classe VariaveisScriptFolha garante que todas as variáveis que devem ser injetadas no script serão setadas, pois o construtor da classe exige o preenchimento de todos os valores. Essa abordagem pode ser combinada com técnicas mais sofisticadas, como builders ou mecanismos de validação como o Beans Validation.



##### Metadados


As anotações possuem duplo propósito, configuração de variáveis a serem injetadas em um script e coleta de meadados, utilizados para construção do ambiente de desenvolvimento de um script para o usuário final, onde o usuário precisará conhecer quais variáveis estão disponíveis, bem como outros detalhes, como parâmetros, retornos e documentação.

1. @ScriptInjectable
2. public class VariaveisScriptFolha {
3.
4.     @ScriptInjectable.Variable(doc = @ScriptInjectable.Doc("Funcionário para o qual o calculo esta sendo executado"))
5.     private Funcionario funcionario;
6.
7.     @ScriptInjectable.Variable(name = "eventoFolha", doc = @ScriptInjectable.Doc("Fornece os dados sobre o evento da folha que esta sendo calculado"))
8.     private Evento evento;
9.
10.     @ScriptInjectable.Variable(name = "usuarioLogado", doc = @ScriptInjectable.Doc("Usuário logado no sistema"))
11.     private String usuario;
12.
13.     public VariaveisScriptFolha(Funcionario funcionario, Evento evento, String usuario) {
14.         this.funcionario = funcionario;
15.         this.evento = evento;
16.         this.usuario = usuario;
17.     }
18.
19. }
20.



É possível configurar os metadados de variáveis de tipos complexos, como por exemplo o Funcionario.

1. public class Funcionario {
2.
3.     private String nome;
4.
5.     private Integer idade;
6.
7.     private BigDecimal salario;
8.
9.     private Date dataAdmissao;
10.
11.     @ScriptInjectable.Method(
12.             doc = @ScriptInjectable.Doc("Nome do funcionário"),
13.             ret = @ScriptInjectable.Return(
14.                     doc = @ScriptInjectable.Doc("O nome do funcionário")))
15.     public String getNome() {
16.         return nome;
17.     }
18.
19.     @ScriptInjectable.Method(
20.             doc = @ScriptInjectable.Doc("Idade do funcionário"),
21.             ret = @ScriptInjectable.Return(
22.                     doc = @ScriptInjectable.Doc("A idade do funcionário")))
23.     public Integer getIdade() {
24.         return idade;
25.     }
26.
27.     @ScriptInjectable.Method(
28.             doc = @ScriptInjectable.Doc("Salário do funcionário"),
29.             ret = @ScriptInjectable.Return(
30.                     doc = @ScriptInjectable.Doc("O salário do funcionário")))
31.     public BigDecimal getSalario() {
32.         return salario;
33.     }
34.
35.     @ScriptInjectable.Method(
36.             doc = @ScriptInjectable.Doc("Data de admissão do funcionário"),
37.             ret = @ScriptInjectable.Return(
38.                     doc = @ScriptInjectable.Doc("A data de admissão do funcionário")))
39.     public Date getDataAdmissao() {
40.         return dataAdmissao;
41.     }
42.
43. }



Essa configuração não é recursiva, suportando apenas o primeiro nível, a partir da classe com a anotação @ScriptInjectable.

É possível configurar a forma como o usuário vai interagir com uma variável. Podemos configurar uma variável como uma classe de funções, que na pratica, apenas altera a forma como o usuário visualizará a variável em tempo de desenvolvimento.

1. @ScriptInjectable
2. public class VariaveisScriptFolha {
3.
4.     // outros atributos
5.
6.     @ScriptInjectable.Class(name = "RepositorioFuncionarios", doc = @ScriptInjectable.Doc("Classe de funções para consulta e manipulação de funcionários"))
7.     private RepositorioFuncionario repositorioFuncionario;
8.
9. }
10.
11.





#### Obtendo dados de um script


Em alguns casos iremos precisar obter o retorno de um script ou o valor de alguma variável específica. A engine fornece métodos para a obtenção de variáveis registradas dentro da engine ou ainda para recuperar os dados de retorno de um script.

Observe o script abaixo cujo o id é 30.

1. idadeFuncionario = 60
2. dataCalculo = Datas.hoje()
3.
4. valor = valorSalarioHora * 8 * 22
5. nomeFuncionario = 'Robert Plant'
6.
7. retornar salario:valor, nome: nomeFuncionario



No exemplo acima estamos utilizando a variável injetada **valorSalarioHora** para fazermos um suposto calculo salarial. Criamos a variável **nomeFuncionario** , e atribuímos o nome para o funcionário e utilizamos o comando retornar para submetermos estes dados como valor de retorno para o script, atribuindo uma chave para cada valor. Estes valores serão resgatados através de uma java.util.Map como veremos abaixo.

1. ScriptEngineContext engineContext = ScriptManager.createContext();
2.
3. engineContext.setVariable("valorSalarioHora", 66.35);
4. Result result = engineContext.run("30");
5.
6. Map returnData = result.getValue();
7.
8. Number salario = (Number)returnData.get("salario");
9. String nomeFuncionario = (String)returnData.get("nome");



Todo script executado gera um retorno. Este tipo de retorno precisa ser previamente reconhecido pelo executor do script, pois será necessário fazer um cast para obtermos o valor de retorno. Para o exemplo acima, o retorno é obtido através de um mapa, através das chaves previamente reconhecidas, obtemos os valores requeridos.

Podemos resgatar os valores das variáveis de outra forma. Para o script executado acima, existem duas outras variáveis declaradas que não foram submetidas ao comando retornar, poderíamos passar elas normalmente para o comando, assim como fizemos com as variáveis salario e nome, ou podemos recuperar seus valores conforme veremos abaixo:

1. ScriptEngineContext engineContext = ScriptManager.createContext();
2.
3. engineContext.setVariable("valorSalarioHora", 66.35);
4. Result result = engineContext.run("30");
5.
6. int idade = result.getVariable("idadeFuncionario");
7. Date dataCalculo = result.getVariable("dataCalculo");



A classe Result fornece um método para obtermos as variáveis usadas dentro do script. Através do método getVariable, podemos resgatar qualquer variável registrada no script, inclusive aquelas que submetemos ao comando retornar. Devido ao uso de generics no retorno do método getVariable, não precisamos fazer o cast para o tipo requerido, pois o cast é feito implicitamente.



### Entendo Contextos


As aplicações possuem apenas uma instância de uma determinada engine. Isso possibilita compartilhar scripts carregados e já compilados em outras execuções, diminuindo o custo de execução dos scripts utilizados por outros processos. Porem é necessário que durante a execução dos scripts exista isolamento, para que uma execução não gere efeitos colaterais em outras.

Embora exista apenas uma instância da engine para uma aplicação, a execução dos scripts é dividida por contextos. Os contextos garantem que os dados envolvidos na execução de um script, como parâmetros passados para o script, instância de classes e outros recursos, estejam restritos a execução corrente, não influenciando execuções paralelas.

Por outro lado, um contexto permite o compartilhamento de informações durante o seu tempo de vida. Podemos executar um número ilimitado de scripts em um único contexto, sendo útil quando precisamos passar os mesmos parâmetros para vários scripts a serem executados ou manter um estado entre eles.

Devemos ter em mente que o estado dos objetos possuem escopo de contexto, qualquer modificação de um atributo será compartilhado a todos os scripts executados dentro de um mesmo contexto, possibilitando por exemplo, agrupar informações entre várias execuções conseguintes ou trocar informações entre scripts.

Manter o escopo reduzido a um contexto de execução pode ser perigoso quando utilizado de maneira involuntária, compartilhando por exemplo, um escopo entre várias execuções sem o conhecimento do ciclo de vida da engine de script.



## Ambiente de desenvolvimento - Editor de script


O editor de scripts fornece uma forma amigável para codificação de scripts que serão compilados e executados pela engine. A responsabilidade sobre a validação da sintaxe, compilação, execução de scripts e geração de informações relacionadas a erros de compilação são geridos inteiramente pela engine.



#### Stack Dubai


[Configuração front-end](frontend.html)

[Configuração back-end](backend.html)



## O projeto


Atualmente a maioria dos softwares foram desenhados para operar nos data-centers das empresas, com contratos e licenças específicas. Porem em um ambiente cloud, onde aplicações podem ser oferecidas como serviço, é necessário que todos os recursos computacionais sejam compartilhados. Clientes precisarão adaptar a aplicação às suas características específicas, e é necessário garantir que as particularidades de cada um não impactem em alterações de software e não gerem conflito à outros clientes.,

A Betha através do projeto cloud, esta adaptando sua infraestrutura web para fornecer aos seus clientes, soluções compatíveis com o este novo paradigma tecnológico, que emergiu junto com o conceito de cloud computer. O bfc-script é uma parte importante deste novo modelo, e irá se integrar com outras soluções subseqüentes. Ele possibilitará que as aplicações sejam personalizadas através de scripts de usuário e ainda que os sistemas FolhaRh e Tributos, que fazem uso de scripts de customização, sejam migrados para o ambiente web.



### Arquitetura


O bfc-script foi projetado para ser intergrado à aplicações Java SE e EE. O framework centraliza toda sua especificação em um módulo core, possibilitando a criação de diversas engines dentro de um mesmo ambiente de execução.

![Arquitetura](images/script-arquitetura.png)



#### A engine de execução


Foi estudado a viabilidade de se implementar uma engine de execução para o bfc-script, porém, foi constatado que existem diversas engines disponíveis para JVM, algumas amplamente utilizadas pela comunidade. Após uma primeira avaliação, foram elencadas 3 engines para testes: Jruby (Ruby), Rhino (Java Script) e Groovy (Mix Java/Ruby).

Os principais requisitos para a seleção de uma engine eram: tipagem dinamica, boa performance, favorecer a criação de DSLs. A engine do groovy foi a que melhor preencheu estes requisitos, se tornando a engine de execução do bfc-script.



#### Registro de engines


Várias engines podem ser registradas em um mesmo ambiente de execução. Isso poderá ser útil caso seja necessário criar engines que resgatam scripts de lugares específicos, ou que ainda precisem restringir ou liberar recursos específicos. As engines são registradas através do mecanismo de service/lookup do java. O ScriptManager faz lookup das engines registradas no classpath, através de uma identificação atribuida à engine no momento em que esta é registrada, constituida por um nome e um Environment (**PRODUCTION** ou **DEVELOPMENT**). Portanto podemos ter duas engines com o mesmo nome mas para ambientes diferentes. O Environment possibilita que as engines implementem caracteristicas desejáveis para os ambientes distintos, sendo estas caracteristicas perceptiveis na compilação e execução do scripts.

Para maioria dos casos de uso não será necessário criar uma engine e sim utilizar a engine engine padrão.



#### Engine padrão


A engine de execução padrão foi desenvolvida para dar suporte às necessidades de praticamente todas as aplicações da Betha. A engine permite que pacotes de funções utilitárias sejam plugados, personalizando o box de funções utilitárias da engine para um caso de uso desejado.

A engine padrão, possui um conjunto de funções utilitárias para manipulação de datas, caracteres, números, e também instruções de iteração e condicionais, que definem a linguagem e utilitários da engine.



### Groovy


Ao contrário do Microsoft .Net, Java (linguagem e plataforma) não foi criada visando o uso de várias linguagens para gerar código interpretado (bytecodes em Java, MSIL - Microsoft Intermediate Language - em .Net). Com os anos, a comunidade Java criou suas próprias ferramentas para compensar este fato, na forma de linguagens que geram bytecodes compatíveis com os produzidos pelo compilador da linguagem Java. Groovy é uma destas linguagens, talvez a mais conhecida. É um projeto de Software Livre hospedado na Codehaus responsável por outros projetos como XStream, Pico/Nano Container, AspectWerkz, ActiveMQ, JMock, Drools e tantos outros. A linguagem Groovy é padronizada pela JSR 241.

O grande foco de Groovy é a produção de scripts, como os feitos em Bash ou Perl, mas a linguagem é poderosa o suficiente para ir muito além. Alguns programas podem exigir que rotinas sejam configuráveis e a maioria dos grandes sistemas empresariais, como ERPs e outros sistemas vendidos como produtos, permite um alto nível de personalização por cliente. Imagine um software de frente de caixa que precisa aceitar promoções definidas pelo time de marketing várias vezes por ano.

Na maioria das vezes estas configurações são implementadas com algum nível de parametrização em arquivos de configuração, mas quando existe uma mudança grande (como uma promoção compre dois produtos do lote ABC-001 e leve mais um) geralmente o desenvolvedor precisa codificar esta em Java e fazer outro deploy da aplicação.

Fonte: [Groovy: Linguagem de Script para Java](http://www.fragmental.com.br/wiki/index.php?title=Groovy:_Linguagem_de_Script_para_Java#Integr.C3.A1vel_a_um_Programa_Java)

Mais informações:

[Wikipedia Groovy](http://pt.wikipedia.org/wiki/Groovy)

[Codehaus](http://groovy.codehaus.org/)



### Linguagens de Script para JVM


Quem tem acompanhado as ferramentas de desenvolvimento de software durante a última década sabe que o termo Java se refere a um par de tecnologias: a linguagem de programação Java e do Java Virtual Machine (JVM). A linguagem Java é compilada em bytecodes que são executados na JVM. Através deste projeto, Java oferece a sua portabilidade como grande diferencial.

A linguagem e a JVM, no entanto, têm caminhado cada vez mais em direções opostas. A linguagem tornou-se mais complexa, enquanto a JVM se tornou uma das plataformas de execução mais rápida e eficiente disponível. Em muitos benchmarks, Java iguala o desempenho do código binário gerado por linguagens compiladas como C e C + +. A crescente complexidade da linguagem e do notável desempenho, portabilidade e escalabilidade da JVM criaram uma abertura para uma nova geração de linguagens de programação. Essas linguagens oferecem possibilidades que carecem na linguagem Java, além de serem geralmente mais sucintas e objetivas.

Tecnólogos divergem sobre o que exatamente é uma linguagem de script. Na sua definição mais estrita, é uma linguagem que permite ao desenvolvedor escrever programas rápidos.

Fonte: [Top five scripting languages the jvm](http://www.infoworld.com/d/developer-world/top-five-scripting-languages-the-jvm-855?page=0,0)

Mais informações:

[Linguagens dinâmicas na JVM](http://www.slideshare.net/amsterdatech/linguagens-dinamicas-na-jvm)

[Java Scripting Linguagens Interpretadas pelo java](http://www.slideshare.net/jeveaux/java-scripting-linguagens-interpretadas-pelo-java)

[List of Java Virtual Machines](http://en.wikipedia.org/wiki/List_of_Java_virtual_machines)



### Linguagens de domínio especifico


Artigo no formato de perguntas e repostas formulado por [Martin Fowler](http://martinfowler.com/).

**O que é uma Domain Specific Language? (ou linguagem de domínio especifico, ou ainda DSL)**

Uma Domain Specific Language (DSL) é uma linguagem de programação de expressividade limitada, focada num domínio particular. A maioria das linguagens que você conhece são linguagens de propósito geral (General Purpose Languages), que podem lhe dar com a maioria das coisas que você encontra durante um projeto de sistema. Cada DSL pode agir somente em um aspecto especifico do sistema.

**Então você não poderia escrever todo projeto em uma DSL?**

Não. A maioria dos projetos irão usar uma linguagem de propósito geral e muitas DSLs.

**Essa idéia é nova?**

Não totalmente. DSLs tem sido usadas extensamente nos círculos de usuários do Unix desde os primórdios desse sistema. A comunidade Lisp discute a criação de DSLs em Lisp e então usa a DSL para implementar a lógica. A maioria dos projetos de TI usam muitas DSLs – você já deve ter ouvido de coisas como CSS, SQL, expressão regular e etc.

**Então porque este assunto está fazendo tanto barulho só agora?**

Provavelmente é por causa do Ruby and Rails. Ruby é uma linguagem com muitas características que tornam fácil o desenvolvimento de DSLs e as pessoas que estão envolvidas na comunidade Ruby têm se sentido mais a vontades com essa abordagem, então eles levam vantagem dessas características. Em particular o Rails usa muitas DSLs que o deixam mais fácil de usar. Isto, por sua vez, tem incentivado mais pessoas a seguir essas idéias. Outra razão é que muitos sistemas feitos em Java ou C

# precisam ter muito de seu comportamento definido de forma mais dinâmica. Isto conduziu a arquivos XML complexos que são difíceis de compreender que, por sua vez, levou as pessoas a explorar DSLs novamente.


**Então DSLs podem ser usadas com outras linguagens além do Ruby?**

Sim, como eu já disse, as DSLs já estavam por ai há muito tempo, mais do que o Ruby. Ruby tem uma sintaxe não obstrutiva e também características de meta-programação que a torna mais fácil para criar elegantes DSLs internas, mais do que outras linguagens como C

# e Java. Mas existe DSLs internas uteis feitas em Java e C#


**Qual a diferença entre DSL interna e DSL externa?**

Uma DSL interna é apenas um idioma particular de escrever código na linguagem hospedeira. Então uma DSL interna feita em Ruby é um código Ruby, escrito num estilo particular que deixa a linguagem mais próxima da linguagem hospede. Tais como elas podem ser chamadas de Interface Fluente ou DSL embutida. Uma DSL externa é uma linguagem completamente separada que é traduzida para que a linguagem hospedeira possa entender.

**Por que as pessoas estão interessadas nas DSLs?**

Eu vejo que as DSLs possuem dois principais benefícios. O benefício mais comum é fazer que certos tipos de códigos fiquem mais fáceis de compreender, que se tornem mais fáceis de modificar, assim melhorando a produtividade do programador. Isto é válido para todos interessados e relativamente fácil de atingir. O benefício mais interessante, todavia, é que uma DSL bem projetada pode ser entendível por pessoas do negocio, permitindo-lhes compreender diretamente o código que implementa suas regras de negócios.

**Então este é o gancho – pessoas do negócio escrevendo suas próprias regras?**

Em geral eu não penso assim. É muito trabalhoso criar um ambiente que permita as pessoas do negocio escrever suas próprias regras. Você tem que fazer boas ferramentas de edição, depuração, testes e etc. Você tem a maioria dos benefícios das DSLs apenas permitindo que pessoas do negocio sejam capazes de ler as regras. Então eles podem revê-las para aperfeiçoa-las, falar sobre elas com os desenvolvedores e propor mudanças corretas da implementação. Ter DSLs legíveis ao contexto negócios é de longe menos esforço do que ter DSLs escrevíveis pelas pessoas do negócios, mas os ganhos ainda são bons. Existem momentos onde vale a pena o esforço para fazer DSLs escrevíveis por pessoas do negocio, mas esse é um objetivo mais avançado.

**Você precisa de ferramentas especiais (leia-se caras)?**

Normalmente, não. DSLs internas são apenas facilidades da linguagem de programação que você está usando. DSLs externas requerem que você use algumas ferramentas especiais – mas essas são open source e muito maduras. O maior problema com essas ferramentas é que a maioria dos desenvolvedores não estão acostumados com elas e acreditam que elas são complicadas de usar mais do que elas realmente são (um problema exacerbado pela pobre documentação). Todavia há exceções no horizonte. Existe uma classe de ferramentas que eu chamo LanguageWorkbench. Essas ferramentas permitem você definir DSLs mais facilmente e também provem sofisticados editores para elas. Ferramentas assim tornam mais viáveis a construção de DSL para os negócios.

**Então isto é a repetição do sonho do desenvolvimento de software sem programação (ou programadores)?**

Esta foi a intenção do COBOL e não penso que há alguma razão para que as DSLs tenham sucesso onde o COBOL (e tantas outras falharam). Eu penso que é importante que DSLs permitam pessoas do negocio e desenvolvedores colaborarem mais eficientemente porque eles podem falar sobre um conjunto de regras que também são códigos executáveis.

**Quando eu deveria considerar a hipótese de criar uma DSL?**

Quando você está trabalhando num aspecto do sistema com ricas regras de negócios ou work-flows. Uma DSL bem escrita deveria permitir que os clientes entendessem as regras pelas quais o sistema funciona.

**Isto não vai levar a uma cacofonia de linguagens que as pessoas acharam mais difíceis de aprender?**

Nós já temos uma cacofonia de frameworks que os programadores tem que aprender. Isto é uma inevitável conseqüência de sistemas reusáveis, é o único jeito que temos de lhe dar com todas essas coisas que os sistemas tem que fazer hoje em dia. Na essência uma DSL não é nada mais do que uma fachada chique sobre um framework. Como resultado elas contribuem um pouquinho com a complexidade que já havia. Na verdade uma boa DSL deveria fazer as coisas melhores tornando esses frameworks mais fáceis de usar.

**Mas as pessoas não vão criar muitas DSLs de baixa qualidade?**

Claro, assim como pessoas criam frameworks de baixa qualidade. Mas, novamente, eu gostaria de argumentar que DSLs de baixa qualidade não causam mais danos se comparados aos que os frameworks mal projetados causam

Fonte: [DSL Interna e externa perguntas e respostas](http://archsofty.blogspot.com/2008/10/dsl-interna-e-externa-perguntas-e.html)

Original: [DSL Questions & Answers](http://www.martinfowler.com/bliki/DslQandA.html)

Mais informações:

[Domain Specific Languages](http://www.grails-exchange.com/files/Guilliaume%20LaForge%20-%20DomainSpecificLanguages.pdf)

[Arquitetura evolucionária e design emergente: Interfaces fluentes](http://www.ibm.com/developerworks/br/java/library/j-eaed14/index.html)

[Groovy SQL Builder](http://ilyasterin.com/blog/2009/07/groovy-sql-builder.html)

[Refatorando para Fluent-Interface](http://gc.blog.br/2007/09/25/refatorando-para-fluent-interface/)



## FAQ


Esta sessão será utilizada para responder perguntas freqüentes.



### Por quê não utilizar uma linguagem baseada em SQL assim como o Tributos?


1. Porque toda infraestrutura de compilação e execução de scripts é dependente de um banco de dados, precisaríamos estar fortemente acoplados a um sistema de banco de dados.
2. Em aplicações web, é importante reduzir o número de acessos a um banco de dados para não prejudicar a performance das aplicações, criar uma solução acoplada a um banco de dados refletiria negativamente nesse aspecto.
3. Linguagens PL/SQL são muito rígidas e difíceis de se compreender por usuários sem conhecimentos em linguagens de programação. A intenção é que a codificação de scripts seja simples e intuitiva.
4. Comprometeria a segurança, pois habilitaria a visibilidade de todas as tabelas do banco de dados ao usuário, permitindo que sejam feitas manipulações de dados não desejados.



### Por quê a API padrão não fornece métodos para consultar uma tabela no banco de dados?


Como a intenção é que a codificação de scripts seja simples e intuitiva e aberta à pessoas que não possuem conhecimentos em linguagens de programação, deixar essa possibilidade aberta para esses usuários, pode acarretar em consultas pouco otimizadas, prejudicando todos os usuários de um banco de dados, levando até mesmo a indisponibilidade de toda a aplicação.



### Por que não devo passar objetos que possuem responsabilidade internas em uma aplicação como parâmetros em scripts?


O bfc-script permite que sejam fornecidos parâmetros que serão utilizados pelo usuário dentro do script. Por exemplo, posso criar um script no qual o salário líquido será passado por parâmetro, ou ainda um objeto que represente um funcionário, onde o usuário terá acesso a nome, sexo e o salário líquido.

Quando você passa por parâmetro um objeto, alterações na classe do objeto impactam diretamente os scripts que o utilizam. Existe uma dependência forte entre a classe que representa o objeto e os scripts. Não é prudente fornecer um objeto que possui responsabilidades internas em sua aplicação, como por exemplo VOs.

VOs constituem o modelo da aplicação e estão suscetíveis a mudanças extremas. Medir o impacto da alteração de um VO por si só já é altamente complexo, se estes VOs forem utilizados em scripts, pode inviabilizar a alteração do modelo e prejudicar a evolução do sistema.

* * *
Copyright © 2021. All rights reserved.
