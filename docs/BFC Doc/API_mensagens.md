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



