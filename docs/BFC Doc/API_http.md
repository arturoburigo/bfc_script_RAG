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




