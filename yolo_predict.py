import cv2
from ultralytics import YOLO
from src.utils import seleccionar_video
from src.mapping import bbox_to_planta

# import matplotlib.pyplot as plt
import numpy as np


def map_number_to_color(number):
    np.random.seed(int(number))

    # Generar un color aleatorio único
    color = np.random.randint(0, 256, size=3)

    return tuple(int(x) for x in color)


model = YOLO("train_models/yolov8n_4cam.pt")  # train_models/yolov8n_4cam.pt
# model = RTDETR("rtdetr-l.pt")  # rtdetr-l.pt

# Create VideoCapture object
INPUT_VIDEO = seleccionar_video()
# INPUT_VIDEO = "rtsp://admin:2Mini001.@192.168.88.71"

plano_planta = cv2.imread(
    "Track_CF/CF_plano.jpg"
)  # Cargar la imagen del plano de planta -> Track_pilar/planta_pilar_crop.jpg - Track_CF/CF_plano.jpg

# Read video
cap = cv2.VideoCapture(INPUT_VIDEO)
win_name = "Camera Preview"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
# Cambiar el tamaño de la ventana
cv2.resizeWindow(win_name, 704, 576)

classes = 0
results = model.track(
    source=INPUT_VIDEO,
    stream=True,
    save=True,
    conf=0.8,
    # iou=0.8,
    imgsz=704,
    # classes=classes,
)  # generator of Results objects

for r in results:
    boxes = r.boxes  # Boxes object for bbox outputs

    image = r.orig_img.copy()
    if boxes.cls.numel() > 0:
        classe = boxes.cls.tolist()
        label = r.names
        scores = boxes.conf.tolist()  # Confidence scores

        points_to_plot = []  # Almacenar los puntos mapeados
        bb_to_plot = []
        id_number = []

        # Draw BBoxes on the image
        # for box, label, score in zip(boxes, labels, scores):
        for i, box in enumerate(boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)  # box
            color = (0, 255, 0)  # Green color
            thickness = 2
            # print(boxes.id)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

            text = f"{label[int(classe[i])]} ({scores[i]:.2f})"
            print(text)

            cv2.putText(
                image,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                thickness,
            )

            # Mapear el punto en el plano de planta
            mapped_point, bb = bbox_to_planta(
                box,
                cam_id="camera71",  # camera62/camera71/camera52/camera122 "TRACK_1"  # "ENTRADA 1_ENTRADA_main"
            )  # Función para mapear el punto a las coordenadas en el plano de planta

            # Comprobar si el punto mapeado está dentro de los límites de la imagen del plano de planta
            # estos es solo para fines de visualizacion para la funcion que dibuja los puntos
            print(mapped_point)
            x, y = mapped_point[0]
            x1, y1 = bb[0]
            if (
                0 <= x < plano_planta.shape[1]
                and 0 <= y < plano_planta.shape[0]
                and 0 <= x1 < image.shape[1]
                and 0 <= y1 < image.shape[0]
            ):
                if boxes.id is not None:
                    points_to_plot.append([x, y])
                    bb_to_plot.append([x1, y1])
                    id_number.append(boxes.id[i])

            # for point, b in zip(mapped_point, bb):
            #     x, y = point
            #     x1, y1 = b
            #     if (
            #         0 <= x < plano_planta.shape[1]
            #         and 0 <= y < plano_planta.shape[0]
            #         and 0 <= x1 < image.shape[1]
            #         and 0 <= y1 < image.shape[0]
            #     ):
            #         if boxes.id is not None:
            #             points_to_plot.append(point)
            #             bb_to_plot.append(b)
            #             id_number.append(boxes.id[i])
            #             # print("id ", boxes.id[i], "point ", point, "b ", b)

        # Dibujar los puntos en la imagen del plano de planta
        # cont = 0
        for point, b, id_num in zip(points_to_plot, bb_to_plot, id_number):
            # print("point", point, b)
            # if boxes.id is not None:
            color = map_number_to_color(id_num)
            # print(id_num, "->", color)
            # cont += 1
            cv2.circle(
                plano_planta, point, 5, color, -1
            )  # Dibujar un círculo rojo en la posición mapeada -> rojo (0, 0, 255)
            cv2.circle(
                image, b, 5, color, -1
            )  # Dibujar un círculo rojo en la posición mapeada
            # print("point", point, b)

    cv2.imshow(win_name, image)

    escala = 0.5  # Se puede ajustar este valor para achicar la imagen
    plano_planta_show = cv2.resize(plano_planta, None, fx=escala, fy=escala)
    cv2.imshow("Plano de Planta", plano_planta_show)

    # Wait for a key press and check the pressed key
    key = cv2.waitKey(1)  # & 0xFF
    if key == ord("q"):  # Press 'q' to exit
        break
    elif key == ord("n"):  # Press 'n' to show the next image
        continue

# Release VideoCapture and destroy windows
cap.release()
cv2.destroyAllWindows()
