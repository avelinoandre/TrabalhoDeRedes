import socket, os

BLUE = "\033[34m"
RESET = "\033[0m"

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

def start_client():
    limparTerminal()
    cabecalho()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(('localhost', 8080))

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

        tamanho_mensagem = input("-> ")
        print(f"Informando tamanho ({tamanho_mensagem}) ao servidor...")
        enviar(tamanho_mensagem, client)

        aviso_janela = receber(client)
        print(aviso_janela, end="")

        resposta = receber(client)
        print(resposta, end="")

        if "Tamanho aceito" in resposta:
            
            while True:
                mensagem = input(f"\nInforme a string que você deseja enviar:\n-> ")
                
                print("\nIniciando envio dos pacotes...")
                deu_erro_servidor = False
                
                #enviando a string em blocos de 4
                for i in range(0, len(mensagem), 4):
                    fatia = mensagem[i:i+4]
                    enviar(fatia, client)
                    
                    confirmacao = receber(client)
                    print(f"Pacote enviado: [{fatia}] | Resposta: {confirmacao}")
                    
                    #Recebe a validação do server
                    if "ERRO" in confirmacao:
                        print(f"\n[CLIENTE] O Servidor não aceitou: {confirmacao}")
                        deu_erro_servidor = True
                        break
                
                if deu_erro_servidor:
                    continue # Volta pro "Informe a string..."
                else:
                    print("\n[CLIENTE] Envio concluído com sucesso!")
                    input("\nPressione ENTER para encerrar a conexão com o servidor...")
                    break
        else:
            print("[CLIENTE] Conexão encerrada pelo servidor (tamanho recusado).")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()