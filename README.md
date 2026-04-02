## Projeto Cliente-Servidor via socket 💻

Projeto desenvolvido para a cadeira de **Redes** da **C.E.S.A.R School**, que consiste no desenvolvimento de uma aplicação cliente-servidor utilizando sockets em Python, com o objetivo de colocar em prática conceitos essenciais de redes de computadores, como o estabelecimento de conexão, a troca de informações e a sincronização entre diferentes aplicações.

Como etapa inicial do processo de comunicação, é realizado um handshake entre cliente e servidor. Nesse momento, são definidos os principais parâmetros que irão regular a troca de dados ao longo da conexão.


## Objetivo 📑

* Desenvolver um sistema de comunicação utilizando sockets em Python;
* Utilizar a arquitetura cliente-servidor para estruturar a aplicação;
* Estabelecer um handshake entre as aplicações;
* Gerenciar o fluxo de dados conforme parâmetros previamente definidos.

## Handshake 🤝

No início da conexão, cliente e servidor realizam uma troca de informações com o objetivo de estabelecer parâmetros fundamentais da comunicação, como o **modo de operação** e o **tamanho máximo das mensagens**. Esse procedimento assegura que ambas as partes sigam as mesmas regras ao longo de toda a interação

## Tecnologias Utilizadas ⚙️

* Python (Versão 3.14.3);
* Biblioteca Socket nativa do Python.

## Estrutura 📄

```
--- TrabalhoDeRedes
    |__ cliente.py
    |__ server.py
    |__ README.md

```
## Guia de execução ⚙️

### Pré-requisito:

* Deve possuir ` Python ` instalado

### 1. Clonar o repositório
```
git clone https://github.com/avelinoandre/TrabalhoDeRedes.git
cd TrabalhoDeRedes

```
### 2. Executar o servidor
Use o comando `python server.py` para iniciar o servidor, que ficará aguardando conexões.

### 3. Executar o cliente
Em outro terminal, use o comando `python cliente.py` e utilize o sistema conforme os comandos do terminal.

## Funcionamento 🖥️

O **cliente** inicia a conexão com o **servidor**, seguido pela realização de um **handshake**, no qual são definidos o modo de operação e o tamanho máximo das mensagens. Em seguida, ocorre a **troca de dados** entre cliente e servidor, e, ao final, a conexão é devidamente encerrada.

## Uso de Inteligência Artificial 🧠
A IA foi usada para ajudar na formatação de códigos e organização e também para ajudar em formas de efetuar o "stop" do envio de pacotes.

## Considerações 📄
Este projeto permitiu consolidar, na prática, conceitos fundamentais de redes de computadores por meio da implementação de uma comunicação cliente-servidor. A aplicação do handshake e o controle da troca de dados mostram a importância da padronização e sincronização entre sistemas. Além disso, o desenvolvimento contribuiu para uma melhor compreensão do funcionamento de conexões em rede e da organização de aplicações distribuídas
