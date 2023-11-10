import tkinter as tk
from tkinter import filedialog
import cv2
import os


def seleccionar_video():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[
            (
                "Archivos de video",
                "*.mp4",
            )
        ],
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
def resize_image(image_path, width=704, height=576):
    image = cv2.imread(image_path)
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
