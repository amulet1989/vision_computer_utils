import cv2
import time
import argparse
import os
import yaml

# Camaras de Queue managemente
# cam = [
#     [
#         246,
#         247,
#         248,
#         249,
#         250,
#     ],
#     [122, 71, 62, 52],
# ]

# Camaras de Turnero
# cam = [["234_640x480"], ["65_640x480"]]
# cam = [["245_704x576"], ["245"]]
cam = [
    [
        # "Entrada1",
        # # "Entrada2",
        # "Track_3",
        # "Track_4",
        # "Track_5",
        # "Track_6",
        # "Track_7",
        # "Salida1",
        # "Salida2",
        # "Ojo_pez",
        "G7V",
        "G8V",
        "G9V",
        "G10V",
        "G11V",
    ],
    ["otras"],
]


# Lee el archivo YAML "cameras.yaml"
with open("cameras.yaml", "r") as file:
    data = yaml.safe_load(file)

# Asigna las direcciones a la variable camera_addresses
camera_addresses = data["cameras"]

# Imprime para verificar
print(camera_addresses)


def start_opencv_pipelines(camera_addresses, cam, record_time, output_path):
    """
    Start OpenCV pipelines for each camera and record the output to a video file.
    :param camera_addresses: List of camera addresses.
    :param cam: List of camera names.
    :param record_time: Time in seconds to record the output.
    :param output_path: Path to the output directory.

    """

    # Obtener la fecha y hora actual para generar nombres de archivo
    current_datetime = time.strftime("%Y%m%d_%H%M%S")

    cap_objects = []  # Lista para almacenar objetos de captura de video

    # Iniciar la captura de video para cada cámara
    for i, address in enumerate(camera_addresses):

        cap = cv2.VideoCapture(address)

        # Verificar si la captura de video se abrió correctamente
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {cam[i]} en la dirección: {address}")
            continue

        cap_objects.append(cap)

    # Crear directorio de salida si no existe
    os.makedirs(output_path, exist_ok=True)

    # Iniciar la grabación para el tiempo especificado
    start_time = time.time()

    # Crear un archivo de video para cada cámara
    video_writers = [
        cv2.VideoWriter(
            f"{output_path}/camera{cam[i]}_{current_datetime}.mp4",
            cv2.VideoWriter_fourcc(*"mp4v"),
            20.0,
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
                print(f"No se pudo capturar un frame de la cámara {cam[i]}")

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
        "--record-time", type=int, default=30, help="Tiempo de grabación en segundos"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="./videos_capturados",
        help="Ruta de salida para los videos capturados",
    )
    args = parser.parse_args()

    for i in range(len(camera_addresses)):
        print(camera_addresses[i], cam[i])
        start_opencv_pipelines(
            camera_addresses[i], cam[i], args.record_time, args.output_path
        )
