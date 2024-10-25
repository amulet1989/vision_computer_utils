import cv2
import numpy as np
import os


def add_black_frames(
    input_video_path, output_video_path, fps, add_start_seconds, add_end_seconds
):
    # Cargar el video original
    cap = cv2.VideoCapture(input_video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calcular el número de frames a añadir al inicio y al final
    add_start_frames = int(fps * add_start_seconds)
    add_end_frames = int(fps * add_end_seconds)

    # Configurar el writer para el video de salida
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # *'avc1' - "mp4v"
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Crear un frame negro
    black_frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Añadir frames negros al inicio
    for _ in range(add_start_frames):
        out.write(black_frame)

    # Escribir el video original
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    # Añadir frames negros al final
    for _ in range(add_end_frames):
        out.write(black_frame)

    # Liberar los recursos
    cap.release()
    out.release()


# Parámetros

# Ruta a la carpeta de videso
video_folder = "videos_capturados/concatenado/3"
video_out = "videos_capturados/concatenado/3/out"
os.makedirs(video_out, exist_ok=True)
paths_de_videos = os.listdir(video_folder)
print(paths_de_videos)
# output_video_path = "videos_capturados/concatenado/sincronizados/TRACK_POZO_FRIO_sync.mp4"  # Ruta del video de salida

fps = 10  # Frames por segundo
add_start_seconds = 0.0  # Segundos a añadir al inicio
add_end_seconds = 0.0  # Segundos a añadir al final

for video in paths_de_videos:
    input_video_path = os.path.join(video_folder, video)
    output_video_path = os.path.join(video_out, video)
    add_black_frames(
        input_video_path, output_video_path, fps, add_start_seconds, add_end_seconds
    )
