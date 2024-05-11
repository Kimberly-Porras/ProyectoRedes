import socket

def secondaryServer(host, port, file_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print("Conectado al servidor principal.")

    with open(file_path, 'r') as file:
        data = file.read()
        s.send(data.encode('utf-8'))

    print("Archivo enviado al servidor principal.")
    input("Presione Enter para salir.")

    s.close()

if __name__ == "__main__":
    host = ""  # Cambia esto a la dirección IP del servidor principal si no está en la misma máquina
    port = 33330

    secondary_host = "192.168.0.163"  # Cambia esto a la dirección IP del servidor principal si no está en la misma máquina
    secondary_port = 33330
    file_path = input("Ingrese la ruta del archivo que desea enviar al servidor principal: ")
    secondaryServer(secondary_host, secondary_port, file_path)  # Inicia el servidor secundario y envía el archivo