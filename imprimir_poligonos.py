import matplotlib.pyplot as plt
import os
from tkinter import Tk, filedialog


def cargar_imagen(especificacion):

    root = Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title=f"Seleccionar una imagen de {especificacion}",
        filetypes=[("Archivos de imagen", "*.jpg")],
    )

    if file_path:
        return file_path
    else:
        return None


def cargar_poligonos(nombre_archivo):
    with open(nombre_archivo, "r") as archivo:
        contenido = archivo.readlines()

    poligonos = []

    for linea in contenido:
        if ";" in linea:
            # Si la línea contiene punto y coma, probablemente sea una línea de polígono
            puntos_str = linea.strip()

            if puntos_str:
                puntos = [int(p) for p in puntos_str.split(";")]
                poligonos.append(puntos)

    return poligonos


def mostrar_imagen_con_poligonos(imagen, poligonos):
    plt.imshow(imagen)

    for i, poligono in enumerate(poligonos, start=1):
        if poligono:
            x = poligono[0::2]
            y = poligono[1::2]
            plt.plot(x + [x[0]], y + [y[0]], label=f"Polígono {i}")

    plt.legend()
    plt.title("Imagen con Polígonos")
    plt.show()


# Cargar la imagen
imagen_path = cargar_imagen("especificacion")

if imagen_path:
    # Extraer el nombre del archivo y cargar el archivo de texto
    nombre_archivo = imagen_path[:-4] + ".txt"

    if not os.path.exists(nombre_archivo):
        print("El archivo de texto no existe.")
    else:
        imagen = plt.imread(imagen_path)
        poligonos = cargar_poligonos(nombre_archivo)
        mostrar_imagen_con_poligonos(imagen, poligonos)
