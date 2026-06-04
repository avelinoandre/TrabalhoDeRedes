import socket, os, hashlib
from cryptography.fernet import Fernet

BLUE = "\033[34m"
RESET = "\033[0m"

#Chave Fernet compartilhada (deve ser identica no servidor)
#Para gerar uma nova chave: Fernet.generate_key() e colar aqui e no servidor
FERNET = Fernet(b"fBlZBUrtT3vLmy2NRmCKEGKdu_7_PfNIi8e-4UdkgMA=")

def receber(client):
    return client.recv(1024).decode()

def enviar(mensagem, client):
    client.send(mensagem.encode())

def limparTerminal():
    os.system("cls" if os.name == "nt" else "clear")

def cabecalho():
    cliente = r"""
 ██████╗██╗     ██╗███████╗███╗   ██╗████████╗███████╗
██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝██╔════╝
██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   █████╗  
██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  
╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ███████╗
 ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
"""
    print(BLUE + cliente + RESET)

#Encripta payload via Fernet com a chave compartilhada e retorna em hexadecimal
def encriptar(texto):
    return FERNET.encrypt(texto.encode()).hex()

#Calcula checksum SHA-256 (primeiros 8 caracteres) do payload
def calcular_checksum(dados):
    return hashlib.sha256(dados.encode()).hexdigest()[:8]

#Monta pacote no formato: SEQ:<n>|DATA:<hex>|CHK:<checksum>
#Se corrompido=True, inverte o checksum para simular erro de integridade
def montar_pacote(seq, payload, corrompido=False):
    chk = calcular_checksum(payload)
    if corrompido:
        chk = chk[::-1]
    return f"SEQ:{seq}|DATA:{encriptar(payload)}|CHK:{chk}"

#Pergunta ao usuario quais pacotes devem ser corrompidos ou perdidos
def configurar_erros(total_pacotes):
    corrompidos = set()
    perdidos = set()

    resp = input("\n[CLIENTE]Deseja simular erros no envio? [s/N]: ").strip().lower()
    if resp != "s":
        return corrompidos, perdidos

    raw_corr = input(f"[CLIENTE]Informe os nºs dos pacotes a CORROMPER (1 a {total_pacotes}), separados por vírgula [Enter = nenhum]: ").strip()
    if raw_corr:
        for tok in raw_corr.split(","):
            try:
                n = int(tok.strip())
                if 1 <= n <= total_pacotes:
                    corrompidos.add(n)
            except ValueError:
                pass

    raw_perd = input(f"[CLIENTE]Informe os nºs dos pacotes a PERDER (1 a {total_pacotes}), separados por vírgula [Enter = nenhum]: ").strip()
    if raw_perd:
        for tok in raw_perd.split(","):
            try:
                n = int(tok.strip())
                if 1 <= n <= total_pacotes:
                    perdidos.add(n)
            except ValueError:
                pass

    print(f"[CLIENTE]Pacotes a corromper: {sorted(corrompidos) if corrompidos else 'nenhum'}")
    print(f"[CLIENTE]Pacotes a perder: {sorted(perdidos) if perdidos else 'nenhum'}\n")
    return corrompidos, perdidos

#Imprime o resumo da sessão ao final do envio
def imprimir_resumo(stats):
    print("\n" + "="*55)
    print("[CLIENTE] RESUMO DA SESSÃO")
    print("="*55)
    print(f"  Mensagem enviada              : {stats['tamanho_mensagem']} caracteres")
    print(f"  Total de pacotes              : {stats['total_pacotes']}")
    print(f"  Pacotes confirmados (ACK)     : {stats['acks_recebidos']}")
    print(f"  Retransmissões por NACK       : {stats['retransmissoes_nack']}")
    print(f"  Retransmissões por timeout    : {stats['retransmissoes_timeout']}")
    print(f"  Pacotes corrompidos simulados : {stats['corrompidos_simulados']}")
    print(f"  Pacotes perdidos simulados    : {stats['perdidos_simulados']}")
    print("="*55 + "\n")

