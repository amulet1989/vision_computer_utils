import tkinter as tk
from tkinter import filedialog
import cv2
import os
import numpy as np


def seleccionar_video():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[("Archivos de video", "*.mp4 *.avi")],
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
def get_frame_from_video(video_path, frame_number, width=None, height=None):
    video = cv2.VideoCapture(video_path)
    # obtener el frame n del video
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = video.read()
    # guardar la imagen como un archivo jpg
    # cv2.imwrite(f"frame_{frame_number}.jpg", frame)
    # redimensionar la imagen
    if width and height:
        resized_frame = cv2.resize(frame, (width, height))
    else:
        resized_frame = frame
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


# Obtener todos lo path de imagenes dentro d euna carpeta
def get_image_paths(directory_path):
    image_paths = []
    for file_name in os.listdir(directory_path):
        if not file_name.endswith(".jpg"):
            continue
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            image_paths.append(file_path)
    return image_paths


# Convertir video en frames jpg
def video_to_frames(video_path, output_folder):
    # Obtener nombre del video sin la extensión
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(output_folder, f"{video_name}_{frame_count}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_count += 1
    cap.release()


# Obtener imagen average
def get_im_avg(directory_path, mask=None, name="average_image"):

    image_files = get_image_paths(directory_path)  # Lista de imágenes de referencia

    accumulated_image = cv2.imread(image_files[0]).astype(np.float32)
    # Entrenar el modelo de fondo con múltiples imágenes de referencia
    for image_file in image_files:
        ref_image = cv2.imread(image_file)
        accumulated_image = cv2.add(accumulated_image, ref_image.astype(np.float32))

    # Dividir por el número de imágenes para obtener la imagen promedio
    average_image = accumulated_image / len(image_files)

    # Convertir de nuevo a formato de imagen (uint8)
    average_image = np.clip(average_image, 0, 255).astype(np.uint8)

    if mask is not None:
        average_image = cv2.bitwise_and(average_image, average_image, mask=mask)
        # average_image = cv2.bitwise_and(ref_image, ref_image, mask=mask)

    # # Guardar o mostrar la imagen promedio
    cv2.imwrite(f"{directory_path}/{name}.jpg", average_image)

    return average_image


# def aplicar_clahe(image, clipLimit=2.0, tileGridSize=(8, 8)):
#     lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
#     l_channel, a, b = cv2.split(lab_image)
#     clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
#     l_channel_clahe = clahe.apply(l_channel)
#     lab_image_clahe = cv2.merge((l_channel_clahe, a, b))
#     return cv2.cvtColor(lab_image_clahe, cv2.COLOR_Lab2BGR)
