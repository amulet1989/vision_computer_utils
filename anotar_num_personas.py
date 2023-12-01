import cv2
from src.utils import seleccionar_video
from src.inferir_and_draw import draw_frame
import os
import numpy as np
import argparse

# roi-LQ122=350;81; 434;81; 417;480; 282;480
# roi-LQ62=50;304;  200;304;  325;396;  325;590;  50;590
# roi-SQ62=375;408; 480;290; 703;290; 703;590; 375;590

all_vertices = {
    "cam52": [[[365, 141], [440, 141], [465, 600], [282, 480]]],
    "cam122": [[[350, 81], [434, 81], [417, 480], [282, 480]]],
    "cam62": [
        [[50, 304], [200, 304], [325, 396], [325, 590], [50, 590]],
        [[375, 408], [480, 290], [703, 290], [703, 590], [375, 590]],
    ],
    "cam71": [[[101, 171], [571, 453], [450, 564], [250, 564], [25, 246]]],
}


def procesar_video(input_video_path, output_video_path, output_txt_path, cam="cam52"):
    cap = cv2.VideoCapture(input_video_path)

    # Definir el códec y el objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    out = cv2.VideoWriter(
        output_video_path, fourcc, 5.0, (int(cap.get(3)), int(cap.get(4)))
    )

    frame_number = 0  # Inicializa el número de frame
    temporal = ""

    with open(output_txt_path, "w") as txt_file:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image2show = frame.copy()
            image2show = cv2.resize(image2show, (704, 576))
            image2show = draw_frame(image2show)
            vertices = all_vertices[cam]

            # Mostrar el fotograma en una ventana emergente
            for vertice in vertices:
                image2show = cv2.polylines(
                    image2show,
                    [np.array(vertice)],
                    isClosed=True,
                    color=(0, 0, 255),
                    thickness=2,
                )

            cv2.imshow("Fotograma", image2show)

            # Leer el número de personas en el frame desde el teclado
            num_personas = input(
                f"Ingresa el número de personas en el frame {frame_number}: "
            )

            # verificar si num_personas no está vacío
            if num_personas != "":
                temporal = num_personas
            else:
                num_personas = temporal

            # Dibujar un rectángulo negro como fondo para el texto
            rectangulo_inicio = (20, 20)
            rectangulo_fin = (300, 100)
            color_rectangulo = (0, 0, 0)
            cv2.rectangle(
                frame, rectangulo_inicio, rectangulo_fin, color_rectangulo, -1
            )  # -1 significa rellenar completamente el rectángulo

            # Dibujar el número en la esquina superior izquierda en color amarillo
            cv2.putText(
                frame,
                f"Personas GT: {num_personas}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )  # Amarillo

            # Escribir el frame modificado en el video de salida
            out.write(frame)

            # Registrar el número de frame y la cantidad de personas en el archivo de texto
            txt_file.write(f"{frame_number} {num_personas}\n")

            # Incrementar el número de frame
            frame_number += 1

            # Esperar un momento para que se muestre el fotograma y registrar la entrada del teclado
            cv2.waitKey(1)

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anotar videos")
    parser.add_argument("--cam", type=str, default="cam52", help="numero de camara")
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
