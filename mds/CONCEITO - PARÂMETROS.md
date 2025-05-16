## ⚠️ Recomenda-se pelo menos o conhecimento básico sobre lógica de programação para o bom entendimento deste conteúdo.
# 📌 Conceitos Básicos sobre Parâmetros
---
Os parâmetros são os campos que o usuário preenche durante a execução do script/relatório, normalmente seu uso é destinado a consultas em fonte dinâmica, mas podem variar conforme a necessidade do script/relatório. São funcionalidades poderosas com capacidade de aprimorar a experiência do usuário e trazer mais dinâmismo para a execução do script/relatório.
Existem parâmetros de diversos tipos com N possibilidades de manipulação, veremos alguns a seguir.

# 📝 Guia para criação de um parâmetro
---
### 🧑‍💻 Acessando o menu de parâmetros:
![Menu parâmetros](screenshots/Screenshot_4.png)

### 🧑‍💻 Criando um parâmetro:
![Criando parâmetro](screenshots/Screenshot_1.png)

# 📝 Guia para configuração do parâmetro
---
![Configurando parâmetro](screenshots/Screenshot_7.png)

### Campos de cadastro do parâmetro:
- Nome: nome do parâmetro, utilizado para chamar o parâmetro no código fonte.
- Descrição: descrição do parâmetro, é o texto que aparece para o usuário.
- Dica de preenchimento: texto que é exibido ao passar o mouse por cima do icone de interrogação.
- Tipo do dado: Tipo do parâmetro.
- Opções da lista: Se a lista vai ser **Dinâmica** ou **Estática**.
- Lista Estática: Define valores fixos para serem selecionados.
- Lista Dinâmica: Valores consultados através da fonte dinâmica.
    - Categoria da fonte: Categoria da fonte dinâmica (normalmente usar a 'Geral').
    - Fonte: Fonte Dinâmica que vai ser consultada, normalmente utilizar a v2 (se houver).
    - Valor: valor que irá retornar do parâmetro de entrada para a variável destino no código fonte (normalmente utilizar o ID).
    - Descrição: o que irá aparecer na tela para o usuário.
    - Filtro: filtro para consulta da fonte dinâmica.

# 📝 Guia para escolher o tipo de parâmetro
---
### Primeiramente veremos os tipos de parâmetros disponíveis:

📂 Parâmetro do tipo Arquivo:
- Permite passar um arquivo para entrada de dados, utilizado em scripts de importações.
- Este parâmetro irá retornar uma variável do tipo 'Arquivo' ou 'File'.
  
⌨️ Parâmetro do tipo Caracteres:
- Permite livre digitação no parâmetro, utilizado para campos de observações, usuário e entre outros.
- Este parâmetro irá retornar uma variável do tipo 'String'.
  
📅 Parâmetro do tipo Data:
- Seleciona a data no formato calendário, muito utilizado para filtros de competência.
- O parâmetro Data fornece a data completa que foi selecionada.
- Este parâmetro irá retornar uma variável do tipo 'Date'.
  
📅 Parâmetro do tipo Data e Hora:
- Seleciona a data e hora no formato calendário, utilizado para filtros mais especificos.
- O parâmetro Data e Hora fornece a data completa, incluindo também hora, minutos e segundos.
- Este parâmetro irá retornar uma variável do tipo 'Date'.
  
🔢 Parâmetro do tipo Inteiro:
- Permite que seja inserido apenas números no parâmetro, utilizado em campos como ID e entre outros.
- Este parâmetro irá retornar uma variável do tipo 'Long'.
  
📋 Parâmetro do tipo Lista Multipla:
- Normalmente é um dos tipos de parâmetros mais utilizados.
- Comumente utilizado para consultas dinâmicas (fontes dinâmicas).
- Permite que seja inserido multiplos itens na seleção do parâmetro, como por exemplo 2 ou 3 matrículas em uma execução só.
- Este parâmetro irá retornar uma variável do tipo 'List' ou 'Array'.
  
📋 Parâmetro do tipo Lista Simples:     
- Normalmente é um dos tipos de parâmetros mais utilizados.
- Utilizado tanto para consultas dinâmicas quanto para seleção de itens já definidos (valor estático).
- Pode ser utilizado para manipular constantes e enumeradores.
- Permite que seja inserido multiplos itens na seleção do parâmetro, como por exemplo 2 ou 3 matrículas em uma execução só.
- Este parâmetro irá retornar uma variável do tipo 'List' ou 'Array'.
  
📅 Parâmetro do tipo Mês/Ano:
- Seleciona o mês e ano no formato calendário, utilizado para filtros mais especificos como competência de cálculo da folha.
- Este parâmetro irá retornar uma variável do tipo 'YearMonth'.
  