def start_client():
    limparTerminal()
    cabecalho()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('localhost', 8080))

        operacao_escolhida = None
        while True:
            operacao = receber(client)
            print(operacao, end="")

            operacao_escolhida = input("-> ")
            enviar(operacao_escolhida, client)

            validacao = receber(client)
            if validacao == "True":
                break
            else:
                print(validacao, end="")
                continue

        tamanho_str = receber(client)
        print(tamanho_str, end="")

        #Valida se o tamanho informado pelo usuario atende o minimo exigido
        while True:
            tamanho_mensagem_raw = input("-> ").strip()
            try:
                tamanho_mensagem_int = int(tamanho_mensagem_raw)
                if tamanho_mensagem_int >= 30:
                    break
                print("[CLIENTE]Valor inválido! O tamanho mínimo é 30 caracteres. Tente novamente.")
            except ValueError:
                print("[CLIENTE]Entrada inválida! Digite um número inteiro.")

        tamanho_mensagem = tamanho_mensagem_raw
        print(f"Informando tamanho ({tamanho_mensagem}) ao servidor...")
        enviar(tamanho_mensagem, client)

        aviso_janela = receber(client)
        print(aviso_janela, end="")

        tamanho_janela = int(receber(client))

        resposta = receber(client)
        print(resposta, end="")

        if "Tamanho aceito" in resposta:

            while True:
                #Valida se a mensagem digitada cabe no limite combinado com o servidor
                while True:
                    mensagem = input(f"\nInforme a string que você deseja enviar (máx. {tamanho_mensagem_int} caracteres):\n-> ")
                    if len(mensagem) <= tamanho_mensagem_int:
                        break
                    print(f"[CLIENTE]Mensagem muito longa! Você digitou {len(mensagem)} caracteres, mas o limite é {tamanho_mensagem_int}. Tente novamente.")

                print("\nIniciando envio dos pacotes...")
                pacotes = [mensagem[i:i+4] for i in range(0, len(mensagem), 4)]

                corrompidos, perdidos = configurar_erros(len(pacotes))

                #Estatísticas da sessão para o resumo final
                stats = {
                    "tamanho_mensagem": len(mensagem),
                    "total_pacotes": len(pacotes),
                    "acks_recebidos": 0,
                    "retransmissoes_nack": 0,
                    "retransmissoes_timeout": 0,
                    "corrompidos_simulados": len(corrompidos),
                    "perdidos_simulados": len(perdidos),
                }

                #Go-Back-N: envia N pacotes por vez, retransmite a janela inteira em caso de NACK ou timeout
                if operacao_escolhida == "1":
                    i = 0
                    deu_erro_servidor = False

                    while i < len(pacotes):
                        janela = pacotes[i:i + tamanho_janela]
                        seq_base = i + 1
                        print(f"\n[CLIENTE]Enviando janela: pacotes {seq_base} a {seq_base + len(janela) - 1}...")

                        for j, fatia in enumerate(janela):
                            seq = i + j + 1
                            perdido = seq in perdidos
                            corrompido = seq in corrompidos

                            #Simula perda: pacote nao e enviado
                            if perdido:
                                print(f"[simulação][CLIENTE]Pacote SEQ:{seq} PERDIDO (não enviado)")
                                continue

                            pacote = montar_pacote(seq, fatia, corrompido=corrompido)
                            enviar(pacote, client)

                            if corrompido:
                                print(f"[simulação][CLIENTE]Pacote enviado (CORROMPIDO) SEQ:{seq}: [{fatia}]")
                            else:
                                print(f"Pacote enviado SEQ:{seq}: [{fatia}]")

                        if i + tamanho_janela >= len(pacotes):
                            enviar("####", client)

                        #Aguarda ACK/NACK com timeout para detectar perdas
                        client.settimeout(5)
                        try:
                            confirmacao = receber(client)
                        except socket.timeout:
                            print(f"\n[CLIENTE]Timeout! Sem resposta do servidor. Reenviando janela a partir do SEQ:{seq_base}...")
                            stats["retransmissoes_timeout"] += 1
                            continue
                        finally:
                            client.settimeout(None)

                        print(f"Resposta do servidor: {confirmacao}")

                        if "NACK" in confirmacao:
                            #Em Go-Back-N, retransmite a janela inteira a partir do pacote indicado
                            print(f"\n[CLIENTE]NACK recebido. Reenviando janela a partir do SEQ:{seq_base}...")
                            stats["retransmissoes_nack"] += 1
                            corrompidos.discard(seq_base)
                            perdidos.discard(seq_base)
                        elif "ERRO" in confirmacao:
                            print(f"\n[CLIENTE]O Servidor não aceitou: {confirmacao}")
                            deu_erro_servidor = True
                            break
                        else:
                            stats["acks_recebidos"] += 1
                            i += tamanho_janela

                #Repetição Seletiva: reenvia apenas o pacote rejeitado (NACK) ou perdido (timeout)
                else:
                    deu_erro_servidor = False

                    for j, fatia in enumerate(pacotes):
                        seq = j + 1
                        corrompido = seq in corrompidos
                        perdido = seq in perdidos

                        while True:
                            #Simula perda: pacote nao e enviado, aguarda timeout do servidor
                            if perdido:
                                print(f"[simulação][CLIENTE]Pacote SEQ:{seq} PERDIDO (não enviado)")
                            else:
                                pacote = montar_pacote(seq, fatia, corrompido=corrompido)
                                enviar(pacote, client)

                                if corrompido:
                                    print(f"[simulação][CLIENTE]Pacote enviado (CORROMPIDO) SEQ:{seq}: [{fatia}]")
                                else:
                                    print(f"Pacote enviado SEQ:{seq}: [{fatia}]")

                            #Aguarda confirmacao individual com timeout
                            client.settimeout(5)
                            try:
                                confirmacao = receber(client)
                            except socket.timeout:
                                print(f"[CLIENTE]Timeout! Sem resposta para SEQ:{seq}. Reenviando...")
                                stats["retransmissoes_timeout"] += 1
                                corrompidos.discard(seq)
                                perdidos.discard(seq)
                                perdido = False
                                corrompido = False
                                continue
                            finally:
                                client.settimeout(None)

                            print(f"Pacote SEQ:{seq} [{fatia}] | Resposta: {confirmacao}")

                            if "NACK" in confirmacao or "ERRO" in confirmacao:
                                #Em Repetição Seletiva, retransmite apenas o pacote rejeitado
                                print(f"[CLIENTE]NACK recebido, reenviando pacote SEQ:{seq} [{fatia}]...")
                                stats["retransmissoes_nack"] += 1
                                corrompidos.discard(seq)
                                perdidos.discard(seq)
                                perdido = False
                                corrompido = False
                                continue

                            stats["acks_recebidos"] += 1
                            break

                if deu_erro_servidor:
                    continue
                else:
                    print("\n[CLIENTE] Envio concluído com sucesso!")

                    #Exibe o resumo da sessão ao finalizar o envio
                    imprimir_resumo(stats)

                    input("Pressione ENTER para encerrar a conexão com o servidor...")
                    break
        else:
            print("[CLIENTE] Conexão encerrada pelo servidor (tamanho recusado).")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()