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

