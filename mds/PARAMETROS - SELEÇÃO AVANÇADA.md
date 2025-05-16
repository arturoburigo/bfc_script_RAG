# 📌 Criando parâmetro para seleção avançada
---
## Finalidade
Consultar a seleção avançada que foi selecionada no parâmetro.
# 📝 Guia para criação do parâmetro
---
### 🧑‍💻 Criando um parâmetro:
![Criando parâmetro](screenshots/Screenshot_1.png)
### 🧑‍💻 Configurando parâmetro para seleção avançada:
![Consulta matrícula](screenshots/Screenshot_3.png)

# ⚙️ Utilizando e manipulando o parâmetro de seleção avançada
---
### 🧑‍💻 Existem diversas maneiras de fazer uso do parâmetro de matrículas, o exemplo abaixo é apenas uma forma de manipular o parâmetro.
``` 
// Declarando a fonte dinâmica de matrículas
fonteMatriculas = Dados.pessoal.v2.matriculas;

// Declarando parâmetro de entrada 
selecao = parametros.selecaoAvancada?.selecionados?.valor

// Filtro da seleção avançada
filtroSelecaoAvancada = ""
if (selecao) {
  filtroSelecaoAvancada = "id in (${selecao.join(',')})"
}

// Lista de matrículas
def matriculas = []

// Exemplo de utilização do parâmetro de seleção avançada como critério de consulta
// No caso da seleção avançada seu filtro deve ser passado como um parâmetro de consulta. ex: parametros: [selecaoAvancada: filtroSelecaoAvancada]
fonteMatriculas.busca(parametros: [selecaoAvancada: filtroSelecaoAvancada]).each{ itemMatriculas ->
    imprimir itemMatricula
    matriculas << itemMatricula
}

// Exemplo de uso para uma lista de matrículas
matriculas.each{ mat -> 
    imprimir mat.id
    imprimir mat.codigoMatricula.numero
    imprimir mat.pessoa.nome
    imprimir "------"
}
```
