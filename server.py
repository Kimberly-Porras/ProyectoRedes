import socket

def startServer(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Servidor escuchando en: ", port)

    while True:
        # establecer conexión
        (c, addr) = s.accept()
        print("Se estableció conexión con: %s" % str(addr))

        # Recibir el nombre del archivo enviado por el cliente
        file_name = c.recv(1024).decode('utf-8')
        print("El contenido del archivo es:", file_name)

        # Recibir los datos del archivo
        file_data = c.recv(4096)
        print("Datos del archivo recibidos.")

        # Aquí puedes guardar los datos recibidos en un archivo
        # con el nombre especificado en 'file_name'

        c.close()

if __name__ == "__main__":
    host = ""
    port = 33330
    startServer(host, port)
