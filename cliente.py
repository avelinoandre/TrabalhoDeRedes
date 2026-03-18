import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(('localhost', 8080))

        #Recebe um print de server pedindo o tamanho máximo da string a ser enviada
        informacao_inicial = client.recv(1024).decode()
        print(informacao_inicial)

        tamanho_mensagem = int(input(""))
        

        print(f"Informando tamanho ({tamanho_mensagem}) ao servidor.")
        client.send(str(tamanho_mensagem).encode())

        #Recebe o retorno do servidor, caso volte "OK", o tamanho é válido
        resposta = client.recv(1024).decode()

        if resposta == "OK":
            print("Servidor autorizou!\n")
            mensagem = input(f"Informe a string que você deseja enviar (até {tamanho_mensagem}):\n")
            #Envia a string em blocos de 4
            for i in range(0, len(mensagem), 4):
                fatia = mensagem[i:i+4]
                client.send(fatia.encode())
            print("Enviado")
        else:
            print(f"Servidor recusou: {resposta}")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()