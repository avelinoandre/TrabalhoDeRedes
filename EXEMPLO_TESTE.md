# Exemplos de Mensagens para Teste

## Mensagens Válidas (≥30 caracteres)

Use estas mensagens para testar o funcionamento correto do sistema:

1. `Esta é uma mensagem de teste com mais de trinta caracteres para validação`
2. `O sistema de troca de mensagens está funcionando corretamente agora`
3. `Python é uma linguagem de programação muito poderosa e versátil`
4. `Redes de computadores permitem a comunicação entre dispositivos`
5. `O protocolo TCP garante a entrega confiável de dados na rede`
6. `Este projeto implementa Go-Back-N e Repetição Seletiva com ACK`
7. `A comunicação cliente-servidor funciona através de sockets TCP`
8. `Mensagens são fragmentadas em pacotes de 4 caracteres cada um`
9. `O servidor valida checksum SHA-256 antes de confirmar pacotes`
10. `Estatísticas de ACKs e NACKs são exibidas ao final da sessão`

## Mensagens Inválidas (<30 caracteres)

O sistema rejeita o **tamanho configurado** antes mesmo do envio — a validação ocorre no cliente ao digitar a mensagem. Se o tamanho informado no handshake for menor que 30, o servidor encerrará a conexão. Use os exemplos abaixo para testar essas rejeições:

1. `Oi`
2. `Teste`
3. `Mensagem curta`
4. `Muito pequeno`
5. `Falha`
6. `ABC123`
7. `Python`
8. `Redes`
9. `TCP/IP`
10. `Socket`

## Cenários de Teste

### Teste 1: Conexão Básica e Handshake
1. Inicie o servidor com `python server.py`
2. Inicie o cliente com `python cliente.py` em outro terminal
3. No cliente, escolha o protocolo: `1` para Go-Back-N ou `2` para Repetição Seletiva
4. Informe o tamanho máximo da mensagem (mínimo 30)
5. No servidor, escolha o tamanho da janela (1 a 5)
6. Observe as confirmações de handshake em ambos os terminais

### Teste 2: Envio Sem Erros Simulados
1. Realize o handshake completo
2. Quando perguntado sobre erros, responda `N`
3. Envie a mensagem: `Esta é uma mensagem de teste com mais de trinta caracteres`
4. Observe os pacotes sendo enviados (fragmentos de 4 chars cada)
5. Verifique os ACKs recebidos e o resumo da sessão ao final

### Teste 3: Simulação de Pacotes Corrompidos
1. Realize o handshake e informe uma mensagem com pelo menos 40 caracteres
2. Quando perguntado sobre erros, responda `s`
3. Informe o número de um pacote para corromper (ex.: `2`)
4. Observe o NACK emitido pelo servidor ao detectar falha no checksum
5. Verifique a retransmissão automática pelo protocolo escolhido

### Teste 4: Simulação de Pacotes Perdidos
1. Realize o handshake normalmente
2. Quando perguntado sobre erros, responda `s`
3. Informe o número de um pacote para perder (ex.: `3`)
4. Observe o timeout no servidor após 5 segundos sem receber o pacote
5. Verifique o NACK por timeout e a retransmissão correspondente

### Teste 5: Comparação entre Go-Back-N e Repetição Seletiva
1. Execute a sessão com Go-Back-N (`1`) simulando erro no pacote `2`
2. Observe que **toda a janela** a partir do pacote 2 é retransmitida
3. Execute novamente com Repetição Seletiva (`2`) simulando o mesmo erro
4. Observe que **somente o pacote 2** é retransmitido
5. Compare os resumos de retransmissões ao final de cada sessão

### Teste 6: Tamanho de Janela Variável
1. Realize o handshake e, no servidor, defina janela = `1`
2. Envie uma mensagem e observe o comportamento pacote a pacote
3. Repita com janela = `5` e compare a velocidade de confirmação
4. Simule um erro com janela grande para ver o impacto do Go-Back-N

## Comandos Úteis

### Iniciar o servidor:
```bash
python server.py
```

### Iniciar o cliente:
```bash
python cliente.py
```

### Instalar dependência necessária:
```bash
pip install cryptography
```

## Análise de Logs

