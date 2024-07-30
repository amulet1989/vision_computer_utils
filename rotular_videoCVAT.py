import xml.etree.ElementTree as ET
import cv2

# Parsear el archivo XML
tree = ET.parse("./videos_capturados/restaurant_demo/gt/annotations.xml")
root = tree.getroot()

# Extraer la información del archivo XML
annotations = {}
for track in root.findall("track"):
    label = track.get("label")
    track_id = int(track.get("id"))
    boxes = []
    for box in track.findall("box"):
        frame = int(box.get("frame"))
        xtl = float(box.get("xtl"))
        ytl = float(box.get("ytl"))
        xbr = float(box.get("xbr"))
        ybr = float(box.get("ybr"))
        state = box.find("attribute[@name='state']").text
        obj_id = int(box.find("attribute[@name='ID']").text)
        boxes.append((frame, xtl, ytl, xbr, ybr, state, obj_id))
    annotations[track_id] = {"label": label, "boxes": boxes}

# Colores para cada clase y estado
colors = {
    "person_sitting": (255, 255, 0),  # cian para personas sentadas
    "person_standing": (0, 255, 0),  # verde para personas de pie
    "table_occupied": (0, 0, 255),  # Rojo para mesas ocupadas
    "table_free": (255, 0, 0),  # Azul para mesas libres
}

# Procesar Video


# Cargar el video
video_path = "./videos_capturados/restaurant_demo/Videos/sala_de_estudio_demo.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Definir el códec y crear el objeto VideoWriter
out = cv2.VideoWriter(
    "anotated.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (frame_width, frame_height),
)

# Diccionario para almacenar el tiempo en estado "sitting" para cada persona
sitting_time = {}

# Procesar frame a frame
frame_number = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    for track_id, data in annotations.items():
        label = data["label"]
        for f, xtl, ytl, xbr, ybr, state, obj_id in data["boxes"]:
            if f == frame_number:
                # Elegir color según la etiqueta y el estado
                if label == "table":
                    if state == "occupied":
                        color = colors["table_occupied"]
                    elif state == "free":
                        color = colors["table_free"]
                elif label == "person":
                    if state == "sitting":
                        color = colors["person_sitting"]
                    elif state == "standing":
                        color = colors["person_standing"]
                else:
                    color = (
                        255,
                        255,
                        255,
                    )  # Blanco por defecto para cualquier otro caso

                # Dibujar el BBox
                cv2.rectangle(
                    frame, (int(xtl), int(ytl)), (int(xbr), int(ybr)), color, 3
                )
                # Dibujar el ID y el estado
                cv2.putText(
                    frame,
                    f"ID: {obj_id}",
                    (int(xtl), int(ytl) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    color,
                    3,
                )
                cv2.putText(
                    frame,
                    f"{state}",
                    (int(xtl), int(ytl) - 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    color,
                    2,
                )

                # Calcular y mostrar el tiempo en estado "sitting" para cada persona
                if label == "person" and state == "sitting":
                    if obj_id not in sitting_time:
                        sitting_time[obj_id] = 1 / fps
                    else:
                        sitting_time[obj_id] += 8 / fps
                    cv2.putText(
                        frame,
                        f"{sitting_time[obj_id]:.2f}s",
                        (int(xtl), int(ybr) + 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        color,
                        2,
                    )

    # Escribir el frame anotado en el video de salida
    out.write(frame)
    frame_number += 1

# Liberar los recursos
cap.release()
out.release()
cv2.destroyAllWindows()
