import matplotlib.pyplot as plt
import numpy as np
import cv2
import yaml
import tkinter as tk
from tkinter import filedialog
import os

# Instrucciones:

# a -> cambiar el estado de registro
# p -> cambiar el estado de registro de puntos de prueba
# m -> mapear los puntos
# b -> borrar los puntos y los poligonos en el ax2
# v -> borrar los puntos y los spoliogonos en el ax1
# i -> imprimir los poligonos en consola
# t -> obtener M del archivo yaml de configuración y mapear puntos de prueba
# c -> cargar poligono del archivo txt
# q -> salir del programa


###############################
# Funcion para cargar imagenes
###############################
def cargar_imagen(especificacion):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title=f"Seleccionar una imagen de {especificacion}",
        filetypes=[("Archivos de imagen", ["*.jpg", "*.jpeg"])],
    )

    if file_path:
        return file_path
    else:
        return None


# Cargamos las dos imágenes desde los archivos
plano_path = cargar_imagen("plano")
imagen1 = plt.imread(plano_path)

image_path = cargar_imagen("camara")
imagen2 = plt.imread(image_path)


#####################################
# Funciones para mapping con opencv #
#####################################
def mapping_opencv(puntos_cam, puntos_plano_planta):
    # Convertir los puntos a numpy array
    puntos_de_cam = np.float32([puntos_cam])
    puntos_de_planta = np.float32([puntos_plano_planta])

    # Calcular la matriz de transformación (perspectiva)
    # M = cv2.getPerspectiveTransform(
    #     puntos_de_cam, puntos_de_planta, solveMethod=0
    # )  #'method == DECOMP_LU || method == DECOMP_SVD || method == DECOMP_EIG || method == DECOMP_CHOLESKY || method == DECOMP_QR'

    M, mask = cv2.findHomography(puntos_de_cam, puntos_de_planta, cv2.RANSAC, 5.0)

    print(f"matriz_transformacion {M}")

    # crear un diccionario para guardar la matriz de transformación respectiva a la camara
    cam_id = image_path.split("/")[-1].replace(".jpg", "")
    cam_ref_point = f"{cam_id}_ref"
    camera_config = {cam_id: M.tolist(), cam_ref_point: "center"}

    # Guardar la matriz en un archivo YAML
    with open(image_path.replace(".jpg", ".yaml"), "w") as archivo_yaml:
        yaml.dump(camera_config, archivo_yaml)
    return M


def mapping_opencv_prueba(puntos_prueba, M):
    puntos_cam_prueba = np.array([puntos_prueba], dtype=np.float32)
    # print("Punto-", punto_imagen_vigilancia)

    # Aplicar la transformación al punto
    punto_plano_planta = cv2.perspectiveTransform(
        puntos_cam_prueba,
        M,  # puede usar la matriz de perspectiva o la de homografía
    )

    # Extrare las coordenadas en el plano de planta en la forma (x, y)
    plano_x_y = [x for x in np.array(punto_plano_planta[0][:][:], dtype=np.int16)]
    print("Puntos del plano:", np.floor(np.array(plano_x_y)).astype(np.int16))
    print("Puntos de la camara:", np.floor(np.array(puntos_prueba)).astype(np.int16))
    for i, punto in enumerate(plano_x_y, start=1):
        ax1.text(punto[0], punto[1], str(i), color="green")
    ax1.plot(*zip(*plano_x_y), "g-")
    fig.canvas.draw()


#######################################
# Funciones para visualizar poligonos #
#######################################
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


def mostrar_imagen_con_poligonos(poligonos):
    # plt.imshow(imagen)

    for i, poligono in enumerate(poligonos, start=1):
        if poligono:
            x = poligono[0::2]
            y = poligono[1::2]
            ax2.plot(x + [x[0]], y + [y[0]], label=f"Polígono {i}")
    fig.canvas.draw()


##############
# Aplicacion #
##############

