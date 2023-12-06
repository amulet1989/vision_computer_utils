from src import utils
import cv2

# images_path = utils.seleccionar_directorio()
# utils.resize_images_in_directory(images_path, width=704, height=576)
# print("se preprocesaron las imagenes")

# image_path = utils.seleccionar_imagen()
# utils.resize_image(image_path, width=704, height=576)
# utils.resize_image(image_path, escalar=True, escala=0.5)

# Sacar un frame de un video y hacerle resize
# video_path = utils.seleccionar_video()
# obtener una imagen de un video
# image_frame = utils.get_frame_from_video(video_path, 5, 704, 576)
# guardar la imagen en la misma carpeta del video
# cv2.imwrite(f"{video_path}.jpg", image_frame)

utils.resize_video(utils.seleccionar_video(), width=704, height=576)
