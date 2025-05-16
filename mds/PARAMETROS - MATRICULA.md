# 📌 Criando parâmetro para seleção da Matrícula
---
## Finalidade
Consultar a matrícula que foi selecionada no parâmetro.
# 📝 Guia para criação do parâmetro
---
### 🧑‍💻 Criando um parâmetro:
![Criando parâmetro](screenshots/Screenshot_1.png)
### 🧑‍💻 Configurando parâmetro para filtrar matrícula:
![Consulta matrícula](screenshots/Screenshot_2.png)

# ⚙️ Utilizando e manipulando o parâmetro de matrícula
---
### 🧑‍💻 Existem diversas maneiras de fazer uso do parâmetro de matrículas, o exemplo abaixo é apenas uma forma de manipular o parâmetro.
``` 
// Declarando a fonte dinâmica de matrículas
fonteMatriculas = Dados.pessoal.v2.matriculas;

// Declarando o parâmetro de entrada
matricula = parametros.matricula?.selecionados?.valor

// Montando o critério de consulta da fonte dinâmica
filtroMatricula = ""
if(matricula){
  filtroMatricula = "id in (${matricula.join(',')})"
}

// Lista de matrículas
def matriculas = []

// Exemplo de utilização do parâmetro de matrícula como critério de consulta
fonteMatriculas.busca(criterio: filtroMatricula).each{ itemMatricula -> 
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