# Creamos una figura con dos ejes
fig, (ax1, ax2) = plt.subplots(1, 2)

# Mostramos las imágenes en los ejes
ax1.imshow(imagen1, aspect="equal")
ax2.imshow(imagen2, aspect="equal")

# Vectores para almacenar los puntos de mapeo de cada imagen
puntos_planta = []
puntos_cam = []
puntos_pruebas = []

# Variable para controlar si se están registrando puntos o no
registrando = False
prueba = False


##############################################
# Función para manejar los eventos del ratón #
##############################################
def onclick(event):
    global registrando, prueba
    if event.button == 1 and registrando:
        # Si se hace clic con el botón izquierdo y se está registrando, se registra el punto
        if event.inaxes == ax1:
            puntos_planta.append((event.xdata, event.ydata))
            ax1.text(event.xdata, event.ydata, str(len(puntos_planta)), color="red")
            if len(puntos_planta) > 1:
                ax1.plot(*zip(*puntos_planta), "r-")
        elif event.inaxes == ax2 and prueba == False:
            puntos_cam.append((event.xdata, event.ydata))
            ax2.text(event.xdata, event.ydata, str(len(puntos_cam)), color="red")
            if len(puntos_cam) > 1:
                ax2.plot(*zip(*puntos_cam), "r-")
        elif event.inaxes == ax2 and prueba:
            puntos_pruebas.append((event.xdata, event.ydata))
            ax2.text(event.xdata, event.ydata, str(len(puntos_pruebas)), color="green")
            if len(puntos_pruebas) > 1:
                ax2.plot(*zip(*puntos_pruebas), "g-")

    elif event.button == 3 and registrando:
        # Si se hace clic con el botón derecho y se está registrando, elimina el último vértice
        if event.inaxes == ax1 and puntos_planta:
            puntos_planta.pop()
            ax1.clear()
            ax1.imshow(imagen1)
            for i, punto in enumerate(puntos_planta, start=1):
                ax1.text(punto[0], punto[1], str(i), color="red")
            if len(puntos_planta) > 1:
                ax1.plot(*zip(*puntos_planta), "r-")

        elif event.inaxes == ax2:
            if prueba and puntos_pruebas:
                puntos_pruebas.pop()
                ax2.clear()
                ax2.imshow(imagen2)
                for i, punto in enumerate(puntos_pruebas, start=1):
                    ax2.text(punto[0], punto[1], str(i), color="green")
                if len(puntos_pruebas) > 1:
                    ax2.plot(*zip(*puntos_pruebas), "g-")
            elif not prueba and puntos_cam:
                puntos_cam.pop()
                ax2.clear()
                ax2.imshow(imagen2)
                for i, punto in enumerate(puntos_cam, start=1):
                    ax2.text(punto[0], punto[1], str(i), color="red")
                if len(puntos_cam) > 1:
                    ax2.plot(*zip(*puntos_cam), "r-")

    fig.canvas.draw()


