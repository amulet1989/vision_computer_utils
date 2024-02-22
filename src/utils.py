import tkinter as tk
from tkinter import filedialog
import cv2
import os


def seleccionar_video():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[("Archivos de video", "*.mp4")],
    )

    if file_path:
        return file_path
    else:
        return None


def seleccionar_imagen():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[
            (
                "Archivos de imagen",
                "*.jpg",
            )
        ],
    )

    if file_path:
        return file_path
    else:
        return None


def seleccionar_directorio():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askdirectory(
        title="Seleccionar directorio",
    )

    if file_path:
        return file_path
    else:
        return None


# recibir una imagen y hacerle resize
def resize_image(image_path, width=704, height=576, escalar=False, escala=0.5):
    image = cv2.imread(image_path)
    if escalar:
        resized_image = cv2.resize(image, None, fx=escala, fy=escala)
    else:
        resized_image = cv2.resize(image, (width, height))

    # guardar la imagen con un nuevo nombre
    new_image_name = os.path.splitext(image_path)[0] + "_resized.jpg"
    image_path = new_image_name
    # guardar la imagen
    cv2.imwrite(image_path, resized_image)
    return resized_image


# hacer resize a todas las imagenes de un directorio
def resize_images_in_directory(directory_path, width, height):
    # leer solo los archivos de imagen
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        # verificar si es un archivo de imagen
        if not file_path.endswith(".jpg"):
            continue
        if os.path.isfile(file_path):
            resize_image(file_path, width, height)
    return None


# obtener el frame n de un video y guardarlo como una imagen jpg
def get_frame_from_video(video_path, frame_number, width, height):
    video = cv2.VideoCapture(video_path)
    # obtener el frame n del video
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = video.read()
    # guardar la imagen como un archivo jpg
    # cv2.imwrite(f"frame_{frame_number}.jpg", frame)
    # redimensionar la imagen
    resized_frame = cv2.resize(frame, (width, height))
    return resized_frame


# hacer resize de un video y guardarlo con el sufijo resized
def resize_video(video_path, width, height, fps=20.0):
    cap = cv2.VideoCapture(video_path)

    # Definir el códec y el objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"H264")

    # Crear un objeto VideoWriter para guardar el video redimensionado
    output_path = video_path.replace(
        ".mp4", "_resized.mp4"
    )  # Añade el sufijo "_resized" al nombre del archivo de salida
    out = cv2.VideoWriter(
        output_path, fourcc, fps, (width, height)
    )  # 30 es la velocidad de fotogramas (puedes ajustarla)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Redimensionar el cuadro al tamaño deseado
        frame = cv2.resize(frame, (width, height))

        # Escribir el cuadro redimensionado en el archivo de salida
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
