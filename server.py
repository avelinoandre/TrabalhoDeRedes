import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    print("Servidor Aguardando Conexão")

    conn, addr = server.accept()
    try:
        mensagem_incial = "Qual o tamanho máximo de string que você deseja enviar? (Mínimo é 30.)\n"
        conn.send(mensagem_incial.encode())

        #Recebe o tamanho máximo da string
        resposta = conn.recv(1024).decode()
        if not resposta: return

        tamanho_mensagem = int(resposta)
        
        print(f"Cliente quer enviar uma string de tamanho {tamanho_mensagem}.")

        #Verifica se o tamanho é maior ou igual a 30, se sim, continua
        if tamanho_mensagem < 30:
            mensagem_erro = f"NEGADO: Tamanho {tamanho_mensagem} é menor que o mínimo de 30."
            conn.send(mensagem_erro.encode())
            print("Conexão recusada por tamanho insuficiente.")
        
        else:
            conn.send("OK".encode())
            print("Tamanho validado. Aguardando recebimento da string")

        #Recebe a string em blocos de 4
        string_final = ""
        while len(string_final) < tamanho_mensagem:
            bloco = conn.recv(4).decode()
            if not bloco: break
            string_final += bloco
            print(f"Recebido bloco: [{bloco}]")

        print(f"\nSucesso! String completa: {string_final}")

    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    start_server()