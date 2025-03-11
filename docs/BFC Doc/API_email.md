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


