import socket
import json
import math
import os
import time

class Cliente:
    def __init__(self, servidor_principal_host, servidor_principal_puerto, carpeta_destino):
        self.servidor_principal_host = servidor_principal_host
        self.servidor_principal_puerto = servidor_principal_puerto
        self.carpeta_destino = carpeta_destino
        if not os.path.exists(self.carpeta_destino):
            os.makedirs(self.carpeta_destino)

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

        fragmentos = []
        inicio_tiempo = time.time()
        for ip, puerto, mensaje in mensajes:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, int(puerto)))
                s.sendall(mensaje.encode())
                nombre_fragmento = self.recibir_trozo_video(s, video_nombre, mensaje, ip, puerto)
                if nombre_fragmento:
                    fragmentos.append(nombre_fragmento)
        fin_tiempo = time.time()
        duracion = fin_tiempo - inicio_tiempo
        print(f"Tiempo total de transferencia: {duracion:.2f} segundos")

        self.combinar_fragmentos(video_nombre, fragmentos)

    def recibir_trozo_video(self, sock, video_nombre, mensaje, ip, puerto):
        partes = mensaje.split(" ")
        inicio = int(partes[1])
        fin = int(partes[2])
        tamaño_total = fin - inicio
        datos_recibidos = b''
        nombre_fragmento = f"{video_nombre}_{inicio}_{fin}.mp4"

        try:
            with open(nombre_fragmento, "wb") as f:
                while len(datos_recibidos) < tamaño_total:
                    data = sock.recv(1024)
                    if not data:
                        break
                    datos_recibidos += data
                    f.write(data)
            print(f"Recibido trozo del video {video_nombre} de {inicio} a {fin}, tamaño: {len(datos_recibidos)} bytes desde {ip}:{puerto}")
            return nombre_fragmento
        except Exception as e:
            print(f"Error al recibir trozo del video desde {ip}:{puerto}: {e}")
            return None

    def combinar_fragmentos(self, video_nombre, fragmentos):
        ruta_video_completo = os.path.join(self.carpeta_destino, f"{video_nombre}_completo.mp4")
        with open(ruta_video_completo, "wb") as video_final:
            for fragmento in sorted(fragmentos):
                with open(fragmento, "rb") as f:
                    video_final.write(f.read())
                os.remove(fragmento)
            print(f"Video {video_nombre} ensamblado correctamente en {ruta_video_completo}")

if __name__ == "__main__":
    carpeta_destino = r'C:\Users\joxan\OneDrive\Documentos\GitHub\ProyectoRedes\Proyecto redes\Videos Descargados'
    cliente = Cliente('172.17.45.235', 8000, carpeta_destino)
    lista_servidores = cliente.solicitar_lista_servidores()
    videos_disponibles = cliente.mostrar_servidores_y_videos(lista_servidores)
    video_elegido = cliente.elegir_video(videos_disponibles)
    servidores = videos_disponibles[video_elegido]
    video_tamaño = servidores[0][2]
    cliente.enviar_mensajes_a_servidores(servidores, video_elegido, video_tamaño)