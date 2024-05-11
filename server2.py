import socket
import random

responseList = [
    'My name is Serverio.'
]

def startServer(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Servidor escuchando en:", port)

    sizeList = len(responseList)

    while True:
        # establecer conexión
        (c, addr) = s.accept()

        random_index = random.randrange(sizeList)
        
        print("Se estableció conexión con:", str(addr))
        message = responseList[random_index] + "\r\n"
        c.send(message.encode('utf8'))
        
        # Recibir el nombre del archivo enviado por el cliente
        file_name = c.recv(1024).decode('utf-8')
        print("El servidor recibió el archivo:", file_name)

        c.close()

if __name__ == "__main__":
    host = ""
    port = 33330
    startServer(host, port)