🔑 Parâmetro do tipo Senha:
- Este tipo de parâmetro oculta o conteúdo que está sendo inserido.
- Permite livre digitação no parâmetro, utilizado para campos de senhas ou para dados que não devem ser exibidos.
- Este parâmetro irá retornar uma variável do tipo 'String'.
  
💰 Parâmetro do tipo Valor:
- Permite inserir valores já formatadas, como por exemplo campos do tipo salário, taxa e entre outros.
- Este parâmetro irá retornar uma variável do tipo 'Double'.

### Exemplo de preenchimento para todos os tipos de parâmetros disponíveis:
![Preenchimento parâmetros](screenshots/Screenshot_5.png)

# ⚙️ Consultando e manipulando os parâmetros no código fonte
---
### Anotações e diferenças ao consumir o conteúdo de um parâmetro:
- A chamada do parâmetro acontece através da palavra reservada **'parametros'**.
- O acesso ao conteúdo do parâmetro acontece através do atributo **'valor'**.
- O acesso da *Lista Múltipla* acontece através do atributo **'selecionados'** aninhado com o atributo **'valor'**.
- O acesso da *Lista Simples* acontece através do atributo **'selecionado'** aninhado com o atributo **'valor'**.

### 🧑‍💻 Segue as diferenças entre as chamadas dos parâmetros:
```
// Lista Simples de matrícula (selecionado)
matricula = parametros.matricula.selecionado.valor
// Lista Múltipla de matrícula (selecionados)
matriculas = parametros.matriculas.selecionados.valor
// Restante dos parâmetros
nome = parametros.nome.valor
``` 

### 🧑‍💻 Chamada de parâmetros e tipagens das classes:
```
// ====== Declarando os parâmetros de entrada ======
selecaoAvancada = parametros.selecaoAvancada?.selecionados?.valor // TIPO -> Lista Múltipla
arquivo = parametros.arquivo?.valor // TIPO -> Arquivo
observacao = parametros.observacao?.valor // TIPO -> Caractere
competencia = parametros.competencia?.valor // TIPO -> Data
calculo = parametros.calculo?.valor // TIPO -> Data e Hora
idMatricula = parametros.id?.valor // TIPO -> Inteiro
matriculas = parametros.matriculas?.selecionado?.valor // TIPO -> Lista Simples
competenciaCalculo = parametros.competenciaCalculo?.valor // TIPO -> Mês/Ano
senha = parametros.senha?.valor // TIPO -> Senha
salario = parametros.salario?.valor // TIPO -> Valor

// ====== Impressões dos parâmetros ======
imprimir "Conteudo: " + selecaoAvancada + ", Classe: " + selecaoAvancada.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: [701271] | Classe: class java.util.ArrayList

imprimir "Conteudo: " + arquivo + ", Classe: " +  arquivo.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: com.betha.plataforma.scripts.worker.execucao.parametros.ParamFile$FileSourceImpl@3e1af457 | Classe: class com.betha.plataforma.scripts.worker.execucao.parametros.ParamFile$FileSourceImpl

imprimir "Conteudo: " + observacao + ", Classe: " +  observacao.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: Observação do documento... | Classe: class java.lang.String

imprimir "Conteudo: " + competencia + ", Classe: " +  competencia.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: Sat Mar 01 00:00:00 BRT 2025 | Classe: class java.util.Date 

imprimir "Conteudo: " + calculo + ", Classe: " +  calculo.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: Sat Mar 01 11:14:00 BRT 2025 | Classe: class java.util.Date

imprimir "Conteudo: " + idMatricula + ", Classe: " +  idMatricula.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: 1234567, Classe: class java.lang.Long

imprimir "Conteudo: " + matriculas + ", Classe: " +  matriculas.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: 37668214, Classe: class java.lang.String

imprimir "Conteudo: " + competenciaCalculo + ", Classe: " +  competenciaCalculo.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: 2025-03, Classe: class java.time.YearMonth

imprimir "Conteudo: " + senha + ", Classe: " +  senha.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: 12345, Classe: class java.lang.String

imprimir "Conteudo: " + salario + ", Classe: " +  salario.getClass()
// A IMPRESSÃO VAI SER -> Conteudo: 1250.0, Classe: class java.lang.Double
``` 

# 📚 Exemplos de parâmetros comumente utilizados na Vertical Pessoal
---
### Exemplo de um parâmetro para consulta de matrículas:
![Consulta matrícula](screenshots/Screenshot_2.png)

### Exemplo de um parâmetro para consulta de seleção avançada:
![Consulta matrícula](screenshots/Screenshot_3.png)
