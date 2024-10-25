import cv2
from src.utils import seleccionar_video

# from src.inferir_and_draw import draw_frame
import os
import numpy as np
import argparse

# roi-LQ52=365;141;440;141;465;600;320;600
# roi-LQ122=350;81;434;81;417;480;282;480
# roi-LQ62=50;304;200;304;325;396;325;590;50;590
# roi-SQ62=375;408;480;290;703;290;703;590;375;590
# roi-SQ71=181;213;571;453;450;576;250;576;64;315

all_vertices = {
    "cam5": [
        [[365, 141], [440, 141], [465, 600], [320, 600]]
    ],  # 365;141;440;141;465;600;320;600
    "cam6": [[[350, 81], [434, 81], [417, 480], [282, 480]]],
    "cam7": [[[181, 213], [571, 453], [450, 576], [250, 576], [64, 315]]],
}


def procesar_video(input_video_path, output_video_path, output_txt_path, cam="cam6"):
    cap = cv2.VideoCapture(input_video_path)

    # Definir el códec y el objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    out = cv2.VideoWriter(
        output_video_path, fourcc, 1.0, (int(cap.get(3)), int(cap.get(4)))
    )

    frame_number = 0  # Inicializa el número de frame
    pred_temporal = ""
    GT_temporal = ""
    TP = 0
    FP = 0
    FN = 0
    TN = 0

    with open(output_txt_path, "w") as txt_file:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image2show = frame.copy()
            image2show = cv2.resize(image2show, (1280, 720))
            # image2show = draw_frame(image2show)
            # vertices = all_vertices[cam]

            # Mostrar el fotograma en una ventana emergente
            # for vertice in vertices:
            #     image2show = cv2.polylines(
            #         image2show,
            #         [np.array(vertice)],
            #         isClosed=True,
            #         color=(0, 0, 255),
            #         thickness=2,
            #     )

            cv2.imshow("Fotograma", image2show)

            # Salvar image2show como un archivo jpg
            cv2.imwrite(f"frame{cam}.jpg", image2show)

            # Ingresar predicción
            print(f"Frame {frame_number}")
            # pred = input(f"Ingresa valor de predicción en el frame {frame_number}: ")
            pred = input(f"Ingresa valor de predicción: ")
            # Ingresar GT
            GT = input(f"Ingresa valor de GT: ")

            # verificar si pred no está vacío
            if pred != "":
                pred_temporal = pred
            else:
                pred = pred_temporal

            # verificar si GT no está vacío
            if GT != "":
                GT_temporal = GT
            else:
                GT = GT_temporal

            print("Pred:", pred, "GT:", GT)
            print("")

            # Actualizar TP, TN, FP, FN
            if pred == GT:
                if pred == "1":
                    TP += 1
                else:
                    TN += 1
            if pred != GT:
                if pred == "1":
                    FP += 1
                else:
                    FN += 1

            # Dibujar un rectángulo negro como fondo para el texto
            # rectangulo_inicio = (20, 20)
            # rectangulo_fin = (300, 100)
            # color_rectangulo = (0, 0, 0)
            # cv2.rectangle(
            #     frame, rectangulo_inicio, rectangulo_fin, color_rectangulo, -1
            # )  # -1 significa rellenar completamente el rectángulo

            # Leyenda
            cv2.putText(
                frame,
                f"Disponible para llamar (ACTIVO): 1",
                (600, 600),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                f"No disponible para llamar (__): 0",
                (600, 650),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            # Dibujar el valor de predicción
            cv2.putText(
                frame,
                f"Pred: {pred}",
                (600, 800),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )  # Amarillo

            # Dibujar el valor de GT
            cv2.putText(
                frame,
                f"GT: {GT}",
                (750, 800),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )  # Amarillo
            cv2.putText(
                frame,
                f"TP:{TP}, FP:{FP}, TN:{TN}, FN:{FN}",
                (570, 850),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )

            # Escribir el frame modificado en el video de salida
            out.write(frame)

            # Registrar el número de frame y la cantidad de personas en el archivo de texto
            txt_file.write(f"{frame_number} {GT} {pred} \n")

            # Incrementar el número de frame
            frame_number += 1

            # Esperar un momento para que se muestre el fotograma y registrar la entrada del teclado
            cv2.waitKey(1)

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # calcular metricas de la matriz de confusión
    total = TP + FP + FN + TN
    accuracy = (TP + TN) / total
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * (precision * recall) / (precision + recall)

    print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1_score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anotar videos")
    parser.add_argument("--cam", type=str, default="cam6", help="numero de camara")
    args = parser.parse_args()

    input_video_path = seleccionar_video()  # Ruta de tu video de entrada

    # Crear la carpeta "output" en la misma ruta del video
    output_folder_path = os.path.dirname(input_video_path)
    output_folder_path = os.path.join(output_folder_path, "output")
    os.makedirs(output_folder_path, exist_ok=True)

    # Crear en dos path dentro de la carpeta "output" a los videos y txt de salida con el mismos nombre pero con los prefijos out
    output_video_path = os.path.join(
        output_folder_path, os.path.basename(input_video_path)
    )
    output_txt_path = os.path.join(
        output_folder_path, os.path.basename(input_video_path)
    )
    output_video_path = output_video_path.replace(".mp4", "_out.mp4")
    output_txt_path = output_txt_path.replace(".mp4", "_out.txt")

    procesar_video(input_video_path, output_video_path, output_txt_path, args.cam)
