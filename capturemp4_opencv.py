import cv2
import time
import argparse
import os


def start_opencv_pipelines(record_time, output_path):
    # Obtener la fecha y hora actual para generar nombres de archivo
    current_datetime = time.strftime("%Y%m%d_%H%M%S")

    # Configurar las direcciones RTSP de las cámaras
    camera_addresses = [
        "rtsp://admin:2Mini001.@192.168.88.131/live1",
        "rtsp://admin:2Mini001.@192.168.88.54/live1",
        "rtsp://admin:2Mini001.@192.168.88.81/live1",
        "rtsp://admin:2Mini001.@192.168.88.46/live1",
    ]

    cap_objects = []  # Lista para almacenar objetos de captura de video

    # Iniciar la captura de video para cada cámara
    for i, address in enumerate(camera_addresses):
        cap = cv2.VideoCapture(address)

        # Verificar si la captura de video se abrió correctamente
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {i + 1} en la dirección: {address}")
            continue

        cap_objects.append(cap)

    # Crear directorio de salida si no existe
    os.makedirs(output_path, exist_ok=True)

    # Iniciar la grabación para el tiempo especificado
    start_time = time.time()

    # Crear un archivo de video para cada cámara
    video_writers = [
        cv2.VideoWriter(
            f"{output_path}/camera{i + 1}_{current_datetime}.mp4",
            cv2.VideoWriter_fourcc(*"mp4v"),
            5.0,
            (
                int(cap.get(3)),
                int(cap.get(4)),
            ),  # Ajusta las dimensiones según tus necesidades
        )
        for i in range(len(cap_objects))
    ]

    while (time.time() - start_time) < record_time:
        frames = []

        # Capturar un frame de cada cámara
        for i, cap in enumerate(cap_objects):
            ret, frame = cap.read()

            # Verificar si la captura fue exitosa
            if ret:
                frames.append(frame)
            else:
                print(f"No se pudo capturar un frame de la cámara {i + 1}")

        # Escribir cada frame en el archivo de video correspondiente
        for i, frame in enumerate(frames):
            video_writers[i].write(frame)

    # Liberar recursos y cerrar las capturas de video
    for cap in cap_objects:
        cap.release()

    # Cerrar los archivos de video
    for writer in video_writers:
        writer.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Iniciar pipelines OpenCV con opciones configurables."
    )
    parser.add_argument(
        "--record-time", type=int, default=120, help="Tiempo de grabación en segundos"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="./videos_capturados",
        help="Ruta de salida para los videos capturados",
    )
    args = parser.parse_args()

    start_opencv_pipelines(args.record_time, args.output_path)
