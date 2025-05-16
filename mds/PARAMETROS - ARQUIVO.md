# 📌 Criando parâmetro do tipo Arquivo
---
## Finalidade
Consultar e manipular um arquivo fornecido como entrada de dados. Muito utilizado em scripts de manipulação de arquivos e importações de dados.
# 📝 Guia para criação do parâmetro
---
### 🧑‍💻 Criando um parâmetro:
![Criando parâmetro](screenshots/Screenshot_1.png)
### 🧑‍💻 Configurando parâmetro para ler o arquivo:
![Parâmetro Arquivo](screenshots/Screenshot_6.png)

# ⚙️ Utilizando e manipulando o parâmetro de arquivo
---
### 🧑‍💻 Consumindo e manipulando um arquivo fornecido através do parâmetro.
```
// Declarando o parâmetro de entrada do tipo .CSV
def arquivo = Arquivo.ler(parametros.arquivo.valor, 'csv', [encoding: 'iso-8859-1'] )

// Declarando o parâmetro de entrada do tipo .TXT
def arquivo = Arquivo.ler(parametros.arquivo.valor, 'txt')

// Caso precisar pular o cabeçalho do arquivo .CSV
if (pularPrimeiraLinha) {
  arquivo.pularLinhas(1)
}

// Exemplo de leitura de um arquivo
while (arquivo.contemProximaLinha()) {
    String linha = arquivo.lerLinha().toString()
    List<String> valores = linha.split(/\|/); // Pode variar conforme encoding do arquivo
    Long numInscricao = Long.valueOf(valores[0]);
    nota = Numeros.numero(valores[1].replace(",","."));
    imprimir linha
    imprimir "Num.: " + numInscricao + " | Nota: " + nota
}
```
