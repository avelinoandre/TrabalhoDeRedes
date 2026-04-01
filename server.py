import socket, os

YELLOW = "\033[33m"
RESET = "\033[0m"

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
        enviar("[SERVIDOR]Janela atual: 5 pacotes.\n",conn)

        if tamanho_mensagem < 30:
            enviar(f"[SERVIDOR]NEGADO: Tamanho {tamanho_mensagem} é menor que o mínimo de 30.", conn)
            print("[SERVIDOR]Conexão recusada por tamanho insuficiente.")
        else:
            conn.send("[SERVIDOR]Tamanho aceito! Envie a string.\n".encode())
            print("[SERVIDOR]Tamanho validado. Aguardando recebimento da string.\n")

            if operacao in (1, 2):
                nome_op = "Go-Back-N" if operacao == 1 else "Repetição Seletiva"
                print(f"[SERVIDOR]Modo {nome_op} iniciado.\n")

                while True:
                    string_final = ""
                    janela = 1
                    janela_max = (tamanho_mensagem + 3) // 4
                    estourou_limite = False

                    while True:
                            pacote = conn.recv(4).decode()
                            
                            if not pacote: break

                            # valida se a quantidade de pacotes foi ultrapassada
                            if janela > janela_max:
                                # DISPARA O ERRO PARA O CLIENTE
                                enviar("[SERVIDOR]ERRO: Limite excedido! Reenvie a string.", conn)
                                print(f"\n[SERVIDOR]ERRO: Cliente tentou enviar pacote {janela}, ultrapassando o limite de {janela_max} pacotes!")
                                estourou_limite = True
                                
                                try:
                                    while conn.recv(1024): pass
                                except socket.timeout:
                                    pass
                                conn.settimeout(None)
                                break

                            # Confirmação normal
                            confirmacao = f"[SERVIDOR]ACK {janela}" if operacao == 1 else "certo"
                            enviar(confirmacao, conn)
                            string_final += pacote
                            
                            if operacao == 1:
                                print(f"[SERVIDOR]Recebido pacote {janela}: [{pacote}]")
                            else:
                                print(f"[SERVIDOR]Recebido pacote: [{pacote}]")
                                
                            janela += 1

                    if estourou_limite:
                        print("[SERVIDOR] Exigindo reenvio. Aguardando nova string...\n")
                        continue 

                    if not estourou_limite and string_final != "":
                        print("\n[SERVIDOR]Sucesso! String completa recebida:")
                        print(string_final)
                        break

    except Exception as e:
        print(f"\n[SERVIDOR] Erro ou conexão encerrada: {e}")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    start_server()