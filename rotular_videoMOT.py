import cv2
import os


# def cargar_labels(labels_path):
#     with open(labels_path, "r") as file:
#         labels = file.read().splitlines()
#     return labels


# def cargar_anotaciones(anotaciones_path):
#     anotaciones = {}
#     with open(anotaciones_path, "r") as file:
#         for line in file:
#             frame_id, track_id, x, y, w, h, _, class_id, _ = line.strip().split(",")
#             frame_id, track_id, class_id = int(frame_id), int(track_id), int(class_id)
#             x, y, w, h = float(x), float(y), float(w), float(h)
#             if frame_id not in anotaciones:
#                 anotaciones[frame_id] = []
#             anotaciones[frame_id].append((track_id, x, y, w, h, class_id))
#     return anotaciones


# def dibujar_anotaciones(frame, anotaciones, labels):
#     for track_id, x, y, w, h, class_id in anotaciones:
#         label = labels[class_id - 1]
#         color = (
#             int((class_id * 37) % 255),
#             int((class_id * 17) % 255),
#             int((class_id * 50) % 255),
#         )
#         cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), color, 2)
#         cv2.putText(
#             frame,
#             f"{label}_{track_id}",
#             (int(x), int(y) - 10),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.5,
#             color,
#             2,
#         )
#     return frame


# def procesar_video(video_path, anotaciones_path, labels, output_path):
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print(f"Error al abrir el video {video_path}")
#         return

#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS)

#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#     anotaciones = cargar_anotaciones(anotaciones_path)
#     frame_id = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         if frame_id in anotaciones:
#             frame = dibujar_anotaciones(frame, anotaciones[frame_id], labels)

#         out.write(frame)
#         frame_id += 1

#     cap.release()
#     out.release()
#     print(f"Video anotado guardado en {output_path}")


# def main(videos_dir, gt_dir):
#     labels_path = os.path.join(gt_dir, "labels.txt")
#     labels = cargar_labels(labels_path)


#     for video_file in os.listdir(videos_dir):
#         if video_file.endswith(".mp4"):
#             video_path = os.path.join(videos_dir, video_file)
#             anotaciones_file = video_file.replace(".mp4", ".txt")
#             anotaciones_path = os.path.join(gt_dir, anotaciones_file)
#             if os.path.exists(anotaciones_path):
#                 output_path = os.path.join(videos_dir, "anotado_" + video_file)
#                 procesar_video(video_path, anotaciones_path, labels, output_path)
#             else:
#                 print(f"Anotaciones para {video_file} no encontradas.")
# Clase para manejar la persistencia de los puntos centrales
class Tracker:
    def __init__(self, max_frames):
        self.points = {}
        self.max_frames = max_frames

    def update(self, frame_id, track_id, center, color):
        if track_id not in self.points:
            self.points[track_id] = []
        self.points[track_id].append((frame_id, center, color))
        # Eliminar puntos antiguos
        self.points[track_id] = [
            (fid, c, col)
            for fid, c, col in self.points[track_id]
            if frame_id - fid <= self.max_frames
        ]

    def get_points(self, frame_id):
        points_to_draw = []
        for track_id in self.points:
            for fid, center, color in self.points[track_id]:
                if frame_id - fid <= self.max_frames:
                    points_to_draw.append((track_id, center, color))
        return points_to_draw


def cargar_labels(labels_path):
    with open(labels_path, "r") as file:
        labels = file.read().splitlines()
    return labels


def cargar_anotaciones(anotaciones_path):
    anotaciones = {}
    with open(anotaciones_path, "r") as file:
        for line in file:
            frame_id, track_id, x, y, w, h, _, class_id, _ = line.strip().split(",")
            frame_id, track_id, class_id = int(frame_id), int(track_id), int(class_id)
            x, y, w, h = float(x), float(y), float(w), float(h)
            if frame_id not in anotaciones:
                anotaciones[frame_id] = []
            anotaciones[frame_id].append((track_id, x, y, w, h, class_id))
    return anotaciones


def dibujar_anotaciones(frame, anotaciones, labels, tracker, frame_id):
    for track_id, x, y, w, h, class_id in anotaciones:
        label = labels[class_id - 1]
        color = (
            int((class_id * 100) % 255),
            int((class_id * 200) % 255),
            int((class_id * 5) % 255),
        )
        cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), color, 1)
        cv2.putText(
            frame,
            f"{label}_{track_id}",
            (int(x), int(y) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )

        center = (int(x + w / 2), int(y + h / 2))
        tracker.update(frame_id, track_id, center, color)

    # Dibujar los puntos de trayectoria
    points_to_draw = tracker.get_points(frame_id)
    for _, center, color in points_to_draw:
        cv2.circle(frame, center, 3, color, -1)

    return frame


def procesar_video(video_path, anotaciones_path, labels, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error al abrir el video {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    anotaciones = cargar_anotaciones(anotaciones_path)
    tracker = Tracker(max_frames=20)
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id in anotaciones:
            frame = dibujar_anotaciones(
                frame, anotaciones[frame_id], labels, tracker, frame_id
            )

        out.write(frame)
        frame_id += 1

    cap.release()
    out.release()
    print(f"Video anotado guardado en {output_path}")


def main(videos_dir, gt_dir):
    labels_path = os.path.join(gt_dir, "labels.txt")
    labels = cargar_labels(labels_path)

    for video_file in os.listdir(videos_dir):
        if video_file.endswith(".mp4"):
            video_path = os.path.join(videos_dir, video_file)
            anotaciones_file = video_file.replace(".mp4", ".txt")
            anotaciones_path = os.path.join(gt_dir, anotaciones_file)
            if os.path.exists(anotaciones_path):
                output_path = os.path.join(videos_dir, "anotado_" + video_file)
                procesar_video(video_path, anotaciones_path, labels, output_path)
            else:
                print(f"Anotaciones para {video_file} no encontradas.")


if __name__ == "__main__":
    videos_dir = "videos_capturados/restaurant_demo/Videos"
    gt_dir = "videos_capturados/restaurant_demo/gt"
    main(videos_dir, gt_dir)
