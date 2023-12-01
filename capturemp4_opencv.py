import cv2
import time
import argparse
import os


def start_opencv_pipelines(record_time, output_path):
    # Obtener la fecha y hora actual para generar nombres de archivo
    current_datetime = time.strftime("%Y%m%d_%H%M%S")

    # Configurar las direcciones RTSP de las cámaras
    camera_addresses = [
        "rtsp://admin:2Mini001.@192.168.88.131",
        "rtsp://admin:2Mini001.@192.168.88.54",
        "rtsp://admin:2Mini001.@192.168.88.81",
        "rtsp://admin:2Mini001.@192.168.88.46",
    ]

    cap_objects = []

    for i, address in enumerate(camera_addresses):
        cap = cv2.VideoCapture(address)

        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {i + 1} en la dirección: {address}")
            continue

        cap_objects.append(cap)

    os.makedirs(output_path, exist_ok=True)

    video_writers = [
        cv2.VideoWriter(
            f"{output_path}/camera{i + 1}_{current_datetime}.mp4",
            cv2.VideoWriter_fourcc(*"mp4v"),
            30,
            (
                int(cap.get(3)),
                int(cap.get(4)),
            ),  # Ajusta las dimensiones según tus necesidades
        )
        for i in range(len(cap_objects))
    ]

    buffer_size = 5  # Tamaño del buffer para almacenar los últimos fotogramas
    frame_buffers = [[] for _ in range(len(cap_objects))]

    start_time = time.time()

    while (time.time() - start_time) < record_time:
        frames = []

        for i, cap in enumerate(cap_objects):
            ret, frame = cap.read()

            if ret:
                frames.append(
                    (i, frame, time.time())
                )  # Almacenar el número de cámara, el fotograma y el timestamp
            else:
                print(f"No se pudo capturar un frame de la cámara {i + 1}")

        # Actualizar los buffers de fotogramas
        for i, frame_info in enumerate(frames):
            frame_buffers[i].append(frame_info)

            # Mantener el tamaño del buffer
            if len(frame_buffers[i]) > buffer_size:
                frame_buffers[i] = frame_buffers[i][-buffer_size:]

        # Sincronizar fotogramas y escribir en archivos de video
        for i, buffer in enumerate(frame_buffers):
            if (
                len(buffer) == buffer_size
            ):  # Solo sincronizar si hay suficientes fotogramas
                timestamps = [frame_info[2] for frame_info in buffer]
                min_timestamp = min(timestamps)

                # Ajustar los fotogramas y escribir en el archivo de video
                for frame_info in buffer:
                    adjusted_frame = frame_info[1]
                    timestamp_diff = frame_info[2] - min_timestamp
                    # Aplicar ajuste de tiempo según la diferencia de timestamps
                    # Aquí, puedes usar interpolación temporal u otros métodos según tus necesidades
                    # adjusted_frame = adjust_frame_by_time(frame_info[1], timestamp_diff)

                    video_writers[i].write(adjusted_frame)

    for cap in cap_objects:
        cap.release()

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
