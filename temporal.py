import matplotlib.pyplot as plt
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
import os


# Función para cargar la imagen
def cargar_imagen():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[("Archivos de imagen", ["*.jpg", "*.jpeg"])],
    )
    return file_path if file_path else None


# Cargamos la imagen
image_path = cargar_imagen()
imagen = plt.imread(image_path)

# Inicializar variables
poligonos = []
poligono_actual = []
modo_correcion = False
punto_seleccionado = None

# Crear figura y ejes
fig, ax = plt.subplots()
ax.imshow(imagen, aspect="equal")


# Función para manejar clics del mouse
def onclick(event):
    global poligono_actual, modo_correcion, punto_seleccionado

    if event.button == 1 and not modo_correcion:
        # Verificar si se cierra el polígono
        if poligono_actual:
            dist = np.linalg.norm(
                np.array(poligono_actual[0]) - np.array([event.xdata, event.ydata])
            )
            if dist < 5:  # Cerrar el polígono si está cerca del primer punto
                poligono_actual.append(poligono_actual[0])  # Cerrar el polígono
                poligonos.append(poligono_actual)
                ax.plot(*zip(*poligono_actual), "r-")
                poligono_actual = []
                fig.canvas.draw()
                return

        # Añadir puntos al polígono actual
        poligono_actual.append([event.xdata, event.ydata])
        ax.plot(event.xdata, event.ydata, "ro")
        if len(poligono_actual) > 1:
            ax.plot(*zip(*poligono_actual), "r-")
        fig.canvas.draw()

    elif event.button == 1 and modo_correcion and punto_seleccionado is not None:
        # Mover punto seleccionado en modo corrección
        poligono, punto = punto_seleccionado
        poligonos[poligono][punto] = [event.xdata, event.ydata]

        # Si es el primer punto en un polígono cerrado, mover también el último punto
        if punto == 0 and len(poligonos[poligono]) > 1:
            poligonos[poligono][-1] = [event.xdata, event.ydata]

        actualizar_imagen()
        fig.canvas.draw()
        punto_seleccionado = None


# Función para actualizar la imagen
def actualizar_imagen():
    ax.clear()
    ax.imshow(imagen, aspect="equal")
    for poligono in poligonos:
        ax.plot(*zip(*poligono), "r-")
        for punto in poligono:
            ax.plot(punto[0], punto[1], "ro")


# Función para manejar teclas
def onkeypress(event):
    global poligono_actual, poligonos, modo_correcion, punto_seleccionado

    if event.key == "i":
        # Imprimir y guardar polígonos en un archivo de texto
        with open(image_path.replace(".jpg", ".txt"), "w") as archivo:
            for i, poligono in enumerate(poligonos, start=1):
                poligono_list = np.floor(poligono).astype(int).tolist()
                formato = ";".join(
                    map(str, np.floor(poligono).astype(int).flatten().tolist())
                )
                archivo.write(f"Poligono {i}: {str(poligono_list)}\n")
                archivo.write(f"{formato}\n")
        print("Polígonos guardados en archivo.")

    elif event.key == "n":
        # Guardar el polígono actual y empezar uno nuevo
        if poligono_actual:
            poligonos.append(poligono_actual)
            poligono_actual = []
            actualizar_imagen()
            fig.canvas.draw()

    elif event.key == "r":
        # Entrar en modo corrección para mover vértices
        modo_correcion = not modo_correcion
        print(
            "Modo corrección activado"
            if modo_correcion
            else "Modo corrección desactivado"
        )

    elif event.key == "q":
        plt.close()
        exit()


# Función para manejar movimiento del mouse
def onmotion(event):
    global punto_seleccionado, modo_correcion

    if modo_correcion and event.inaxes == ax:
        # Seleccionar punto más cercano al cursor en modo corrección
        for i, poligono in enumerate(poligonos):
            for j, punto in enumerate(poligono):
                if np.linalg.norm([event.xdata - punto[0], event.ydata - punto[1]]) < 5:
                    print("Punto seleccionado", i, j)
                    punto_seleccionado = (i, j)
                    break


#####################################################
# Función para manejar el zoom con el scroll del mouse
#####################################################
def onscroll(event):
    if event.inaxes == ax:
        scale_factor = 1.1 if event.button == "up" else 0.9
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim([xlim[0] * scale_factor, xlim[1] * scale_factor])
        ax.set_ylim([ylim[0] * scale_factor, ylim[1] * scale_factor])
        fig.canvas.draw_idle()


# Conectar eventos
fig.canvas.mpl_connect("button_press_event", onclick)
fig.canvas.mpl_connect("key_press_event", onkeypress)
fig.canvas.mpl_connect("motion_notify_event", onmotion)
fig.canvas.mpl_connect("scroll_event", onscroll)

plt.show()
