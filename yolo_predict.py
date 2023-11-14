import cv2
from ultralytics import YOLO
from src.utils import seleccionar_video
from src.mapping import bbox_to_planta


model = YOLO("yolov8n.pt")  # train_models/yolov8n_4cam.pt
# model = RTDETR("rtdetr-l.pt")  # rtdetr-l.pt


# Create VideoCapture object
INPUT_VIDEO = seleccionar_video()
# INPUT_VIDEO = "rtsp://admin:2Mini001.@192.168.88.71"

plano_planta = cv2.imread(
    "Track_pilar/planta_pilar_crop.jpg"
)  # Cargar la imagen del plano de planta

# Read video
cap = cv2.VideoCapture(INPUT_VIDEO)
win_name = "Camera Preview"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

classes = 0
results = model.track(
    source=INPUT_VIDEO, stream=True, save=False, conf=0.7, imgsz=704, classes=classes
)  # generator of Results objects

for r in results:
    boxes = r.boxes  # Boxes object for bbox outputs

    image = r.orig_img.copy()
    if boxes.cls.numel() > 0:
        classe = boxes.cls.tolist()
        label = r.names
        scores = boxes.conf.tolist()  # Confidence scores

        points_to_plot = []  # Almacenar los puntos mapeados

        # Draw BBoxes on the image
        # for box, label, score in zip(boxes, labels, scores):
        for i, box in enumerate(boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)  # box
            color = (0, 255, 0)  # Green color
            thickness = 2

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
                box, cam_id="ENTRADA 1_ENTRADA_main"
            )  # Función para mapear el punto a las coordenadas en el plano de planta

            # Comprobar si el punto mapeado está dentro de los límites de la imagen del plano de planta
            for point in mapped_point:
                x, y = point
                if 0 <= x < plano_planta.shape[1] and 0 <= y < plano_planta.shape[0]:
                    points_to_plot.append(point)

        # Dibujar los puntos en la imagen del plano de planta
        for point, b in zip(points_to_plot, bb):
            print("point", point, b)
            cv2.circle(
                plano_planta, point, 5, (0, 0, 255), -1
            )  # Dibujar un círculo rojo en la posición mapeada
            cv2.circle(
                image, b, 5, (0, 0, 255), -1
            )  # Dibujar un círculo rojo en la posición mapeada) in points_to_plot:
            print("point", point, b)

    cv2.imshow(win_name, image)

    escala = 0.75  # Puedes ajustar este valor según tus necesidades
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
