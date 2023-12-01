import cv2
from ultralytics import YOLO

# import matplotlib.pyplot as plt
import numpy as np


def map_number_to_color(number):
    np.random.seed(int(number))

    # Generar un color aleatorio único
    color = np.random.randint(0, 256, size=3)

    return tuple(int(x) for x in color)


# Cargar modelo YOLO
model = YOLO("trained_models/yolov8m_4cam.pt")  # train_models/yolov8n_4cam.pt


def draw_frame(frame):
    results = model(frame)
    # print(results)
    for r in results:
        boxes = r.boxes  # Boxes object for bbox outputs

        image = r.orig_img.copy()
        if boxes.cls.numel() > 0:
            classe = boxes.cls.tolist()
            label = r.names
            scores = boxes.conf.tolist()  # Confidence scores

            # Draw BBoxes on the image
            # for box, label, score in zip(boxes, labels, scores):
            for i, box in enumerate(boxes.xyxy):
                # print(boxes)
                # Por alguna razón algunas detecciones dan ID None, en ese caso se salta la impresion
                # if boxes.id == None:
                #    continue

                # Dibujar el rectángulo y el texto
                x1, y1, x2, y2 = map(int, box)  # box
                point = np.floor(np.array([np.floor((x1 + x2) / 2), y2])).astype(
                    np.int16
                )
                # print(point)
                cv2.circle(image, point, 5, (0, 0, 255), -1)
                # Asignar un color por ID
                color = (0, 255, 0)  # Green color
                thickness = 2
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
                # text = f"{label[int(classe[i])]} ({scores[i]:.2f})"
                # print(text)

    return image
