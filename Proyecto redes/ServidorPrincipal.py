import socket
import threading
import json

class ServidorPrincipal:
    def __init__(self, ip, puerto):
        # Inicializa el servidor principal con la IP y el puerto especificados
        self.ip = ip
        self.puerto = int(puerto)
        # Diccionario para almacenar los servidores de vídeo registrados
        self.servidores = {}

    def iniciar(self):
        # Configura el socket para escuchar conexiones entrantes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.puerto))
        self.sock.listen(5)
        print(f"Servidor principal escuchando en IP: {self.ip}, Puerto: {self.puerto}")
        # Inicia un hilo para escuchar conexiones entrantes
        threading.Thread(target=self.escuchar_conexiones).start()

    def escuchar_conexiones(self):
        while True:
            # Acepta nuevas conexiones
            conn, addr = self.sock.accept()
            # Inicia un nuevo hilo para manejar cada conexión entrante
            threading.Thread(target=self.manejar_conexion, args=(conn, addr)).start()

    def manejar_conexion(self, conn, addr):
        print(f"Conexión establecida con {addr}")
        try:
            while True:
                # Recibe datos de la conexión
                datos = conn.recv(4096).decode()
                if datos:
                    if datos == 'heartbeat':
                        # Omitir la impresión de los mensajes de heartbeat
                        continue
                    print(f"Datos recibidos de {addr}: {datos}")
                    if datos.startswith('NUEVO_SERVIDOR'):
                        # Registra un nuevo servidor de vídeo
                        self.registrar_servidor(datos, addr)
                    elif datos == 'solicitud lista servidores':
                        # Envía la lista de servidores al cliente que la solicitó
                        self.enviar_lista_servidores(conn)
                else:
                    break
        except Exception as e:
            print(f"Error al manejar conexión: {e}")
        finally:
            # Cierra la conexión cuando se termina de manejar
            conn.close()
            print(f"Conexión cerrada con {addr}")

    def registrar_servidor(self, datos, addr):
        try:
            # Divide los datos recibidos para extraer el puerto y la lista de vídeos
            partes = datos.split(',', 2)
            puerto = int(partes[1])
            lista_videos = json.loads(partes[2])
            ip_servidor = addr[0]
            # Registra el servidor de vídeo en el diccionario
            self.servidores[(ip_servidor, puerto)] = {'videos': lista_videos}
            print(f"Servidor registrado: {ip_servidor}:{puerto} con videos: {lista_videos}")
        except Exception as e:
            print(f"Error registrando servidor: {e}")

    def enviar_lista_servidores(self, conn):
        try:
            # Convierte el diccionario de servidores a un formato adecuado para enviar
            servidores_str = {f"{ip}:{puerto}": data for (ip, puerto), data in self.servidores.items()}
            data = json.dumps(servidores_str)
            # Envía la lista de servidores al cliente
            conn.sendall(data.encode('utf-8'))
            print(f"Lista de servidores enviada: {data}")
        except Exception as e:
            print(f"Error enviando lista de servidores: {e}")

if __name__ == "__main__":
    # Crea una instancia del servidor principal y lo inicia
    servidor_principal = ServidorPrincipal('192.168.0.146', 8000)
    servidor_principal.iniciar()
