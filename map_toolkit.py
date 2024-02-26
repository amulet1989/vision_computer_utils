# Importamos matplotlib y numpy
import matplotlib.pyplot as plt
import numpy as np
from src import utils

# Cargamos las dos imágenes desde archivos
imagen1 = plt.imread(utils.seleccionar_imagen())
imagen2 = plt.imread(utils.seleccionar_imagen())

# Creamos una figura con dos ejes
fig, (ax1, ax2) = plt.subplots(1, 2)

# Mostramos las imágenes en los ejes
ax1.imshow(imagen1, aspect="equal")
ax2.imshow(imagen2, aspect="equal")

puntos1 = []
puntos2 = []

# Variable para controlar si se están registrando puntos o no
registrando = False


# Función para manejar los eventos del ratón
def onclick(event):
    global registrando
    if event.button == 1 and registrando:
        # Si se hace clic con el botón izquierdo y se está registrando, se registra el punto
        if event.inaxes == ax1:
            puntos1.append((event.xdata, event.ydata))
            ax1.text(event.xdata, event.ydata, str(len(puntos1)), color="red")
            if len(puntos1) > 1:
                ax1.plot(*zip(*puntos1), "r-")
        elif event.inaxes == ax2:
            puntos2.append((event.xdata, event.ydata))
            ax2.text(event.xdata, event.ydata, str(len(puntos2)), color="red")
            if len(puntos2) > 1:
                ax2.plot(*zip(*puntos2), "r-")
        fig.canvas.draw()


# Función para manejar los eventos del teclado
def onkeypress(event):
    global registrando
    if event.key == "a":
        # Si se presiona 'a', se cambia el estado de registro
        registrando = not registrando
    if event.key == "q":
        # Si se presiona 'q', se guardan los puntos en archivos
        # np.save("puntos1.npy", puntos1)
        # np.save("puntos2.npy", puntos2)
        print(puntos1)
        print(puntos2)
        print("Puntos guardados en archivos")
        plt.close()
        exit()


# # Conectamos los eventos del ratón y del teclado
# plt.connect("button_press_event", onclick)
# plt.connect("key_press_event", onkeypress)

# # Mostramos la figura
# plt.show()


# Función para manejar el zoom con el rol del mouse
def onscroll(event):
    ax = event.inaxes
    if ax is not None:
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location

        if event.button == "up":
            # deal with zoom in
            scale_factor = 1 / 1.5
        elif event.button == "down":
            # deal with zoom out
            scale_factor = 1.5
        else:
            # deal with something that should never happen
            scale_factor = 1

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        ax.figure.canvas.draw()


# Conectamos los eventos del ratón y del teclado
plt.connect("button_press_event", onclick)
plt.connect("key_press_event", onkeypress)
fig.canvas.mpl_connect("scroll_event", onscroll)

# Mostramos la figura
plt.tight_layout()
plt.show()
