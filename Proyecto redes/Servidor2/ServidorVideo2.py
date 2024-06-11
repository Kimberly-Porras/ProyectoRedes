import os
import socket
import threading
import time
import json

class ServidorVideo:
    def __init__(self, puerto, ruta_videos, ip_servidor_principal, puerto_servidor_principal):
        self.puerto = int(puerto)
        self.ruta_videos = ruta_videos
        self.ip_servidor_principal = ip_servidor_principal
        self.puerto_servidor_principal = int(puerto_servidor_principal)
        self.sock_principal = None
        self.heartbeat_interval = 10
        self.lista_videos = self.obtener_lista_videos()  # Inicializa la lista de videos
        self.polling_interval = 10

    def iniciar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.puerto))
        self.sock.listen(5)
        ip = socket.gethostbyname(socket.gethostname())
        print(f"Servidor de video escuchando en IP: {ip}, Puerto: {self.puerto}")
        threading.Thread(target=self.escuchar_conexiones).start()
        self.conectar_servidor_principal()
        threading.Thread(target=self.verificar_servidor_principal).start()
        threading.Thread(target=self.monitorear_carpeta_videos).start()

    def conectar_servidor_principal(self):
        while True:
            try:
                self.sock_principal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock_principal.connect((self.ip_servidor_principal, self.puerto_servidor_principal))
                lista_videos = self.obtener_lista_videos()
                mensaje = f'NUEVO_SERVIDOR,{self.puerto},{json.dumps(lista_videos)}'
                self.sock_principal.send(mensaje.encode())
                print(f"Conectado al servidor principal en {self.ip_servidor_principal}:{self.puerto_servidor_principal}")
                break
            except Exception as e:
                print(f"Error conectando al servidor principal: {e}")
                time.sleep(5)  # Intenta reconectar después de 5 segundos

    def obtener_lista_videos(self):
        videos = []
        for archivo in os.listdir(self.ruta_videos):
            if archivo.endswith('.mp4'):
                ruta = os.path.join(self.ruta_videos, archivo)
                tamaño = os.path.getsize(ruta)
                videos.append({'nombre': archivo, 'tamaño': tamaño, 'ruta': ruta})
        return videos

    def notificar_cambio_videos(self):
        try:
            if self.sock_principal:
                lista_videos = self.obtener_lista_videos()
                mensaje = f'ACTUALIZAR_VIDEOS,{self.puerto},{json.dumps(lista_videos)}'
                self.sock_principal.send(mensaje.encode())
                print("Notificación de cambio de videos enviada al servidor principal")
        except Exception as e:
            print(f"Error notificando cambio de videos: {e}")

    def escuchar_conexiones(self):
        while True:
            conn, addr = self.sock.accept()
            threading.Thread(target=self.manejar_conexion, args=(conn, addr)).start()

    def manejar_conexion(self, conn, addr):
        print(f"Conexión establecida con {addr}")
        try:
            while True:
                datos = conn.recv(1024).decode()
                if datos:
                    print(f"Datos recibidos de {addr}: {datos}")
                    partes = datos.split(" ")
                    if len(partes) == 3:
                        video_nombre = partes[0]
                        try:
                            inicio = int(partes[1])
                            fin = int(partes[2])
                            self.enviar_trozo_video(conn, video_nombre, inicio, fin)
                        except ValueError as e:
                            print(f"Error en los índices de video: {e}")
                    else:
                        print(f"Formato de mensaje incorrecto: {datos}")
                else:
                    break
        except Exception as e:
            print(f"Error al manejar conexión: {e}")
        finally:
            conn.close()
            print(f"Conexión cerrada con {addr}")

    def enviar_trozo_video(self, conn, video_nombre, inicio, fin):
        ruta_video = os.path.join(self.ruta_videos, video_nombre)
        if not os.path.exists(ruta_video):
            print(f"Video no encontrado: {video_nombre}")
            return
        try:
            with open(ruta_video, 'rb') as f:
                f.seek(inicio)
                while inicio < fin:
                    tamano_chunk = min(1024, fin - inicio)
                    trozo = f.read(tamano_chunk)
                    if not trozo:
                        break
                    conn.sendall(trozo)
                    inicio += tamano_chunk
                    time.sleep(0.01)
                    print(f"Enviado trozo de tamaño {tamano_chunk} del video {video_nombre}")
        except Exception as e:
            print(f"Error enviando trozo del video: {e}")

    def procesar_solicitud(self, datos, conn):
        pass

    def verificar_servidor_principal(self):
        while True:
            try:
                if self.sock_principal is None:
                    self.conectar_servidor_principal()
                else:
                    self.sock_principal.send(b'heartbeat')
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print("Servidor principal no detectado, pausando servidor de video.")
                self.sock_principal = None
                time.sleep(30)

    def monitorear_carpeta_videos(self):
        while True:
            time.sleep(self.polling_interval)
            nueva_lista_videos = self.obtener_lista_videos()
            if nueva_lista_videos != self.lista_videos:
                self.lista_videos = nueva_lista_videos
                self.notificar_cambio_videos()

if __name__ == "__main__":
    puerto = 12346
    ruta_videos = r'C:\Users\User\Desktop\Proyecto redes\Servidor2\video'
    ip_servidor_principal = '192.168.0.146'
    puerto_servidor_principal = 8000
    servidor_video = ServidorVideo(puerto, ruta_videos, ip_servidor_principal, puerto_servidor_principal)
    servidor_video.iniciar()
