# Projeto Cliente-Servidor via Socket 💻

Projeto desenvolvido para a cadeira de **Redes** da **C.E.S.A.R School**, que consiste na implementação de uma aplicação cliente-servidor utilizando sockets em Python. O objetivo é colocar em prática conceitos essenciais de redes de computadores: estabelecimento de conexão, controle de fluxo, detecção de erros, criptografia e sincronização entre aplicações distribuídas.

## Objetivo 📑

- Desenvolver um sistema de comunicação utilizando sockets em Python;
- Utilizar a arquitetura cliente-servidor com suporte a múltiplos clientes simultâneos (via threads);
- Realizar um handshake inicial para negociação dos parâmetros da sessão;
- Implementar os protocolos de controle de fluxo **Go-Back-N** e **Repetição Seletiva**;
- Garantir a integridade dos dados através de checksums SHA-256;
- Proteger o conteúdo transmitido com criptografia simétrica via **Fernet**;
- Permitir a simulação de erros (pacotes corrompidos e perdidos) para fins didáticos.

## Handshake 🤝

No início de cada conexão, cliente e servidor negociam os parâmetros da sessão:

1. **Modo de operação**: Go-Back-N (`1`) ou Repetição Seletiva (`2`);
2. **Tamanho máximo da mensagem**: definido pelo cliente (mínimo de 30 caracteres);
3. **Tamanho da janela de transmissão**: definido pelo servidor (1 a 5 pacotes).

Esse procedimento garante que ambas as partes operem com as mesmas regras ao longo de toda a comunicação.

## Protocolos de Controle de Fluxo 🔁

### Go-Back-N
O cliente envia uma janela de N pacotes por vez. Em caso de **NACK** (erro de integridade) ou **timeout**, toda a janela é retransmitida a partir do pacote problemático. O servidor confirma a janela com um **ACK cumulativo**.

### Repetição Seletiva
O cliente envia e aguarda confirmação para cada pacote individualmente. Em caso de **NACK** ou **timeout**, apenas o pacote rejeitado é retransmitido, sem impactar os demais.

## Integridade e Segurança 🔒

- **Checksum SHA-256**: os primeiros 8 caracteres do hash SHA-256 do payload são incluídos em cada pacote. O servidor rejeita pacotes cujo checksum não corresponda ao conteúdo recebido;
- **Criptografia Fernet**: o payload de cada pacote é cifrado com uma chave simétrica compartilhada entre cliente e servidor antes do envio. O servidor decifra ao receber;
- **Formato do pacote**: `SEQ:<n>|DATA:<hex_cifrado>|CHK:<checksum>`.

## Simulação de Erros 🧪

Antes do envio, o cliente permite configurar quais pacotes devem ser **corrompidos** (checksum invertido) ou **perdidos** (não enviados), possibilitando observar o comportamento de cada protocolo diante de falhas na rede. Ambos os lados exibem um resumo ao final da sessão com estatísticas de ACKs, NACKs, retransmissões e timeouts.

## Tecnologias Utilizadas ⚙️

- Python 3;
- Biblioteca `socket` (nativa);
- Biblioteca `threading` (nativa) — múltiplos clientes simultâneos no servidor;
- Biblioteca `hashlib` (nativa) — checksums SHA-256;
- Biblioteca `cryptography` — criptografia simétrica via Fernet.

## Estrutura 📄

```
TrabalhoDeRedes/
├── cliente.py
├── server.py
└── README.md
```

## Guia de Execução ⚙️

### Pré-requisitos

- Python instalado;
- Biblioteca `cryptography` instalada (ver passo abaixo).

### 1. Clonar o repositório

```bash
git clone https://github.com/avelinoandre/TrabalhoDeRedes.git
cd TrabalhoDeRedes
```

### 2. Instalar dependências

```bash
pip install cryptography
```

Alternativas:

```bash
uv pip install cryptography
# ou
python -m pip install cryptography
```

### 3. Executar o servidor

```bash
python server.py
```

O servidor ficará aguardando conexões e aceitará múltiplos clientes em paralelo. Para cada nova conexão, será solicitado o **tamanho da janela** diretamente no terminal do servidor.

### 4. Executar o cliente

Em outro terminal:

```bash
python cliente.py
```

Siga as instruções exibidas no terminal: escolha o protocolo, informe o tamanho da mensagem, configure eventuais erros simulados e envie a string.

## Fluxo de Funcionamento 🖥️

```
Cliente                          Servidor
  |                                  |
  |---- escolha do protocolo ------> |
  |<--- confirmação ----------------- |
  |---- tamanho da mensagem -------> |
  |<--- tamanho da janela ----------- |
  |                                  |
  |==== envio dos pacotes (loop) ==== |
  |---- SEQ:n|DATA:<enc>|CHK:<chk> ->|  (verifica checksum e decifra)
  |<--- ACK / NACK ------------------ |  (retransmite se NACK ou timeout)
  |                                  |
  |---- encerramento da conexão ---->|
```

## Uso de Inteligência Artificial 🧠

A IA foi utilizada como apoio na formatação de código, organização das estruturas de controle e na investigação de abordagens para sinalizar o fim do envio de pacotes.

## Considerações 📄

Este projeto consolidou, na prática, conceitos fundamentais de redes de computadores: controle de fluxo com janela deslizante, detecção e recuperação de erros, criptografia de dados em trânsito e programação concorrente com threads. A implementação lado a lado de Go-Back-N e Repetição Seletiva permitiu comparar diretamente o impacto de cada estratégia diante de perdas e corrupções simuladas.
