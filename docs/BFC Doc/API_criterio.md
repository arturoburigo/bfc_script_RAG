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


