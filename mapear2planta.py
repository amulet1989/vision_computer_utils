import cv2
import numpy as np
import yaml
from src.utils import seleccionar_imagen
from src.mapping import bbox_to_planta

# Cargar la imagen de vigilancia y el plano de planta
image_path = "Track_CF_9cam/camera71.jpg"  # Track_pilar/TRACK_pozo_frio_resized.jpg
imagen_vigilancia = cv2.imread(image_path)
plano_planta = cv2.imread(
    "Track_CF_9cam/Planta_CF_9cam.jpg"
)  # Track_pilar/planta_planta_Pilar_resized.jpg - Track_CF/CF_plano.jpg

# Puntos de interés manual (deben coincidir en la imagen y en el palno de planta)
puntos_vigilancia = np.float32([[[125, 341], [537, 273], [341, 89], [149, 53]]])
puntos_plano_planta = np.float32([[[140, 456], [88, 516], [196, 556], [376, 560]]])
# Definir puntos a mapear, para validar la transformación.
punto_imagen_vigilancia = [
    [257, 207],
    [33, 111],
    [401, 63],
    [625, 263],
    [541, 343],
]  # [195, 256], [375, 244], [455, 476]

# Hay dos formas de calcular la matriz de transformación:

# Calcular la matriz de transformación (perspectiva)
matriz_transformacion = cv2.getPerspectiveTransform(
    puntos_vigilancia, puntos_plano_planta, solveMethod=0
)  #'method == DECOMP_LU || method == DECOMP_SVD || method == DECOMP_EIG || method == DECOMP_CHOLESKY || method == DECOMP_QR'
print(f"matriz_transformacion {matriz_transformacion}")

# Calcular la matriz de transformación (homografía) con cv2.findHomography
# matriz_transformacion, _ = cv2.findHomography(
#     puntos_vigilancia, puntos_plano_planta, method=1
# )
# 0 - a regular method using all the points, i.e., the least squares method
# RANSAC - RANSAC-based robust method
# LMEDS - Least-Median robust method
# RHO - PROSAC-based robust method
# print(f"matriz_transformacion {matriz_transformacion2}")

# puede usar la matriz de perspectiva o la de homografía
M = matriz_transformacion

# crear un diccionario para guardar la matriz de transformación respectiva a la camara
cam_id = image_path.split("/")[-1].replace(".jpg", "")
cam_ref_point = f"{cam_id}_ref"
camera_config = {cam_id: M.tolist(), cam_ref_point: "center"}

# Guardar la matriz en un archivo YAML
with open(image_path.replace(".jpg", ".yaml"), "w") as archivo_yaml:
    yaml.dump(camera_config, archivo_yaml)

# Luego, se puede cargar la matriz desde el archivo YAML
with open(image_path.replace(".jpg", ".yaml"), "r") as archivo_yaml:
    diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)

# # Cargar la matriz de transformación desde el archivo YAML general
# with open("config/mapping_cfg_cf.yaml", "r") as archivo_yaml:
#     diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)

M = np.array(diccionario_cargado[cam_id])
print(M)

# Aplicar la transformación a la imagen de vigilancia,
# se deforma la imagen para que coincidan los puntos de la imagen en el plano de planta
imagen_vigilancia_mapeada = cv2.warpPerspective(
    imagen_vigilancia,
    M,  # puede usar la matriz de perspectiva o la de homografía
    (plano_planta.shape[1], plano_planta.shape[0]),
)

punto_imagen_vigilancia = np.array([punto_imagen_vigilancia], dtype=np.float32)
# print("Punto-", punto_imagen_vigilancia)

# Aplicar la transformación al punto
punto_plano_planta = cv2.perspectiveTransform(
    punto_imagen_vigilancia,
    M,  # puede usar la matriz de perspectiva o la de homografía
)

# Extrare las coordenadas en el plano de planta en la forma (x, y)
imagen_x_y = [x for x in np.array(punto_imagen_vigilancia[0][:][:], dtype=np.int16)]
plano_x_y = [x for x in np.array(punto_plano_planta[0][:][:], dtype=np.int16)]
print(plano_x_y)

# Imprimir los puntos en la imagen
for i in range(len(imagen_x_y)):
    cv2.circle(imagen_vigilancia, (imagen_x_y[i]), 5, (0, 0, 255), -1)
    cv2.circle(plano_planta, (plano_x_y[i]), 5, (0, 255, 0), -1)
    cv2.circle(imagen_vigilancia_mapeada, (plano_x_y[i]), 5, (0, 0, 255), -1)

# Mostrar las imágenes
escala = 0.40  # Puedes ajustar este valor según tus necesidades
plano_planta = cv2.resize(plano_planta, None, fx=escala, fy=escala)
imagen_vigilancia_mapeada = cv2.resize(
    imagen_vigilancia_mapeada, None, fx=escala, fy=escala
)

cv2.imshow("Imagen de Vigilancia", imagen_vigilancia)
cv2.imshow("Plano de Planta", plano_planta)
cv2.imshow("Imagen Mapeada", imagen_vigilancia_mapeada)

# Esperar a que se presione la tecla 'q'
cv2.waitKey(0)
cv2.destroyAllWindows()
