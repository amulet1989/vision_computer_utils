import cv2
import time
import argparse
import os
import yaml
from ultralytics import YOLO

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
cam = [["245_704x576"], ["245"]]

# Lee el archivo YAML "cameras.yaml"
with open("cameras.yaml", "r") as file:
    data = yaml.safe_load(file)

# Asigna las direcciones a la variable camera_addresses
camera_addresses = data["cameras"]

# Imprime para verificar
print(camera_addresses)


# Obtener roi_x, roi_y, roi_width, roi_height a partir de cuatro puntos en la imagen
# roi=[97, 76], [605, 93], [595, 417], [86, 433]
def get_center_width_height(roi):
    """
    Calculate the bounding box (center_x, center_y, width, height) from four points.
    :param roi: List of four points [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
    :return: Tuple (center_x, center_y, width, height) defining the bounding box.
    """
    x_coords = [point[0] for point in roi]
    y_coords = [point[1] for point in roi]

    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)

    width = max_x - min_x
    height = max_y - min_y
    center_x = min_x + width / 2
    center_y = min_y + height / 2

    return center_x, center_y, width, height


# Función para decidir si algunas de la sdetecciones están dentro de una ROI determinada
def is_inside_roi(bboxs, roi):
    # [97, 76], [605, 93], [595, 417], [86, 433]
    #
    roi_x, roi_y, roi_width, roi_height = get_center_width_height(roi)

    for bbox in bboxs:
        # Check if the detected class is 'person'
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        if (roi_x <= center_x <= roi_x + roi_width) and (
            roi_y <= center_y <= roi_y + roi_height
        ):
            print(f"persona en:, ({center_x}, {center_y})")
            return True

    return False


# Funcion para detectar si hay personas
def detect_person_rtsp(rtsp_url, model, detection_time=5, roi=[]):
    """
    Detect persons in a RTSP stream using YOLOv8 model.
    :param rtsp_url: URL of the RTSP stream.
    :param model: YOLOv8 model.
    :param detection_time: Time in seconds to perform detection.
    :return: True if a person is detected, False otherwise.
    """
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir el flujo RTSP en {rtsp_url}")
        return False

    start_time = time.time()
    person_detected = False

    while time.time() - start_time < detection_time:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame del flujo RTSP")
            break

        # Realizar la inferencia con YOLOv8
        results = model(source=frame, conf=0.5, iou=0.7, imgsz=640)  #
        for result in results:
            boxes = result.boxes
            if boxes.cls.numel() > 0:  # Comprobar si la clase detectada es 'person'
                if is_inside_roi(boxes.xyxy, roi):
                    # print(boxes.cls.tolist())
                    person_detected = True
                    break

        if person_detected:
            break

    cap.release()
    return person_detected


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

    model = YOLO("trained_models/yolov8m_cf_caja_640x480_v12.pt")
    roi = [[97, 76], [605, 93], [595, 417], [86, 433]]
    while True:
        if detect_person_rtsp(camera_addresses[0][0], model, detection_time=3, roi=roi):
            print("Se detectaron personas en la cámara 1.")
            print("Grabando ...")

            for i in range(len(camera_addresses)):
                print(camera_addresses[i], cam[i])
                start_opencv_pipelines(
                    camera_addresses[i], cam[i], args.record_time, args.output_path
                )
        else:
            print("No se detectaron personas en ninguna de las cámaras.")

        print("Esperando 10 minutos antes de volver a verificar y grabar...")
        time.sleep(600)
