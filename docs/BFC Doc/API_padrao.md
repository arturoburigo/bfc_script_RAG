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

