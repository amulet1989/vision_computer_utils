import cv2
import numpy as np


def check_cinta_libre(ref_image, current_image, pts, umbral=15, varThreshold=35):
    """
    ref_image: Imagen de referencia
    current_image: Imagen actual
    pts: Puntos de la ROI (polígono)
    umbral: Umbral de porcentaje de diferencia (por defecto 15%)
    varThreshold: Umbral de detección de cambios en el fondo (por defecto 35) mientras más bajo más sensible a los cambios
    return: diff, diff_thresh, flag, percentage_diff
    flag=True: Área libre de objetos
    flag=False: Área ocupada por un objeto

    """
    # Crear una máscara de la ROI
    mask = np.zeros(ref_image.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts, 255)

    # Aplicar la máscara para extraer la ROI de ambas imágenes
    roi_ref = cv2.bitwise_and(ref_image, ref_image, mask=mask)
    roi_current = cv2.bitwise_and(current_image, current_image, mask=mask)

    #####################################################
    ###### Usar un modleo de substracción de fondo ######
    #####################################################

    # Inicializar el sustractor de fondo
    # MOG2 (Mixture of Gaussians 2)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=1, varThreshold=varThreshold, detectShadows=False
    )

    # Aplicar la sustracción de fondo
    # Alimentar el sustractor con la imagen de referencia para que aprenda el fondo
    bg_subtractor.apply(roi_ref, learningRate=1.0)

    # Procesar la imagen actual para detectar diferencias
    diff = bg_subtractor.apply(roi_current, learningRate=0)

    # Eliminar pequeñas manchas blancas usando una apertura morfológicas (opening)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    diff_thresh = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)

    # Volver a circunscribir la imagen resultante a la ROI
    diff_thresh = cv2.bitwise_and(diff_thresh, diff_thresh, mask=mask)

    ######################################
    ###### Usar diferencia absoluta ######
    ######################################
    # # Convertir a escala de grises
    # roi_ref_gray = cv2.cvtColor(roi_ref, cv2.COLOR_BGR2GRAY)
    # roi_current_gray = cv2.cvtColor(roi_current, cv2.COLOR_BGR2GRAY)

    # # Calcular la diferencia absoluta entre la imagen de referencia y la imagen actual
    # diff = cv2.absdiff(roi_ref_gray, roi_current_gray)

    # Umbralizar la imagen de diferencia para obtener una imagen binaria
    # _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Contar los píxeles en la ROI
    roi_pixel_count = np.count_nonzero(mask)
    print(f"Número de píxeles en la ROI: {roi_pixel_count}")

    # Contar los píxeles blancos (diferencia) en la imagen umbralizada
    non_zero_count = np.count_nonzero(diff_thresh)
    print(f"Número de píxeles diferentes (blancos) en la ROI: {non_zero_count}")

    # Calcular el porcentaje de píxeles diferentes
    percentage_diff = (non_zero_count / roi_pixel_count) * 100

    # Determinar si el área está libre basándose en el porcentaje de diferencia
    if percentage_diff < umbral:  # Umbral del 15%
        flag = True
    else:
        flag = False
    return diff, diff_thresh, flag, percentage_diff


if __name__ == "__main__":

    # Cargar la imagen de referencia (cinta sin productos) y la imagen actual
    ref_image = cv2.imread("./videos_capturados/camera245_640x480_ref.jpg")
    current_image = cv2.imread(
        "./videos_capturados/pruebas_cinta/camera245_704x576_20240731_102519-00011.jpg"  # linea_de_caja_val/camera245_704x576_20240731_102519-00010.jpg
    )  # linea_de_caja_train/camera245_704x576_20240731_204910-00003.jpg / linea_de_caja_train/camera245_704x576_20240731_103532-00001

    # Definir los cuatro puntos de la ROI en ambas imágenes (en este caso, son iguales)
    pts = np.array([[102, 172], [101, 269], [129, 270], [128, 170]], dtype="int32")

    # ROI Grande: [[100, 169], [100, 270], [209, 277], [213, 163]]
    # ROI Chica : [[102, 172], [171, 168], [171, 275], [102, 271]]
    # ROI 20cm: [[102, 172], [101, 269], [129, 270], [128, 170]]

    # Correr la funcion
    diff, diff_thresh, flag, percentage_diff = check_cinta_libre(
        ref_image, current_image, pts, umbral=15, varThreshold=35
    )

    # Dibujar la ROI en ambas imágenes
    cv2.polylines(ref_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.polylines(current_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    print(f"Porcentaje de píxeles diferentes en la ROI: {percentage_diff:.2f}%")
    if flag:
        print("Área libre de objetos")
    else:
        print("Área ocupada por un objeto")

    # Mostrar las imágenes con la ROI dibujada
    cv2.imshow("Imagen de Referencia con ROI", ref_image)
    cv2.imshow("Imagen Actual con ROI", current_image)
    # cv2.imshow("Actual mejorada", roi_current)
    cv2.imshow("Diferencia original", diff)  # diff
    cv2.imshow("Diferencia con opening", diff_thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