###############################################
# Función para manejar los eventos del teclado #
###############################################
def onkeypress(event):
    """
    a -> cambiar el estado de registro
    p -> cambiar el estado de registro de puntos de prueba
    m -> mapear los puntos
    b -> borrar los puntos y los poligonos en el ax2
    v -> borrar los puntos y los spoliogonos en el ax1
    i -> imprimir los poligonos en consola
    t -> obtener M del archivo yaml de configuración y mapear puntos de prueba
    c -> cargar poligono del archivo txt
    q -> salir del programa
    """
    global registrando, prueba, puntos_pruebas, puntos_cam, puntos_planta
    if event.key == "a":
        # Si se presiona 'a', se cambia el estado de registro
        registrando = not registrando
        print("Registrando:", registrando)
    if event.key == "p":
        # Si se presiona 'p', se cambia el estado de registro de puntos de prueba
        prueba = not prueba
        print("Registrando pruebas:", prueba)
    if event.key == "m":
        # Si se presiona 'm', se mapean los puntos
        M = mapping_opencv(puntos_cam, puntos_planta)
        mapping_opencv_prueba(puntos_pruebas, M)
        print("Puntos mapeados")
    if event.key == "b":
        # Si se presiona 'b', se borran los puntos y se limpilan los poligonos
        puntos_cam = []
        puntos_pruebas = []
        ax2.clear()
        ax2.imshow(imagen2, aspect="equal")
        fig.canvas.draw()
        print("Puntos en camara borrados")
    if event.key == "v":
        # Si se presiona 'b', se borran los puntos y se limpilan los poligonos
        puntos_planta = []
        ax1.clear()
        ax1.imshow(imagen1, aspect="equal")
        fig.canvas.draw()
        print("Puntos en planta borrados")
    if event.key == "i":
        # Si se presiona 'i', se imprimen los poligonos en consola redondeados a enteros

        # Polígonos redondeados a enteros
        poligono_planta = np.floor(np.array(puntos_planta)).astype(np.int16)
        poligono_cam = np.floor(np.array(puntos_cam)).astype(np.int16)
        poligono_pruebas = np.floor(np.array(puntos_pruebas)).astype(np.int16)

        # Formatear los polígonos en una sola línea
        formato_planta = ";".join(map(str, poligono_planta.flatten()))
        formato_cam = ";".join(map(str, poligono_cam.flatten()))
        formato_pruebas = ";".join(map(str, poligono_pruebas.flatten()))

        # Imprimir los polígonos en consola
        print("poligono imagen 1:", str(poligono_planta.tolist()))
        print("poligono imagen 2 rojo:", str(poligono_cam.tolist()))
        print("poligono_imagen 2 verde:", str(poligono_pruebas.tolist()))

        # Guardar la salida en un archivo de texto
        with open(image_path.replace(".jpg", ".txt"), "w") as archivo:
            archivo.write(f"Poligono imagen 1: {str(poligono_planta.tolist())}\n")
            archivo.write(f"{formato_planta}\n")
            archivo.write(f"Poligono imagen 2 rojo: {str(poligono_cam.tolist())}\n")
            archivo.write(f"{formato_cam}\n")
            archivo.write(
                f"Poligono imagen 2 verde: {str(poligono_pruebas.tolist())}\n"
            )
            archivo.write(f"{formato_pruebas}\n")

            print(f"Los poligonos han sido guardados en {archivo}")
    if event.key == "t":
        # Si se presiona 't', se lee el archivo de configuración y se mapean los puntos de prueba
        cam_id = image_path.split("/")[-1].replace(".jpg", "")
        with open(image_path.replace(".jpg", ".yaml"), "r") as archivo_yaml:
            diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)
            M = np.array(diccionario_cargado[cam_id])
            mapping_opencv_prueba(puntos_pruebas, M)
            print("Puntos mapeados")
    if event.key == "c":
        # Si se presiona 'c', se carga un polígono desde un archivo txt
        if image_path:
            # Extraer el nombre del archivo y cargar el archivo de texto
            nombre_archivo = image_path[:-4] + ".txt"

            if not os.path.exists(nombre_archivo):
                print("El archivo de texto no existe.")
            else:
                poligonos = cargar_poligonos(nombre_archivo)
                mostrar_imagen_con_poligonos(poligonos)

    if event.key == "q":
        # Si se presiona 'q', se cierra el programa
        # Se imprimen los puntos de mapeo en la consola redondeados a enteros
        # print("puntos_planta:", np.floor(np.array(puntos_planta)).astype(np.int16))
        # print("puntos_cam:", np.floor(np.array(puntos_cam)).astype(np.int16))
        # print("puntos_pruebas:", np.floor(np.array(puntos_pruebas)).astype(np.int16))
        plt.close()
        exit()


#####################################################
# Función para manejar el zoom con el rol del mouse #
#####################################################
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
