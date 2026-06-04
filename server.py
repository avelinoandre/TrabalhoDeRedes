import socket, os, hashlib, threading
from cryptography.fernet import Fernet

YELLOW = "\033[33m"
RESET = "\033[0m"

#Chave Fernet compartilhada (deve ser identica no cliente)
#Para gerar uma nova chave: Fernet.generate_key() e substituir abaixo
CHAVE = b"REDES2026_padded_to_32bytes_aaaaa="  #Placeholder — use a mesma chave gerada no cliente
FERNET = Fernet(b"fBlZBUrtT3vLmy2NRmCKEGKdu_7_PfNIi8e-4UdkgMA=")

def enviar(mensagem, conn):
    conn.send(mensagem.encode())

def receber(conn):
    return conn.recv(1024).decode()

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def cabecalho():
    servidor = r"""
███████╗███████╗██████╗ ██╗   ██╗██╗██████╗  ██████╗ ██████╗ 
██╔════╝██╔════╝██╔══██╗██║   ██║██║██╔══██╗██╔═══██╗██╔══██╗
███████╗█████╗  ██████╔╝██║   ██║██║██║  ██║██║   ██║██████╔╝
╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██║██║  ██║██║   ██║██╔══██╗
███████║███████╗██║  ██║ ╚████╔╝ ██║██████╔╝╚██████╔╝██║  ██║
╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
"""
    print(YELLOW + servidor + RESET)

def print_asc():
    limpar_tela()
    cabecalho()

#Decriptografa payload recebido via Fernet com a chave compartilhada
def decriptar(token_hex):
    token = bytes.fromhex(token_hex)
    return FERNET.decrypt(token).decode()

#Calcula checksum SHA-256 (primeiros 8 caracteres) do payload
def calcular_checksum(dados):
    return hashlib.sha256(dados.encode()).hexdigest()[:8]

#Verifica se o checksum recebido bate com o payload decriptado
def verificar_checksum(dados, checksum_recebido):
    return calcular_checksum(dados) == checksum_recebido

#Faz o parse de um pacote no formato: SEQ:<n>|DATA:<hex>|CHK:<checksum>
def parsear_pacote(raw):
    partes = dict(p.split(":", 1) for p in raw.split("|"))
    seq = int(partes["SEQ"])
    payload = decriptar(partes["DATA"])
    checksum = partes["CHK"]
    return seq, payload, checksum

#Imprime o resumo da sessão ao final do atendimento
def imprimir_resumo(stats):
    print("\n" + "="*55)
    print("[SERVIDOR] RESUMO DA SESSÃO")
    print("="*55)
    print(f"  Pacotes recebidos com sucesso : {stats['pacotes_ok']}")
    print(f"  Erros de integridade (NACK)   : {stats['erros_integridade']}")
    print(f"  Timeouts detectados           : {stats['timeouts']}")
    print(f"  ACKs enviados                 : {stats['acks_enviados']}")
    print(f"  NACKs enviados                : {stats['nacks_enviados']}")
    print(f"  Mensagem reconstruída         : {stats['tamanho_final']} caracteres")
    print("="*55 + "\n")

