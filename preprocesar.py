from src import utils
import cv2
import os
import numpy as np

#### Resize todas las imagenes en un directorio ####
# images_path = utils.seleccionar_directorio()
# utils.resize_images_in_directory(images_path, width=640, height=480)
# print("se preprocesaron las imagenes")
#######################################################################

#### Resize una imagen ####
# image_path = utils.seleccionar_imagen()
# utils.resize_image(image_path, width=704, height=576)
# utils.resize_image(image_path, escalar=True, escala=0.5)
################################################################

#### Sacar un frame de un video y hacerle resize ####
# video_path = utils.seleccionar_video()
# # obtener una imagen de un video
# image_frame = utils.get_frame_from_video(
#     video_path,
#     5,
# )  # 1280,720 - 640,480
# # guardar la imagen en la misma carpeta del video
# cv2.imwrite(f"{video_path}_640x480.jpg", image_frame)
##########################################

### hacer resize a aun video ####
# utils.resize_video(utils.seleccionar_video(), width=704, height=576, fps=20.0)
##############################

#### Convertir un video en imagenes ####
# video_path = utils.seleccionar_video()
# # obtener directorio base del video
# base_path = os.path.dirname(video_path)
# utils.video_to_frames(video_path, os.path.join(base_path, "frames_video"))
##########################################

#### Obtener imagen de referencia ####
pts = np.array([[113, 157], [104, 260], [134, 262], [139, 155]], dtype="int32")
# Caja5 [[102, 172], [101, 269], [129, 270], [128, 170]]
# Caja6 [[104, 184], [101, 275], [130, 277], [129, 182]]
# Caja7 [[113, 157], [104, 260], [134, 262], [139, 155]]
mask = np.zeros((480, 640), dtype=np.uint8)
cv2.fillConvexPoly(mask, pts, 255)
directory_path = utils.seleccionar_directorio()  # "./videos_capturados/Image_ref"
imag_prom = utils.get_im_avg(
    directory_path, mask, name="image_ref_caja7"
)  # Obtener imagen promedio
########################################
