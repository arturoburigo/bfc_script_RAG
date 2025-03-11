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


