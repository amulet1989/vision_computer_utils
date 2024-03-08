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


# Cargar modelo YOLO
model = YOLO(
    "trained_models/yolov8m_640x480_cf_9cam_v18.pt"
)  # train_models/yolov8n_4cam.pt

# Create VideoCapture object
INPUT_VIDEO = seleccionar_video()
# INPUT_VIDEO = "rtsp://admin:2Mini001.@192.168.88.81/live1"

plano_planta = cv2.imread(
    "Track_CF_9cam/Planta_CF_9cam.jpg"
)  # Cargar la imagen del plano de planta -> Track_pilar/planta_planta_Pilar_resized.jpg - Track_CF/CF_plano.jpg

# Read video
cap = cv2.VideoCapture(INPUT_VIDEO)
win_name = "Camera Preview"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

# Ajustar el tamaño de la ventana de salida del video
cv2.resizeWindow(win_name, 640, 480)

# classes = 0
results = model.track(
    source=INPUT_VIDEO,
    stream=True,
    save=False,
    conf=0.4,
    iou=0.7,
    imgsz=640,  # 640 1280
    # classes=classes,
)  # generator of Results objects

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
            if boxes.id == None:
                continue

            # Dibujar el rectángulo y el texto
            x1, y1, x2, y2 = map(int, box)  # box
            # Asignar un color por ID
            color = map_number_to_color(boxes.id[i])  # (0, 255, 0)  # Green color
            thickness = 2
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
            text = f"{label[int(classe[i])]} ({scores[i]:.2f})"
            # print(text)

            cv2.putText(
                image,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                thickness,
            )

            # Mapear el punto en el plano de planta, acá se debe poner el id correcto de camara relativo al .yaml de configuracion
            # TRACK_ENTRADA/TRACK_SALIDA/TRACK_1-3-4-5-6-7-8/TRACK_Nueva/TRACK_pozo_frio
            # print(box)
            mapped_point, bb = bbox_to_planta(
                box,
                cam_id="camera52",  # camera62/camera71/camera52/camera122 -
            )  # Función para mapear el punto a las coordenadas en el plano de planta

            # Comprobar si el punto mapeado está dentro de los límites de la imagen
            # estos es solo para fines de visualizacion para la funcion que dibuja los puntos
            # print(mapped_point)
            x, y = mapped_point[0]
            x1, y1 = bb[0]
            if (
                0 <= x < plano_planta.shape[1]
                and 0 <= y < plano_planta.shape[0]
                and 0 <= x1 < image.shape[1]
                and 0 <= y1 < image.shape[0]
            ):
                # Dibujar los puntos en las imágenes
                cv2.circle(
                    plano_planta, [x, y], 5, color, -1
                )  # Dibujar un círculo en la posición mapeada -> rojo (0, 0, 255)
                cv2.circle(
                    image, [x1, y1], 5, color, -1
                )  # Dibujar un círculo en la posición mapeada

    cv2.imshow(win_name, image)

    escala = (
        0.75  # Se puede ajustar este valor para achicar o agrandar la imagen del palno
    )
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
