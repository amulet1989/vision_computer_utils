import cv2
import numpy as np
from src import utils
import pickle
from sys import argv
import argparse


def train_bg_subtractor(image_files, mask):

    # Inicializar el sustractor de fondo
    # bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    #     history=120, varThreshold=35, detectShadows=True
    # )
    accumulated_image = cv2.imread(image_files[0]).astype(np.float32)
    # Entrenar el modelo de fondo con múltiples imágenes de referencia
    for image_file in image_files:
        ref_image = cv2.imread(image_file)
        # Aplicar la máscara para extraer la ROI de ambas imágenes
        # roi_ref = cv2.bitwise_and(ref_image, ref_image, mask=mask)
        accumulated_image = cv2.add(accumulated_image, ref_image.astype(np.float32))
        # bg_subtractor.apply(roi_ref, learningRate=1.0)

    # Dividir por el número de imágenes para obtener la imagen promedio
    average_image = accumulated_image / len(image_files)

    # Convertir de nuevo a formato de imagen (uint8)
    average_image = np.clip(average_image, 0, 255).astype(np.uint8)
    average_image = cv2.bitwise_and(average_image, average_image, mask=mask)

    # # Guardar o mostrar la imagen promedio
    cv2.imwrite("average_image_caja5.jpg", average_image)
    # cv2.imshow("Imagen Promedio", average_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return average_image


def aplicar_clahe(image, clipLimit=2.0, tileGridSize=(8, 8)):
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l_channel, a, b = cv2.split(lab_image)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    l_channel_clahe = clahe.apply(l_channel)
    lab_image_clahe = cv2.merge((l_channel_clahe, a, b))
    return cv2.cvtColor(lab_image_clahe, cv2.COLOR_Lab2BGR)


def check_cinta_libre(
    ref_image, current_image, pts, umbral=15, varThreshold=35, metodo=1
):
    """
    ref_image: Imagen de referencia
    current_image: Imagen actual
    pts: Puntos de la ROI (polígono)
    umbral: Umbral de porcentaje de diferencia (por defecto 15%)
    varThreshold: Umbral de detección de cambios en el fondo (por defecto 35) mientras más bajo más sensible a los cambios
    metodo: 0: Diferencia absoluta, 1: Modelo de fondo MOG2
    return: diff, diff_thresh, flag, percentage_diff
    flag=True: Área libre de objetos
    flag=False: Área ocupada por un objeto

    """
    # Crear una máscara de la ROI
    mask = np.zeros((480, 640), dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts, 255)

    # Aplicar la máscara para extraer la ROI de ambas imágenes
    roi_ref = cv2.bitwise_and(ref_image, ref_image, mask=mask)
    roi_current = cv2.bitwise_and(current_image, current_image, mask=mask)
    # roi_current_o = roi_current.copy()

    # Modelo prentrenado
    # directory_path = "./videos_capturados/Image_ref"
    # image_files = utils.get_image_paths(
    #     directory_path
    # )  # Lista de imágenes de referencia

    # # Entrenar el modelo de fondo con imágenes de referencia
    # imag_prom = train_bg_subtractor(image_files, mask)
    # imag_prom = cv2.imread("average_image.jpg")

    if metodo == 1:
        #####################################################
        ###### Usar un modelo de sustracción de fondo ######
        #####################################################
        # Mejorar contraste con CLAHE
        # roi_ref = aplicar_clahe(roi_ref)
        # roi_current = aplicar_clahe(roi_current)
        ##########################################

        # Inicializar el sustractor de fondo
        # MOG2 (Mixture of Gaussians 2)
        bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=1, varThreshold=varThreshold, detectShadows=True
        )
        # bg_subtractor = train_bg_subtractor(bg_subtractor, image_files, mask)

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
        # diff_thresh = cv2.bitwise_and(diff, diff, mask=mask)
        # ########################################################
    else:
        ######################################
        ###### Usar diferencia absoluta ######
        ######################################

        # Mejorar contraste con CLAHE
        # roi_ref = aplicar_clahe(roi_ref)
        # roi_current = aplicar_clahe(roi_current)
        ##########################################

        # Convertir a escala de grises
        roi_ref_gray = cv2.cvtColor(roi_ref, cv2.COLOR_BGR2GRAY)
        roi_current_gray = cv2.cvtColor(roi_current, cv2.COLOR_BGR2GRAY)

        # Calcular la diferencia absoluta entre la imagen de referencia y la imagen actual
        diff = cv2.absdiff(roi_ref_gray, roi_current_gray)

        # Umbralizar la imagen de diferencia para obtener una imagen binaria
        _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        ####################################

    # Contar los píxeles en la ROI
    roi_pixel_count = np.count_nonzero(mask)
    print(f"Número de píxeles en la ROI: {roi_pixel_count}")

    # Contar los píxeles blancos (diferencia) en la imagen umbralizada
    # non_zero_count = np.count_nonzero(diff_thresh)
    non_zero_count = np.sum(diff_thresh == 255)
    print(f"Número de píxeles diferentes (blancos) en la ROI: {non_zero_count}")

    # Calcular el porcentaje de píxeles diferentes
    percentage_diff = (non_zero_count / roi_pixel_count) * 100

    # Determinar si el área está libre basándose en el porcentaje de diferencia
    flag = (
        percentage_diff < umbral
    )  # Área libre si el porcentaje de diferencia es menor que el umbral

    return diff, diff_thresh, flag, percentage_diff


