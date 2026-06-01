import socket, os, hashlib

YELLOW = "\033[33m"
RESET = "\033[0m"

#Chave de criptografia simetrica XOR (deve ser identica no cliente)
CHAVE = b"REDES2026"

def enviar(mensagem,conn):
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

#Decriptografa payload recebido via XOR com a chave compartilhada
def decriptar(hex_str):
    cifrado = bytes.fromhex(hex_str)
    return bytes(b ^ CHAVE[i % len(CHAVE)] for i, b in enumerate(cifrado)).decode()

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

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    print_asc()

    conn, addr = server.accept()
    try:
        while True:
            modo_operacao = "[SERVIDOR]Escolha o método da operação\n[1]Go-backn\n[2]Repetição Seletiva\n"
            enviar(modo_operacao,conn)
            operacao_escolhida = receber(conn)
            if operacao_escolhida == "1":
                operacao = 1
                enviar("True",conn)
                print_asc()
                print("[CLIENTE]Operação escolhida foi [1]Go-backn\n")
                break
            elif operacao_escolhida == "2":
                operacao = 2
                enviar("True",conn)
                print_asc()
                print("[CLIENTE]Operação escolhida foi [2]Repetição Seletiva\n")
                break
            else:
                enviar("[SERVIDOR]Erro! Opção inválida! Repetindo operação...\n",conn)
                print_asc()
                print("[SERVIDOR]Erro! Opção inválida! Aguardando nova resposta...")
                continue
        
        enviar("[SERVIDOR]Qual o tamanho máximo de string que você deseja enviar? (Mínimo é 30.)\n",conn)
        tamanho_mensagem = int(receber(conn))
        
        print(f"[SERVIDOR]Cliente quer enviar uma string de tamanho {tamanho_mensagem}.\n")

        while True:
            try:
                tamanho_janela_inicial = int(input("[SERVIDOR]Escolha o tamanho da janela (1 a 5): "))
                if 1 <= tamanho_janela_inicial <= 5:
                    break
                print("[SERVIDOR]Valor inválido! Digite um número entre 1 e 5.")
            except ValueError:
                print("[SERVIDOR]Entrada inválida! Digite um número inteiro.")

        enviar(f"[SERVIDOR]Janela atual: {tamanho_janela_inicial} pacotes.\n", conn)
        enviar(str(tamanho_janela_inicial), conn)

        if tamanho_mensagem < 30:
            enviar(f"[SERVIDOR]NEGADO: Tamanho {tamanho_mensagem} é menor que o mínimo de 30.", conn)
            print("[SERVIDOR]Conexão recusada por tamanho insuficiente.")
        else:
            conn.send("[SERVIDOR]Tamanho aceito! Envie a string.\n".encode())
            print("[SERVIDOR]Tamanho validado. Aguardando recebimento da string.\n")

            janela_max = (tamanho_mensagem + 3) // 4
            nome_op = "Go-Back-N" if operacao == 1 else "Repetição Seletiva"
            print(f"[SERVIDOR]Modo {nome_op} iniciado.\n")
            print(f"[SERVIDOR]Máximo de pacotes esperados: {janela_max}\n")

            string_final = ""
            janela = 1

            #Go-Back-N: recebe até N pacotes por vez e valida janela completa antes de confirmar
            if operacao == 1:
                while janela <= janela_max:
                    tamanho_janela = min(tamanho_janela_inicial, janela_max - janela + 1)
                    print(f"[SERVIDOR]Aguardando janela: pacotes {janela} a {janela + tamanho_janela - 1}...")

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
                            print(f"[SERVIDOR]Timeout! Pacote {janela} não chegou. Enviando NACK...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
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
                            print(f"[SERVIDOR]Pacote malformado recebido. Enviando NACK...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
                            erro_detectado = True
                            break

                        print(f"[SERVIDOR]Recebido pacote {seq}: [{payload}] | CHK:{checksum}")

                        if not verificar_checksum(payload, checksum):
                            print(f"[SERVIDOR]Erro de integridade no pacote {seq}! Enviando NACK da janela...")
                            enviar(f"[SERVIDOR]NACK {janela_base}", conn)
                            erro_detectado = True
                            break

                        pacotes_janela.append(payload)
                        janela += 1

                    #Se não houve erro, confirma a janela com ACK cumulativo
                    if not erro_detectado and pacotes_janela:
                        for p in pacotes_janela:
                            string_final += p
                        confirmacao = f"[SERVIDOR]ACK {janela - 1}"
                        enviar(confirmacao, conn)
                        print(f"[SERVIDOR]ACK cumulativo enviado: {confirmacao}\n")

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
                        print(f"[SERVIDOR]Timeout! Pacote {janela} não chegou. Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {janela}", conn)
                        continue
                    finally:
                        conn.settimeout(None)

                    if not raw or raw == "####":
                        break

                    #Faz parse e valida checksum do pacote individual
                    try:
                        seq, payload, checksum = parsear_pacote(raw)
                    except Exception:
                        print(f"[SERVIDOR]Pacote malformado recebido. Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {janela}", conn)
                        continue

                    print(f"[SERVIDOR]Recebido pacote {seq}: [{payload}] | CHK:{checksum}")

                    if not verificar_checksum(payload, checksum):
                        print(f"[SERVIDOR]Erro de integridade no pacote {seq}! Enviando NACK...")
                        enviar(f"[SERVIDOR]NACK {seq}", conn)
                        continue

                    confirmacao = f"[SERVIDOR]ACK {seq} OK"
                    enviar(confirmacao, conn)
                    print(f"[SERVIDOR]Validação enviada: {confirmacao}\n")
                    string_final += payload
                    janela += 1

            print("\n[SERVIDOR]Sucesso! String completa recebida:")
            print(string_final)

    except Exception as e:
        print(f"\n[SERVIDOR] Erro ou conexão encerrada: {e}")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    start_server()