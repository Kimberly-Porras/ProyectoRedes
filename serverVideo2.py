import socket

def secondaryServer(host, port, file_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print("Conectado al servidor principal.")

    # Envía solo el nombre del archivo
    s.send(file_name.encode('utf-8'))

    print("Archivo enviado al servidor principal:", file_name)
    input("Presione Enter para salir.")

    s.close()

if __name__ == "__main__":
    host = ""  # Cambia esto a la dirección IP del servidor principal si no está en la misma máquina
    port = 33330

    secondary_host = "192.168.0.163"  # Cambia esto a la dirección IP del servidor principal si no está en la misma máquina
    secondary_port = 33330
    file_name = input("Ingrese el nombre del archivo que desea enviar al servidor principal: ")
    secondaryServer(secondary_host, secondary_port, file_name)  # Inicia el servidor secundario y envía el nombre del archivo