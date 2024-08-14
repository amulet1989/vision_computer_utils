import xml.etree.ElementTree as ET
import cv2

# Parsear el archivo XML
tree = ET.parse("./videos_capturados/Demo_marketing_pilar/gt/annotations.xml")
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
        state = (
            box.find("attribute[@name='state']").text
            if box.find("attribute[@name='state']") is not None
            else None
        )
        obj_id = (
            int(box.find("attribute[@name='ID']").text)
            if box.find("attribute[@name='ID']") is not None
            else None
        )
        boxes.append((frame, xtl, ytl, xbr, ybr, state, obj_id))
    annotations[track_id] = {"label": label, "boxes": boxes}

# Colores para cada clase y estado
colors = {
    "SAM": (255, 255, 0),  # cian para personas sentadas
    "NATURA": (0, 255, 0),  # verde para personas de pie
    "HELLMAN's": (0, 0, 255),  # Rojo para mesas ocupadas
    "table_free": (255, 0, 0),  # Azul para mesas libres
}

# Procesar Video

# Cargar el video
video_path = "./videos_capturados/Demo_marketing_pilar/Videos/video.mp4"
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
                # Elegir color según la etiqueta
                color = (255, 255, 255)  # Blanco por defecto
                if label == "SAM":
                    color = colors["SAM"] if state == "occupied" else colors["SAM"]
                elif label == "NATURA":
                    color = colors["NATURA"] if state == "sitting" else colors["NATURA"]

                # Dibujar el BBox
                cv2.rectangle(
                    frame, (int(xtl), int(ytl)), (int(xbr), int(ybr)), color, 3
                )

                # Dibujar el label
                cv2.putText(
                    frame,
                    f"{label}",
                    (int(xtl), int(ytl) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    color,
                    3,
                )

    # Escribir el frame anotado en el video de salida
    out.write(frame)
    frame_number += 1

# Liberar los recursos
cap.release()
out.release()
cv2.destroyAllWindows()
