import cv2
from src import utils

# Ruta al video
# video_path = "videos_capturados/cameraG9V_20240715_160014.mp4"

# Crear un objeto de captura de video
# cap = cv2.VideoCapture(video_path)

######################################
###### Espejar un video ################
#########################################
# # Verificar si se abrió correctamente el video
# if not cap.isOpened():
#     print("Error al abrir el video")
#     exit()

# # Obtener el ancho y alto del video
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# # Crear un objeto para guardar el video espejado
# fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec para el archivo de salida
# out = cv2.VideoWriter(
#     "videos_capturados/video_espejado.mp4", fourcc, 20.0, (width, height)
# )

# while True:
#     # Leer fotograma por fotograma
#     ret, frame = cap.read()

#     # Si no se pudo leer el fotograma, salir del bucle
#     if not ret:
#         break

#     # Espejar el fotograma
#     mirrored_frame = cv2.flip(frame, 1)

#     # Escribir el fotograma espejado en el archivo de salida
#     out.write(mirrored_frame)

#     # Mostrar el fotograma espejado
#     cv2.imshow("Video Espejado", mirrored_frame)

#     # Salir del bucle si se presiona la tecla 'q'
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# # Liberar el objeto de captura y el objeto de escritura
# cap.release()
# out.release()

# # Cerrar todas las ventanas
# cv2.destroyAllWindows()

# ##################################################
# ###### Ver numeros de frames de un video ################
# #############################################################
# # Verificar si se abrió correctamente el video
# if not cap.isOpened():
#     print("Error al abrir el video")
#     exit()

# # Obtener el número total de fotogramas
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# # Inicializar el índice del fotograma actual
# current_frame_index = 0

# while True:
#     # Establecer la posición del fotograma actual
#     cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)

#     # Leer el fotograma actual
#     ret, frame = cap.read()

#     # Si no se pudo leer el fotograma, salir del bucle
#     if not ret:
#         break

#     # Mostrar el número del fotograma en la ventana
#     cv2.putText(
#         frame,
#         f"Frame: {current_frame_index}/{total_frames - 1}",
#         (10, 30),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         1,
#         (0, 255, 0),
#         2,
#     )

#     # Mostrar el fotograma en una ventana
#     cv2.imshow("Video Frame by Frame", frame)

#     # Esperar a que se presione una tecla
#     key = cv2.waitKey(0) & 0xFF

#     # Si se presiona la tecla 'd', avanzar al siguiente fotograma
#     if key == ord("d"):
#         if current_frame_index < total_frames - 1:
#             current_frame_index += 1

#     # Si se presiona la tecla 'a', retroceder al fotograma anterior
#     elif key == ord("a"):
#         if current_frame_index > 0:
#             current_frame_index -= 1

#     # Si se presiona la tecla 'q', salir del bucle
#     elif key == ord("q"):
#         break

# # Liberar el objeto de captura
# cap.release()

# # Cerrar todas las ventanas
# cv2.destroyAllWindows()

##################################################
###### Recortar entre frame X y Y #####################
#############################################################


def recortar_video(video_path, x, y, output_path):
    # Verificar que y > x
    if y <= x:
        print("El valor de y debe ser mayor que el valor de x")
        return

    # Crear un objeto de captura de video
    cap = cv2.VideoCapture(video_path)

    # Verificar si se abrió correctamente el video
    if not cap.isOpened():
        print("Error al abrir el video")
        return

    # Obtener el ancho, alto y fps del video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Crear un objeto para guardar el video recortado
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec para el archivo de salida
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Establecer la posición del fotograma inicial x
    cap.set(cv2.CAP_PROP_POS_FRAMES, x)

    # Leer y guardar los fotogramas desde x hasta y
    for i in range(x, y + 1):
        ret, frame = cap.read()
        if not ret:
            print(f"No se pudo leer el fotograma {i}")
            break
        out.write(frame)

    # Liberar el objeto de captura y el objeto de escritura
    cap.release()
    out.release()

    print(f"Video recortado guardado en {output_path}")


# Ejemplo de uso
video_path = "videos_capturados/cameraG9V_20240715_160014.mp4"
video_path = utils.seleccionar_video()
x = 900  # Fotograma inicial
y = 1900  # Fotograma final
# output_path = "videos_capturados/cameraG9V_20240715_160014_crop.mp4"
output_path = video_path.replace(".mp4", "_croped.mp4")

recortar_video(video_path, x, y, output_path)
