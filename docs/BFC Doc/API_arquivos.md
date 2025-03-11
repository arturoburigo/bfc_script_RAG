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



