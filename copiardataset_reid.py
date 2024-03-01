import os
import shutil
import argparse


def procesar_directorios(directorio_base, directorio_salida):
    # Obtener la lista de carpetas con fechas
    fechas = os.listdir(directorio_base)

    # Iterar sobre las carpetas de fechas
    for fecha in fechas:
        ruta_fecha = os.path.join(directorio_base, fecha)

        # Verificar si es un directorio
        if os.path.isdir(ruta_fecha):
            # Crear directorio en el directorio de salida
            directorio_salida_fecha = os.path.join(directorio_salida, fecha)
            os.makedirs(directorio_salida_fecha, exist_ok=True)

            # Obtener la lista de carpetas con horas
            horas = os.listdir(ruta_fecha)

            # Iterar sobre las carpetas de horas
            for hora in horas:
                ruta_hora = os.path.join(ruta_fecha, hora)

                # Verificar si es un directorio
                if os.path.isdir(ruta_hora):
                    # Obtener la lista de carpetas de cámaras
                    camaras = os.listdir(ruta_hora)

                    # Iterar sobre las carpetas de cámaras
                    for camara in camaras:
                        ruta_camara = os.path.join(ruta_hora, camara)

                        # Verificar si es un directorio
                        if os.path.isdir(ruta_camara):
                            # Crear directorio en el directorio de salida
                            directorio_salida_camara = os.path.join(
                                directorio_salida_fecha, camara
                            )
                            os.makedirs(directorio_salida_camara, exist_ok=True)

                            # Obtener la lista de archivos de video
                            videos = os.listdir(ruta_camara)

                            # Iterar sobre los archivos de video
                            for video in videos:
                                ruta_video_original = os.path.join(ruta_camara, video)

                                # Obtener información de la cámara, hora, minutos y segundos
                                _, extension = os.path.splitext(video)
                                camara_nombre = camara.lower()
                                hora_nombre = hora
                                minutos, segundos = os.path.splitext(video)[0].split(
                                    "."
                                )

                                # Crear nuevo nombre del video
                                nuevo_nombre = f"{camara_nombre}_{hora_nombre}_{minutos}.{segundos}{extension}"

                                # Construir la ruta de destino
                                ruta_video_destino = os.path.join(
                                    directorio_salida_camara, nuevo_nombre
                                )

                                # Copiar el archivo al nuevo directorio con el nuevo nombre
                                shutil.copy(ruta_video_original, ruta_video_destino)

    print("Proceso completado")


def main():
    parser = argparse.ArgumentParser(
        description="Procesar estructura de directorios de videos."
    )
    parser.add_argument(
        "--directorio_base",
        help="Ruta al directorio base de la estructura de directorios de videos.",
    )
    parser.add_argument(
        "--directorio_salida",
        help="Ruta al directorio de salida para la nueva estructura de directorios.",
    )

    args = parser.parse_args()

    procesar_directorios(args.directorio_base, args.directorio_salida)


if __name__ == "__main__":
    main()
