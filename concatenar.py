import os
import subprocess
import argparse


def concatenar_videos_cronologicamente(directorio_base, directorio_salida):
    # Obtener la lista de carpetas de cámaras en el directorio base
    carpetas_camaras = [
        d
        for d in os.listdir(directorio_base)
        if os.path.isdir(os.path.join(directorio_base, d))
    ]

    # Iterar sobre las carpetas de cámaras
    for camara in carpetas_camaras:
        # Construir la ruta de la carpeta de la cámara en el directorio base
        carpeta_camara = os.path.join(directorio_base, camara)

        # Obtener la lista de archivos de video en la carpeta de la cámara
        videos = [f for f in os.listdir(carpeta_camara) if f.endswith(".mp4")]

        # Ordenar los videos por nombre para garantizar el orden cronológico
        videos.sort()

        # Construir la ruta del archivo de salida
        ruta_video_salida = os.path.join(directorio_salida, f"{camara}.mp4")

        # Construir la lista de rutas de los videos a concatenar
        rutas_videos = [os.path.join(carpeta_camara, video) for video in videos]

        # Usar ffmpeg para concatenar los videos en orden cronológico
        comando_ffmpeg = [
            "ffmpeg",
            "-i",
            f'concat:{"|".join(rutas_videos)}',
            "-c",
            "copy",
            ruta_video_salida,
        ]

        # Ejecutar el comando ffmpeg
        subprocess.run(comando_ffmpeg)

    print("Concatenación completada")


def main():
    parser = argparse.ArgumentParser(
        description="Concatenar cronológicamente clips de video en cada carpeta de cámara."
    )
    parser.add_argument(
        "directorio_base",
        help="Ruta al directorio base de la estructura de directorios de videos.",
    )
    parser.add_argument(
        "directorio_salida",
        help="Ruta al directorio de salida para los archivos de video concatenados.",
    )

    args = parser.parse_args()

    concatenar_videos_cronologicamente(args.directorio_base, args.directorio_salida)


if __name__ == "__main__":
    main()
