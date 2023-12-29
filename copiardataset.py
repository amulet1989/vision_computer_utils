import os
import shutil
import logging
import argparse


def organizar_videos(directorio_base, directorio_destino):
    # Configurar el sistema de logs
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Crear el directorio destino si no existe
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)

    # Recorrer la estructura de carpetas
    for fecha in os.listdir(directorio_base):
        directorio_fecha = os.path.join(directorio_base, fecha)
        if os.path.isdir(directorio_fecha):
            for hora in os.listdir(directorio_fecha):
                directorio_hora = os.path.join(directorio_fecha, hora)
                if os.path.isdir(directorio_hora):
                    for camara in os.listdir(directorio_hora):
                        directorio_camara = os.path.join(directorio_hora, camara)
                        if os.path.isdir(directorio_camara):
                            # Crear la subcarpeta para la cámara en el directorio destino
                            carpeta_camara_destino = os.path.join(
                                directorio_destino, camara
                            )
                            if not os.path.exists(carpeta_camara_destino):
                                os.makedirs(carpeta_camara_destino)

                            # Recorrer los archivos de video en la cámara
                            for video in os.listdir(directorio_camara):
                                if video.endswith(".mp4"):
                                    # Crear un nombre único para el video
                                    nombre_video = f"{camara}_{fecha}_{hora}_{video}"

                                    # Construir la ruta completa del archivo de origen y destino
                                    ruta_origen = os.path.join(directorio_camara, video)
                                    ruta_destino = os.path.join(
                                        carpeta_camara_destino, nombre_video
                                    )

                                    # Copiar y renombrar el archivo
                                    shutil.copy2(ruta_origen, ruta_destino)

                                    # Log de la operación
                                    logging.info(
                                        f"Copiando {ruta_origen} a {ruta_destino}"
                                    )

    # Log de finalización
    logging.info("Proceso completado.")


if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Organizar videos de cámaras.")
    parser.add_argument(
        "directorio_base", help="Directorio base de los videos de cámaras."
    )
    parser.add_argument(
        "directorio_destino", help="Directorio de destino para organizar los videos."
    )

    # Obtener los argumentos del comando
    args = parser.parse_args()

    # Ejecutar la función con los directorios proporcionados
    organizar_videos(args.directorio_base, args.directorio_destino)
