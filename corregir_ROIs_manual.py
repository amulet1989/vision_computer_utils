import cv2
import numpy as np
from src import utils
import matplotlib.pyplot as plt
import cv2
import yaml
import os

# Cargar las imágenes


# ####################
# # Usando ORB       #
# ####################

# # Inicializar ORB
# orb = cv2.BRISK_create()  # ORB_create()
# # Detectar los puntos clave y calcular los descriptores
# kp1, des1 = orb.detectAndCompute(imagen1, None)
# kp2, des2 = orb.detectAndCompute(imagen2, None)

# # Crear un objeto BFMatcher con distancia Hamming como medida
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# # Emparejar los descriptores con ORB
# matches = bf.match(des1, des2)

# # Ordenar los emparejamientos en orden de distancia
# matches = sorted(matches, key=lambda x: x.distance)

# # Dibujar los primeros 10 emparejamientos
# resultado = cv2.drawMatches(imagen1, kp1, imagen2, kp2, matches[:5], None, flags=2)
# # Mostrar la imagen
# cv2.imshow("Emparejamientos", resultado)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Cargar las imágenes a comparar
imagen1 = plt.imread(utils.seleccionar_imagen())
imagen2 = plt.imread(utils.seleccionar_imagen())

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
    # if event.key == "p":
    #     # Si se presiona 'p', se cambia el estado de registro de puntos de prueba
    #     prueba = not prueba
    #     print("Registrando pruebas:", prueba)
    # if event.key == "m":
    #     # Si se presiona 'm', se mapean los puntos
    #     M = mapping_opencv(puntos_cam, puntos_planta)
    #     mapping_opencv_prueba(puntos_pruebas, M)
    #     print("Puntos mapeados")
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
    # if event.key == "i":
    #     # Si se presiona 'i', se imprimen los poligonos en consola redondeados a enteros

    #     # Polígonos redondeados a enteros
    #     poligono_planta = np.floor(np.array(puntos_planta)).astype(np.int16)
    #     poligono_cam = np.floor(np.array(puntos_cam)).astype(np.int16)
    #     poligono_pruebas = np.floor(np.array(puntos_pruebas)).astype(np.int16)

    #     # Formatear los polígonos en una sola línea
    #     formato_planta = ";".join(map(str, poligono_planta.flatten()))
    #     formato_cam = ";".join(map(str, poligono_cam.flatten()))
    #     formato_pruebas = ";".join(map(str, poligono_pruebas.flatten()))

    #     # Imprimir los polígonos en consola
    #     print("poligono imagen 1:", str(poligono_planta.tolist()))
    #     print("poligono imagen 2 rojo:", str(poligono_cam.tolist()))
    #     print("poligono_imagen 2 verde:", str(poligono_pruebas.tolist()))

    #     # Guardar la salida en un archivo de texto
    #     with open(image_path.replace(".jpg", ".txt"), "w") as archivo:
    #         archivo.write(f"Poligono imagen 1: {str(poligono_planta.tolist())}\n")
    #         archivo.write(f"{formato_planta}\n")
    #         archivo.write(f"Poligono imagen 2 rojo: {str(poligono_cam.tolist())}\n")
    #         archivo.write(f"{formato_cam}\n")
    #         archivo.write(
    #             f"Poligono imagen 2 verde: {str(poligono_pruebas.tolist())}\n"
    #         )
    #         archivo.write(f"{formato_pruebas}\n")

    #         print(f"Los poligonos han sido guardados en {archivo}")
    # if event.key == "t":
    #     # Si se presiona 't', se lee el archivo de configuración y se mapean los puntos de prueba
    #     cam_id = image_path.split("/")[-1].replace(".jpg", "")
    #     with open(image_path.replace(".jpg", ".yaml"), "r") as archivo_yaml:
    #         diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)
    #         M = np.array(diccionario_cargado[cam_id])
    #         mapping_opencv_prueba(puntos_pruebas, M)
    #         print("Puntos mapeados")
    # if event.key == "c":
    #     # Si se presiona 'c', se carga un polígono desde un archivo txt
    #     if image_path:
    #         # Extraer el nombre del archivo y cargar el archivo de texto
    #         nombre_archivo = image_path[:-4] + ".txt"

    #         if not os.path.exists(nombre_archivo):
    #             print("El archivo de texto no existe.")
    #         else:
    #             poligonos = cargar_poligonos(nombre_archivo)
    #             mostrar_imagen_con_poligonos(poligonos)

    if event.key == "q":
        # Si se presiona 'q', se cierra el programa
        # Se imprimen los puntos de mapeo en la consola redondeados a enteros
        # print("puntos_planta:", np.floor(np.array(puntos_planta)).astype(np.int16))
        # print("puntos_cam:", np.floor(np.array(puntos_cam)).astype(np.int16))
        # print("puntos_pruebas:", np.floor(np.array(puntos_pruebas)).astype(np.int16))
        plt.close()
        # exit()


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

# Convertir los puntos marcados por el usuario a formatos que OpenCV pueda entender
src_pts = np.float32(puntos_planta).reshape(-1, 1, 2)
dst_pts = np.float32(puntos_cam).reshape(-1, 1, 2)

# Calcular la matriz de transformación usando RANSAC
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Aplicar la transformación a la imagen alineada
imagen1_alineada = cv2.warpPerspective(imagen1, M, (imagen2.shape[1], imagen2.shape[0]))

roi_original = np.float32([[[401, 119], [415, 459], [282, 458], [339, 120]]])  # 52
roi_transformada = cv2.perspectiveTransform(roi_original, M)

roi_transformada = roi_transformada.astype(np.int32)
roi_original = roi_original.astype(np.int32)

# Dibujar ROI original en imagen1
imagen1 = cv2.polylines(
    imagen1,
    [roi_original],  # [np.array(vertice)],
    isClosed=True,
    color=(0, 0, 255),
    thickness=2,
)
imagen2 = cv2.polylines(
    imagen2,
    [roi_transformada],  # roi_transformada - roi_original
    isClosed=True,
    color=(0, 0, 255),
    thickness=2,
)

# Dibujar los emparejamientos
# Dibujar líneas que conectan los puntos coincidentes entre las dos imágenes
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.imshow(imagen1)
ax2.imshow(imagen2)

clicked_points_img1 = puntos_planta
clicked_points_img2 = puntos_cam
for i in range(min(len(clicked_points_img1), len(clicked_points_img2))):
    ax1.plot(clicked_points_img1[i][0], clicked_points_img1[i][1], "ro")
    ax2.plot(clicked_points_img2[i][0], clicked_points_img2[i][1], "ro")
    ax1.plot(
        [clicked_points_img1[i][0], clicked_points_img2[i][0]],
        [clicked_points_img1[i][1], clicked_points_img2[i][1]],
        "g-",
    )

plt.show()
