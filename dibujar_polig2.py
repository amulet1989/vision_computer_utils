import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog

### Lista eventos de tecaldo ###
"""
c -> cargar poligono del archivo txt
n -> cargar poligono nuevo
i -> imprimir los poligonos en consola y crear txt
b -> borrar todos los puntos y los poligonos 
q -> salir del programa
r -> pasar al modo de corrección
    click izquierdo -> mover punto seleccionado
    click derecho -> eliminar punto seleccionado
    pasar sobre un punto intermedio -> crea nuevo vertice
"""


# Función para cargar la imagen
def cargar_imagen():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    file_path = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[("Archivos de imagen", ["*.jpg", "*.jpeg"])],
    )
    return file_path if file_path else None


image_path = cargar_imagen()
imagen = plt.imread(image_path)

# Inicializar variables
poligonos = []
poligono_actual = []
modo_correcion = False
punto_seleccionado = None
umbral_cercania = 5

# Crear figura y ejes
fig, ax = plt.subplots()
ax.imshow(imagen, aspect="equal")
fig.suptitle("Creando polígonos")  # Título inicial


# Función para manejar clics del mouse
def onclick(event):
    global poligono_actual, modo_correcion, punto_seleccionado

    if event.button == 1 and not modo_correcion:
        # Verificar si se cierra el polígono
        if poligono_actual:
            dist = np.linalg.norm(
                np.array(poligono_actual[0]) - np.array([event.xdata, event.ydata])
            )
            if (
                dist < umbral_cercania
            ):  # Cerrar el polígono si está cerca del primer punto
                poligono_actual.append(poligono_actual[0])  # Cerrar el polígono
                poligonos.append(poligono_actual)
                ax.plot(*zip(*poligono_actual), "r-")
                # Dibujar el número del polígono en el primer vértice
                ax.text(
                    poligono_actual[0][0],
                    poligono_actual[0][1],
                    str(len(poligonos)),
                    color="blue",
                    fontsize=12,
                )
                poligono_actual = []
                actualizar_imagen()
                return

        # Añadir puntos al polígono actual
        poligono_actual.append([event.xdata, event.ydata])
        ax.plot(event.xdata, event.ydata, "ro")
        if len(poligono_actual) > 1:
            ax.plot(*zip(*poligono_actual), "r-")
        fig.canvas.draw()

    elif event.button == 3 and not modo_correcion and poligono_actual:
        # Eliminar el último vértice del polígono actual
        poligono_actual.pop()
        actualizar_imagen()

    elif event.button == 1 and modo_correcion and punto_seleccionado is not None:
        # Mover punto seleccionado en modo corrección
        poligono, punto = punto_seleccionado
        poligonos[poligono][punto] = [event.xdata, event.ydata]

        # Si es el primer punto en un polígono cerrado, mover también el último punto
        if punto == 0 and len(poligonos[poligono]) > 1:
            poligonos[poligono][-1] = [event.xdata, event.ydata]

        actualizar_imagen()
        punto_seleccionado = None

    elif event.button == 3 and modo_correcion and punto_seleccionado is not None:
        # Eliminar punto seleccionado en modo corrección con clic derecho
        poligono, punto = punto_seleccionado
        del poligonos[poligono][punto]
        actualizar_imagen()
        punto_seleccionado = None


# Función para actualizar la imagen
def actualizar_imagen():
    ax.clear()
    ax.imshow(imagen, aspect="equal")
    for i, poligono in enumerate(poligonos):
        ax.plot(*zip(*poligono), "r-")
        for punto in poligono:
            ax.plot(punto[0], punto[1], "ro")
        # Dibujar el número del polígono en el primer vértice
        ax.text(poligono[0][0], poligono[0][1], str(i + 1), color="blue", fontsize=18)
        # Añadir puntos sin relleno entre los vértices
        for j in range(len(poligono) - 1):
            mid_point = [
                (poligono[j][0] + poligono[j + 1][0]) / 2,
                (poligono[j][1] + poligono[j + 1][1]) / 2,
            ]
            ax.plot(mid_point[0], mid_point[1], "ro", mfc="none")
    for punto in poligono_actual:
        ax.plot(punto[0], punto[1], "ro")
    if len(poligono_actual) > 1:
        ax.plot(*zip(*poligono_actual), "r-")
    fig.canvas.draw()