#Lida com a conexão de um cliente em uma thread separada
def handle_client(conn, addr):
    print(f"\n[SERVIDOR] Nova conexão de {addr}")
    
    #Estatísticas da sessão para o resumo final
    stats = {
        "pacotes_ok": 0,
        "erros_integridade": 0,
        "timeouts": 0,
        "acks_enviados": 0,
        "nacks_enviados": 0,
        "tamanho_final": 0,
    }

    try:
        while True:
            modo_operacao = "[SERVIDOR]Escolha o método da operação\n[1]Go-backn\n[2]Repetição Seletiva\n"
            enviar(modo_operacao, conn)
            operacao_escolhida = receber(conn)
            if operacao_escolhida == "1":
                operacao = 1
                enviar("True", conn)
                print(f"[{addr}][CLIENTE]Operação escolhida foi [1]Go-backn\n")
                break
            elif operacao_escolhida == "2":
                operacao = 2
                enviar("True", conn)
                print(f"[{addr}][CLIENTE]Operação escolhida foi [2]Repetição Seletiva\n")
                break
            else:
                enviar("[SERVIDOR]Erro! Opção inválida! Repetindo operação...\n", conn)
                print(f"[{addr}][SERVIDOR]Opção inválida. Aguardando nova resposta...")
                continue

        enviar("[SERVIDOR]Qual o tamanho máximo de string que você deseja enviar? (Mínimo é 30.)\n", conn)
        tamanho_mensagem = int(receber(conn))

        print(f"[{addr}][SERVIDOR]Cliente quer enviar uma string de tamanho {tamanho_mensagem}.\n")

        while True:
            try:
                tamanho_janela_inicial = int(input(f"[SERVIDOR][{addr}]Escolha o tamanho da janela (1 a 5): "))
                if 1 <= tamanho_janela_inicial <= 5:
                    break
                print("[SERVIDOR]Valor inválido! Digite um número entre 1 e 5.")
            except ValueError:
                print("[SERVIDOR]Entrada inválida! Digite um número inteiro.")

        enviar(f"[SERVIDOR]Janela atual: {tamanho_janela_inicial} pacotes.\n", conn)
        enviar(str(tamanho_janela_inicial), conn)

        if tamanho_mensagem < 30:
            enviar(f"[SERVIDOR]NEGADO: Tamanho {tamanho_mensagem} é menor que o mínimo de 30.", conn)
            print(f"[{addr}][SERVIDOR]Conexão recusada por tamanho insuficiente.")
        else:
            conn.send("[SERVIDOR]Tamanho aceito! Envie a string.\n".encode())
            print(f"[{addr}][SERVIDOR]Tamanho validado. Aguardando recebimento da string.\n")

            janela_max = (tamanho_mensagem + 3) // 4
            nome_op = "Go-Back-N" if operacao == 1 else "Repetição Seletiva"
            print(f"[{addr}][SERVIDOR]Modo {nome_op} iniciado.\n")
            print(f"[{addr}][SERVIDOR]Máximo de pacotes esperados: {janela_max}\n")

            string_final = ""
            janela = 1

            #Go-Back-N: recebe até N pacotes por vez e valida janela completa antes de confirmar
            if operacao == 1:
                while janela <= janela_max:
                    tamanho_janela = min(tamanho_janela_inicial, janela_max - janela + 1)
                    print(f"[{addr}][SERVIDOR]Aguardando janela: pacotes {janela} a {janela + tamanho_janela - 1}...")

                    pacotes_janela = []
                    fim_antecipado = False
                    janela_base = janela
                    erro_detectado = False

                    for _ in range(tamanho_janela):
                        #Aguarda pacote com timeout para detectar perdas
                        conn.settimeout(5)
                        try:
                            raw = conn.recv(1024).decode()
                        except socket.timeout:
                            print(f"[{addr}][SERVIDOR]Timeout! Pacote {janela} não chegou. Enviando NACK...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
                            stats["timeouts"] += 1
                            stats["nacks_enviados"] += 1
                            erro_detectado = True
                            break
                        finally:
                            conn.settimeout(None)

                        if not raw or raw == "####":
                            fim_antecipado = True
                            break

                        #Faz parse e valida checksum de cada pacote recebido
                        try:
                            seq, payload, checksum = parsear_pacote(raw)
                        except Exception:
                            print(f"[{addr}][SERVIDOR]Pacote malformado recebido. Enviando NACK...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
                            stats["nacks_enviados"] += 1
                            erro_detectado = True
                            break

                        print(f"[{addr}][SERVIDOR]Recebido pacote {seq}: [{payload}] | CHK:{checksum}")

                        if not verificar_checksum(payload, checksum):
                            print(f"[{addr}][SERVIDOR]Erro de integridade no pacote {seq}! Enviando NACK da janela...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
                            stats["erros_integridade"] += 1
                            stats["nacks_enviados"] += 1
                            erro_detectado = True
                            break

                        pacotes_janela.append(payload)
                        stats["pacotes_ok"] += 1
                        janela += 1

                    #Se não houve erro, confirma a janela com ACK cumulativo
                    if not erro_detectado and pacotes_janela:
                        for p in pacotes_janela:
                            string_final += p
                        confirmacao = f"[SERVIDOR]ACK {janela - 1}"
                        enviar(confirmacao, conn)
                        stats["acks_enviados"] += 1
                        print(f"[{addr}][SERVIDOR]ACK cumulativo enviado: {confirmacao}\n")

                    if fim_antecipado:
                        break

                    #Em Go-Back-N, volta ao inicio da janela se houve erro
                    if erro_detectado:
                        janela = janela_base

            #Repetição Seletiva: valida e confirma cada pacote individualmente
            elif operacao == 2:
                while janela <= janela_max:
                    #Aguarda cada pacote com timeout para detectar perdas
                    conn.settimeout(5)
                    try:
                        raw = conn.recv(1024).decode()
                    except socket.timeout:
                        print(f"[{addr}][SERVIDOR]Timeout! Pacote {janela} não chegou. Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {janela}", conn)
                        stats["timeouts"] += 1
                        stats["nacks_enviados"] += 1
                        continue
                    finally:
                        conn.settimeout(None)

                    if not raw or raw == "####":
                        break

                    #Faz parse e valida checksum do pacote individual
                    try:
                        seq, payload, checksum = parsear_pacote(raw)
                    except Exception:
                        print(f"[{addr}][SERVIDOR]Pacote malformado recebido. Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {janela}", conn)
                        stats["nacks_enviados"] += 1
                        continue

                    print(f"[{addr}][SERVIDOR]Recebido pacote {seq}: [{payload}] | CHK:{checksum}")

                    if not verificar_checksum(payload, checksum):
                        print(f"[{addr}][SERVIDOR]Erro de integridade no pacote {seq}! Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {seq}", conn)
                        stats["erros_integridade"] += 1
                        stats["nacks_enviados"] += 1
                        continue

                    confirmacao = f"[SERVIDOR]ACK {seq} OK"
                    enviar(confirmacao, conn)
                    stats["acks_enviados"] += 1
                    print(f"[{addr}][SERVIDOR]Validação enviada: {confirmacao}\n")
                    string_final += payload
                    stats["pacotes_ok"] += 1
                    janela += 1

            stats["tamanho_final"] = len(string_final)

            print(f"\n[{addr}][SERVIDOR]Sucesso! String completa recebida:")
            print(string_final)

            #Exibe o resumo da sessão ao finalizar o atendimento deste cliente
            imprimir_resumo(stats)

    except Exception as e:
        print(f"\n[SERVIDOR][{addr}] Erro ou conexão encerrada: {e}")
    finally:
        conn.close()
        print(f"[SERVIDOR] Conexão com {addr} encerrada.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(5)
    print_asc()
    print("[SERVIDOR] Aguardando conexões (Ctrl+C para encerrar)...\n")

    #Loop principal: aceita clientes continuamente, cada um em uma thread separada
    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Encerrado pelo usuário.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()