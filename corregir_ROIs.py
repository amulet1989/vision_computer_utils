import cv2
import numpy as np
from src import utils

# Cargar las imágenes a comparar
imagen1 = cv2.imread(utils.seleccionar_imagen())
imagen2 = cv2.imread(utils.seleccionar_imagen())

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

####################
# Usando SIFT      #
####################

# Inicializar SIFT
sift = cv2.SIFT_create()
# Detectar los puntos clave y calcular los descriptores
kp1, des1 = sift.detectAndCompute(imagen1, None)
kp2, des2 = sift.detectAndCompute(imagen2, None)

# Crear un objeto BFMatcher con distancia euclidiana como medida
bf = cv2.BFMatcher()
# Emparejar los descriptores con SIFT
matches = bf.knnMatch(des1, des2, k=2)

# Aplicar el filtro de razón de Lowe
good_matches = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:  # 0.75
        good_matches.append(m)

# Aplicar el filtro de distancia entre puntos clave
max_distance = 30  # Define la distancia máxima permitida
min_distance = 1  # Define la distancia mínima permitida
filtered_matches = []
for match in good_matches:
    pt_original = kp1[match.queryIdx].pt
    pt_movida = kp2[match.trainIdx].pt

    distance = np.sqrt(
        (pt_original[0] - pt_movida[0]) ** 2 + (pt_original[1] - pt_movida[1]) ** 2
    )
    if distance <= max_distance and distance > min_distance:
        filtered_matches.append(match)

# Ordenar los emparejamientos en orden de distancia
good_matches = sorted(filtered_matches, key=lambda x: x.distance)


# Usamos los mejores matches para encontrar la transformación
src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
print(src_pts)
print(dst_pts)

M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
# print(M)

# Aplicamos la transformación a la ROI
roi_original = np.float32([[[401, 119], [415, 459], [282, 458], [339, 120]]])  # 52
# roi_original = np.float32([[[27, 258], [194, 266], [309, 339], [307, 477], [20, 476]]])  # 62
# roi_original = np.float32([[[317, 70], [386, 73], [376, 469], [224, 467]]]) # 122
# roi_original = np.float32([[[168, 164], [540, 355], [433, 478], [199, 475], [34, 261]]])  # 71
# roi_original = np.float32([[[277, 116], [345, 116], [387, 466], [235, 466]]])  # 249
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
    [roi_original],  # roi_transformada - roi_original
    isClosed=True,
    color=(0, 0, 255),
    thickness=2,
)


# Dibujar los emparejamientos
resultado = cv2.drawMatches(
    imagen1,
    kp1,
    imagen2,
    kp2,
    good_matches,
    None,
    flags=2,  # cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
)
print("La ROI ha sido transformada.")

# Aplicar la transformación a una de las imágenes
imagen1_alineada = cv2.warpPerspective(imagen1, M, (imagen2.shape[1], imagen2.shape[0]))

# Mostrar la imagen
cv2.imshow("Emparejamientos", resultado)
cv2.waitKey(0)
cv2.imshow("Imagen 1 Alineada", imagen1_alineada)
cv2.waitKey(0)
cv2.destroyAllWindows()
