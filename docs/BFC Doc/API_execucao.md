## API de Execução


O bfc-script disponibiliza uma API para a consulta das informações relacionadas a execução.



#### Consultar o protocolo da execução


1. Execucao.atual.protocolo





#### Consultar se a execução foi cancelada pelo usuário


1. Execucao.atual.foiCancelada





### Exemplos


Monitorar o cancelamento e interromper a execução:

1. percorrer(...) {
2.
3.   // processamento da aplicação
4.
5.   // verifica e interompe caso a execução atual foi cancelada
6.   se(Execucao.atual.foiCancelada){
7.     interomper 'Execucao cancelada'
8.   }
9.
10. }