### Con imágenes ###
if __name__ == "__main__":

    # Añadir parser para las variables umbral=15, varThreshold=25
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--umbral", type=float, default=15.0, help="Umbral de porcentaje de diferencia"
    )
    parser.add_argument(
        "--varThreshold",
        type=int,
        default=25,
        help="Umbral de detección de cambios en el fondo",
    )
    parser.add_argument(
        "--metodo",
        type=int,
        default=1,
        help="0: Diferencia absoluta, 1: Modelo de fondo MOG2",
    )
    parser.add_argument(
        "--source", type=str, default="imagen", help="Ruta de la imagen actual"
    )
    args = parser.parse_args()

    # Cargar la imagen de referencia (cinta sin productos) y la imagen actual
    ref_image = cv2.imread("./videos_capturados/camera245_640x480_ref.jpg")
    average_image = cv2.imread("average_image_caja5.jpg")
    # Definir los cuatro puntos de la ROI en ambas imágenes (en este caso, son iguales)
    pts = np.array([[102, 172], [101, 269], [129, 270], [128, 170]], dtype="int32")

    # ROI Grande: [[100, 169], [100, 270], [209, 277], [213, 163]]
    # ROI Chica : [[102, 172], [171, 168], [171, 275], [102, 271]]
    # ROI 20cm: [[102, 172], [101, 269], [129, 270], [128, 170]]

    if args.source == "imagen":
        current_image = cv2.imread(utils.seleccionar_imagen())
        # Correr la funcion
        diff, diff_thresh, flag, percentage_diff = check_cinta_libre(
            average_image,
            current_image,
            pts,
            umbral=args.umbral,
            varThreshold=args.varThreshold,
            metodo=args.metodo,
        )

        # Dibujar la ROI en ambas imágenes
        cv2.polylines(ref_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.polylines(
            current_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2
        )

        print(f"Porcentaje de píxeles diferentes en la ROI: {percentage_diff:.2f}%")
        if flag:
            print("Área libre de objetos")
        else:
            print("Área ocupada por un objeto")

        # Mostrar las imágenes con la ROI dibujada
        cv2.imshow("Imagen de Referencia con ROI", ref_image)
        cv2.imshow("Imagen Actual con ROI", current_image)
        cv2.imshow("Diferencia original", diff)  # diff
        cv2.imshow("Diferencia con opening", diff_thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        video_path = utils.seleccionar_video()
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Procesar el frame actual
            diff, diff_thresh, flag, percentage_diff = check_cinta_libre(
                average_image,
                frame,
                pts,
                umbral=args.umbral,
                varThreshold=args.varThreshold,
                metodo=args.metodo,
            )

            # Dibujar la ROI en el frame actual
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

            print(f"Porcentaje de píxeles diferentes en la ROI: {percentage_diff:.2f}%")
            if flag:
                print("Área libre de objetos")
            else:
                print("Área ocupada por un objeto")

            # Mostrar el frame con la ROI dibujada
            cv2.imshow("Frame", frame)
            cv2.imshow("Diferencia con opening", diff_thresh)
            cv2.imshow("Average", average_image)

            # Esperar una tecla para pasar al siguiente frame
            key = cv2.waitKey(0) & 0xFF
            if key == ord("q"):  # Presionar 'q' para salir
                break
        cap.release()
        cv2.destroyAllWindows()
