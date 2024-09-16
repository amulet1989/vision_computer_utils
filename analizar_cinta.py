import cv2
import numpy as np
from ultralytics import YOLO

# Necesario solo para hacer pruebas las imagenes y videos de prueba
from src import utils
import argparse

# Cargar modelo YOLOv8m
model = YOLO("trained_models/producto_cinta_yolov8seg_v3.pt")  # path al modelo.pt


# Función para obtener las máscara binaria usando modelo YOLOv8 device -> ("cuda:0" / "cpu")
def model_infer(image, model=model, conf=0.35, classes=0, device="cpu"):
    # Ejecutar inferencia en la imagen usando el modelo
    results = model(
        source=image,
        device=device,
        save=False,
        conf=conf,
        classes=classes,
        retina_masks=True,
        verbose=False,
    )

    # Obtener las máscaras de los objetos detectados
    masks = results[0].masks

    # Crear una máscara binaria vacía
    binary_mask = np.zeros(
        image.shape[:2], dtype=np.uint8
    )  # Tamaño de la imagen (alto, ancho)

    if masks is None:
        # Si no hay máscaras, devolver una imagen negra con las mismas dimensiones
        return binary_mask

    # Obtener las coordenadas de las máscaras
    mask_array = masks.xy

    # Dibujar las máscaras en la imagen binaria
    for mask in mask_array:
        # print("Mask coordinates:", mask)  # Debug: Imprimir coordenadas de la máscara
        if len(mask) > 0:
            # Convierte cada conjunto de coordenadas en polígonos y rellénalos
            polygon = np.array(mask, dtype=np.int32)  # Asegurarse de que sean enteros
            cv2.fillPoly(binary_mask, [polygon], 255)

    # Retornar la máscara binaria
    return binary_mask


# Función principal para hacer el chequeo de la cinta usando uno d etres metodos disponibles
def check_cinta_libre(
    ref_image, current_image, pts, umbral=15, varThreshold=40, metodo=2, conf=0.35
):
    """
    ref_image: Imagen de referencia
    current_image: Imagen actual
    pts: Puntos de la ROI (polígono)
    umbral: Umbral de porcentaje de diferencia (por defecto 15%)
    varThreshold: Umbral de detección de cambios en el fondo (por defecto MOG2-75, DiffAbs-40) mientras más bajo más sensible a los cambios
    metodo: 0: Diferencia absoluta, 1: Modelo de fondo MOG2, otro valor: Modelo YOLOv8 segmentación
    conf: Umbral de confianza para la detección de objetos (por defecto 0.35) mientras más bajo más sensible
    return: diff, diff_thresh, flag, percentage_diff
    flag=True: Área libre de objetos
    flag=False: Área ocupada por un objeto

    Ejemplo de uso:
    _, _, flag, percentage_diff = check_cinta_libre(ref_image, current_image, pts, umbral=15, varThreshold=40, metodo=2, conf=0.4)

    """
    # Crear una máscara de la ROI
    mask = np.zeros(ref_image.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts, 255)

    # Aplicar la máscara para extraer la ROI de ambas imágenes
    roi_ref = cv2.bitwise_and(ref_image, ref_image, mask=mask)
    roi_current = cv2.bitwise_and(current_image, current_image, mask=mask)

    if metodo == 1:
        #####################################################
        ###### Usar un modelo de sustracción de fondo ######
        #####################################################
        # Mejorar contraste con CLAHE
        # roi_ref = utils.aplicar_clahe(roi_ref)
        # roi_current = utils.aplicar_clahe(roi_current)
        ##########################################

        # Inicializar el sustractor de fondo
        # MOG2 (Mixture of Gaussians 2)
        bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=1, varThreshold=varThreshold, detectShadows=True
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
        #########################################################

    elif metodo == 0:
        ######################################
        ###### Usar diferencia absoluta ######
        ######################################

        # Mejorar contraste con CLAHE
        # roi_ref = utils.aplicar_clahe(roi_ref)
        # roi_current = utils.aplicar_clahe(roi_current)
        ##########################################

        # # Diferencia en escala de grises
        # roi_ref_gray = cv2.cvtColor(roi_ref, cv2.COLOR_BGR2GRAY)
        # roi_current_gray = cv2.cvtColor(roi_current, cv2.COLOR_BGR2GRAY)

        # # Calcular la diferencia absoluta entre la imagen de referencia y la imagen actual
        # diff = cv2.absdiff(roi_ref_gray, roi_current_gray)
        ###############################################

        # Calcular la diferencia absoluta para cada canal RGB
        diff_B = cv2.absdiff(roi_ref[:, :, 0], roi_current[:, :, 0])
        diff_G = cv2.absdiff(roi_ref[:, :, 1], roi_current[:, :, 1])
        diff_R = cv2.absdiff(roi_ref[:, :, 2], roi_current[:, :, 2])

        # Crear una imagen de diferencia tomando el valor máximo de los tres canales en cada píxel
        diff = cv2.max(cv2.max(diff_B, diff_G), diff_R)

        # Umbralizar la imagen de diferencia para obtener una imagen binaria
        _, diff_thresh = cv2.threshold(diff, varThreshold, 255, cv2.THRESH_BINARY)
        #########################################################

    else:
        ################################################
        ###### Usar modelo YOLOv8 de segmentación ######
        ################################################

        # Hacer la inferencia y obtener la máscara
        diff = model_infer(current_image, conf=conf, classes=0)

        # Volver a circunscribir la imagen resultante a la ROI
        diff_thresh = cv2.bitwise_and(diff, diff, mask=mask)
        ################################################

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


