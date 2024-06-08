import socket
import json
import math

class Cliente:
    def __init__(self, servidor_principal_host, servidor_principal_puerto):
        self.servidor_principal_host = servidor_principal_host
        self.servidor_principal_puerto = servidor_principal_puerto

    def solicitar_lista_servidores(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.servidor_principal_host, self.servidor_principal_puerto))
            s.sendall(b'solicitud lista servidores')
            data = s.recv(4096).decode('utf-8')
            lista_servidores = json.loads(data)
            return lista_servidores

    def mostrar_servidores_y_videos(self, lista_servidores):
        videos_disponibles = {}
        for servidor, info in lista_servidores.items():
            ip, puerto = servidor.split(":")
            for video in info['videos']:
                if video['nombre'] not in videos_disponibles:
                    videos_disponibles[video['nombre']] = []
                videos_disponibles[video['nombre']].append((ip, puerto, video['tamaño']))
        return videos_disponibles

    def elegir_video(self, videos_disponibles):
        print("Videos disponibles:")
        for i, video in enumerate(videos_disponibles.keys(), start=1):
            print(f"{i}. {video}")
        eleccion = int(input("Seleccione un video por número: ")) - 1
        video_elegido = list(videos_disponibles.keys())[eleccion]
        return video_elegido

    def enviar_mensajes_a_servidores(self, servidores, video_nombre, video_tamaño):
        num_servidores = len(servidores)
        chunk_size = math.ceil(video_tamaño / num_servidores)
        mensajes = []

        for i, (ip, puerto, _) in enumerate(servidores):
            inicio = i * chunk_size
            fin = min((i + 1) * chunk_size, video_tamaño)
            mensaje = f"{video_nombre} {inicio} {fin}"
            mensajes.append((ip, puerto, mensaje))

        for ip, puerto, mensaje in mensajes:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, int(puerto)))
                s.sendall(mensaje.encode())
                # Recibir el trozo del video
                self.recibir_trozo_video(s, mensaje)

    def recibir_trozo_video(self, sock, mensaje):
        partes = mensaje.split(" ")
        video_nombre = partes[0]
        inicio = int(partes[1])
        fin = int(partes[2])
        tamaño_total = fin - inicio
        datos_recibidos = b''

        try:
            while len(datos_recibidos) < tamaño_total:
                data = sock.recv(1024)
                if not data:
                    break
                datos_recibidos += data
            print(f"Recibido trozo del video {video_nombre} de {inicio} a {fin}, tamaño: {len(datos_recibidos)} bytes")
        except Exception as e:
            print(f"Error al recibir trozo del video: {e}")

if __name__ == "__main__":
    cliente = Cliente('192.168.0.146', 8000)
    lista_servidores = cliente.solicitar_lista_servidores()
    videos_disponibles = cliente.mostrar_servidores_y_videos(lista_servidores)
    video_elegido = cliente.elegir_video(videos_disponibles)
    servidores = videos_disponibles[video_elegido]
    video_tamaño = servidores[0][2]  # Asumimos que el tamaño del video es el mismo en todos los servidores
    cliente.enviar_mensajes_a_servidores(servidores, video_elegido, video_tamaño)