### Log do Servidor — Handshake e Recebimento (Go-Back-N):
```
[SERVIDOR] Nova conexão de ('127.0.0.1', 54321)
[('127.0.0.1', 54321)][CLIENTE] Operação escolhida foi [1]Go-backn

[('127.0.0.1', 54321)][SERVIDOR] Cliente quer enviar uma string de tamanho 60.

[('127.0.0.1', 54321)][SERVIDOR] Aguardando janela: pacotes 1 a 3...
[('127.0.0.1', 54321)][SERVIDOR] Recebido pacote 1: [Esta] | CHK:a1b2c3d4
[('127.0.0.1', 54321)][SERVIDOR] Recebido pacote 2: [ é u] | CHK:b2c3d4e5
[('127.0.0.1', 54321)][SERVIDOR] Recebido pacote 3: [ma m] | CHK:c3d4e5f6
[('127.0.0.1', 54321)][SERVIDOR] ACK cumulativo enviado: [SERVIDOR]ACK 3
```

### Log do Servidor — Erro de Integridade (NACK):
```
[('127.0.0.1', 54321)][SERVIDOR] Recebido pacote 2: [ensa] | CHK:xxxxxxxx
[('127.0.0.1', 54321)][SERVIDOR] Erro de integridade no pacote 2! Enviando NACK da janela...
```

### Log do Servidor — Timeout por Pacote Perdido:
```
[('127.0.0.1', 54321)][SERVIDOR] Timeout! Pacote 3 não chegou. Enviando NACK...
```

### Log do Cliente — Envio Normal:
```
[CLIENTE] Enviando janela: pacotes 1 a 3...
Pacote enviado SEQ:1: [Esta]
Pacote enviado SEQ:2: [ é u]
Pacote enviado SEQ:3: [ma m]
Resposta do servidor: [SERVIDOR]ACK 3
```

### Log do Cliente — Pacote Corrompido Simulado:
```
[simulação][CLIENTE] Pacote enviado (CORROMPIDO) SEQ:2: [ensa]
Resposta do servidor: [SERVIDOR]NACK 1
[CLIENTE] NACK recebido. Reenviando janela a partir do SEQ:1...
```

### Log do Cliente — Pacote Perdido Simulado:
```
[simulação][CLIENTE] Pacote SEQ:3 PERDIDO (não enviado)
[CLIENTE] Timeout! Sem resposta do servidor. Reenviando janela a partir do SEQ:1...
```

### Resumo da Sessão — Cliente:
```
=======================================================
[CLIENTE] RESUMO DA SESSÃO
=======================================================
  Mensagem enviada              : 52 caracteres
  Total de pacotes              : 13
  Pacotes confirmados (ACK)     : 13
  Retransmissões por NACK       : 1
  Retransmissões por timeout    : 0
  Pacotes corrompidos simulados : 1
  Pacotes perdidos simulados    : 0
=======================================================
```

### Resumo da Sessão — Servidor:
```
=======================================================
[SERVIDOR] RESUMO DA SESSÃO
=======================================================
  Pacotes recebidos com sucesso : 13
  Erros de integridade (NACK)   : 1
  Timeouts detectados           : 0
  ACKs enviados                 : 5
  NACKs enviados                : 1
  Mensagem reconstruída         : 52 caracteres
=======================================================
```

## Troubleshooting

### Erro: `OSError: [Errno 98] Address already in use`
**Solução:** A porta 8080 ainda está ocupada por uma sessão anterior. Aguarde alguns segundos e tente novamente, ou encerre o processo que a está usando:
```bash
# Linux/macOS
fuser -k 8080/tcp
```

### Erro: `ConnectionRefusedError`
**Solução:** O servidor não está rodando. Inicie o `server.py` antes de executar o `cliente.py`.

### Erro: `cryptography.fernet.InvalidToken`
**Solução:** As chaves Fernet em `cliente.py` e `server.py` estão diferentes. Certifique-se de que ambos os arquivos usam exatamente a mesma chave no campo `FERNET`.

### Cliente fica travado aguardando resposta
**Solução:** O timeout é de 5 segundos. Se o servidor travar ou a conexão cair, o cliente emitirá uma mensagem de timeout e tentará retransmitir automaticamente.

### Mensagem rejeitada ao digitar
**Solução:** A mensagem digitada ultrapassa o tamanho máximo informado no handshake. Digite uma mensagem menor ou reinicie a sessão informando um tamanho maior.

### Servidor não exibe nada após a conexão do cliente
**Solução:** O servidor aguarda que o operador defina o tamanho da janela no terminal. Verifique o terminal do servidor e informe um valor entre 1 e 5.