### Probar el método con imágenes o con videos ###
if __name__ == "__main__":

    # Añadir parser para las variables umbral=15, varThreshold=25
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--umbral", type=float, default=15.0, help="Umbral de porcentaje de diferencia"
    )
    parser.add_argument(
        "--varThreshold",
        type=int,
        default=40,
        help="Umbral de detección de cambios en el fondo",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Umbral de detección de cambios en el fondo",
    )
    parser.add_argument(
        "--metodo",
        type=int,
        default=0,
        help="0: Diferencia absoluta, 1: Modelo de fondo MOG2",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="imagen",
        help="Procesar una imagen, de lo contrario un video",
    )
    parser.add_argument(
        "--caja", type=int, default=0, help="Nro de caja a procesar de la lista"
    )
    args = parser.parse_args()

    # Cargar la imagen de referencia (cinta sin productos)
    images = ["image_ref_caja5.jpg", "image_ref_caja6.jpg", "image_ref_caja7.jpg"]
    average_image = cv2.imread(images[args.caja])

    # Definir los cuatro puntos de la ROI
    rois = [
        [[102, 172], [101, 269], [129, 270], [128, 170]],
        [[104, 184], [101, 275], [130, 277], [129, 182]],
        [[113, 157], [104, 260], [134, 262], [139, 155]],
    ]
    pts = np.array(rois[args.caja], dtype="int32")
    # Caja5 [[102, 172], [101, 269], [129, 270], [128, 170]]
    # Caja6 [[104, 184], [101, 275], [130, 277], [129, 182]]
    # Caja7 [[113, 157], [104, 260], [134, 262], [139, 155]]

    if args.source == "imagen":
        # Seleccionar imagen actual
        current_image = cv2.imread(utils.seleccionar_imagen())

        #### Correr la funcion check_cinta_libre() ####
        diff, diff_thresh, flag, percentage_diff = check_cinta_libre(
            average_image,
            current_image,
            pts,
            umbral=args.umbral,
            varThreshold=args.varThreshold,
            metodo=args.metodo,
            conf=args.conf,
        )

        # Dibujar la ROI en ambas imágenes
        cv2.polylines(
            average_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2
        )
        cv2.polylines(
            current_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2
        )

        print(f"Porcentaje de píxeles diferentes en la ROI: {percentage_diff:.2f}%")
        if flag:
            print("Área libre de objetos")
        else:
            print("Área ocupada por un objeto")

        # Mostrar las imágenes con la ROI dibujada
        cv2.imshow("Imagen de Referencia con ROI", average_image)
        cv2.imshow("Imagen Actual con ROI", current_image)
        cv2.imshow("Diferencia original", diff)  # diff
        cv2.imshow("Diferencia con opening", diff_thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:  # Si es un video
        # Elegir el video
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
                conf=args.conf,
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
            cv2.imshow("Diferencia original", diff)  # diff
            cv2.imshow("Diferencia con opening", diff_thresh)
            cv2.imshow("Average", average_image)

            # Esperar una tecla para pasar al siguiente frame
            key = cv2.waitKey(0) & 0xFF
            if key == ord("q"):  # Presionar 'q' para salir
                break
        cap.release()
        cv2.destroyAllWindows()