# Función para manejar teclas
def onkeypress(event):
    global poligono_actual, poligonos, modo_correcion, punto_seleccionado, imagen, image_path

    if event.key == "i":
        # Imprimir y guardar polígonos en un archivo de texto
        with open(image_path.replace(".jpg", ".txt"), "w") as archivo:
            for i, poligono in enumerate(poligonos, start=1):
                poligono = np.delete(poligono, -1, 0)  # Eliminar el último elemento
                poligono_list = np.floor(poligono).astype(int).tolist()
                formato = ";".join(
                    map(str, np.floor(poligono).astype(int).flatten().tolist())
                )
                archivo.write(f"Poligono {i}: {str(poligono_list)}\n")
                archivo.write(f"{formato}\n")
                print(f"Poligono {i}: {str(poligono_list)}\n")
                print(f"{formato}\n")
        print("Polígonos guardados en archivo.")

    elif event.key == "c":
        # Cargar los polígonos desde el archivo de texto
        file_path = filedialog.askopenfilename(
            title="Seleccionar un archivo de polígonos",
            filetypes=[("Archivos de texto", "*.txt")],
        )
        if file_path:
            poligonos.clear()
            with open(file_path, "r") as archivo:
                for line in archivo:
                    if line.startswith("Poligono"):
                        continue
                    puntos_str = line.strip().split(";")
                    puntos = [
                        [int(puntos_str[i]), int(puntos_str[i + 1])]
                        for i in range(0, len(puntos_str), 2)
                    ]
                    poligonos.append(puntos)
            # Añadir el punto inicial al final para cerrar el polígono
            for poligono in poligonos:
                poligono.append(poligono[0])
            actualizar_imagen()
            fig.canvas.draw()
            print("Polígonos cargados desde el archivo.")

    elif event.key == "n":
        # Guardar el polígono actual y empezar uno nuevo
        if poligono_actual:
            poligonos.append(poligono_actual)
            poligono_actual = []
            actualizar_imagen()

    elif event.key == "r":
        # Entrar en modo corrección para mover vértices
        modo_correcion = not modo_correcion
        # Cambiar el título de la figura según el modo actual
        fig.suptitle("Corrigiendo polígonos" if modo_correcion else "Creando polígonos")
        fig.canvas.draw()
        print(
            "Modo corrección activado"
            if modo_correcion
            else "Modo corrección desactivado"
        )

    elif event.key == "b":
        # Borrar polígonos
        poligonos = []
        poligono_actual = []
        actualizar_imagen()

    elif event.key == "l":
        # Borrar polígonos y cargar una nueva imagen
        poligonos = []
        poligono_actual = []
        image_path = cargar_imagen()
        imagen = plt.imread(image_path)
        actualizar_imagen()

    elif event.key == "h":
        ayuda1 = """
    click izquierdo -> crear nuevo vertice
    click derecho ->  eliminar último vertice
    """
        ayuda2 = """
    click izquierdo -> mover punto seleccionado
    click derecho -> eliminar punto seleccionado
    pasar sobre un punto intermedio -> crea nuevo vertice
    """
        print("Comandos disponibles:")
        print(ayuda1)
        print("c -> cargar poligono del archivo txt")
        print("n -> cargar poligono nuevo")
        print("i -> imprimir los poligonos en consola y crear txt")
        print("b -> borrar todos los puntos y los poligonos")
        print("r -> pasar al modo de corrección")
        print(ayuda2)
        print("l -> cargar una nueva imagen")
        print("q -> salir del programa")

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
                if (
                    np.linalg.norm([event.xdata - punto[0], event.ydata - punto[1]])
                    < umbral_cercania
                ):
                    punto_seleccionado = (i, j)
                    break

        # Verificar si se clicó en un punto sin relleno para añadir un nuevo vértice
        for i, poligono in enumerate(poligonos):
            for j in range(len(poligono) - 1):
                mid_point = [
                    (poligono[j][0] + poligono[j + 1][0]) / 2,
                    (poligono[j][1] + poligono[j + 1][1]) / 2,
                ]
                if (
                    np.linalg.norm(
                        [event.xdata - mid_point[0], event.ydata - mid_point[1]]
                    )
                    < 1
                ):
                    poligonos[i].insert(j + 1, [event.xdata, event.ydata])
                    actualizar_imagen()
                    return


# Función para manejar el zoom con el scroll del mouse
def onscroll(event):
    if event.inaxes == ax:
        scale_factor = 1.1
        if event.button == "up":
            scale_factor = 1 / scale_factor
        ax.set_xlim(
            [
                event.xdata - (event.xdata - ax.get_xlim()[0]) * scale_factor,
                event.xdata + (ax.get_xlim()[1] - event.xdata) * scale_factor,
            ]
        )
        ax.set_ylim(
            [
                event.ydata - (event.ydata - ax.get_ylim()[0]) * scale_factor,
                event.ydata + (ax.get_ylim()[1] - event.ydata) * scale_factor,
            ]
        )
        fig.canvas.draw()


# Conectar eventos a las funciones correspondientes
fig.canvas.mpl_connect("button_press_event", onclick)
fig.canvas.mpl_connect("key_press_event", onkeypress)
fig.canvas.mpl_connect("motion_notify_event", onmotion)
fig.canvas.mpl_connect("scroll_event", onscroll)

plt.show()
