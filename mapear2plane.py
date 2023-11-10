import cv2
import numpy as np
from src import calibration_utils

# [632, 238],[1144, 570],[672, 866],[332, 530]
# [256, 106],[544, 414],[364, 554],[120, 262],

# Datos de los puntos de referencia
# Coordenadas en metros
x_m = [-4, -1.25, -1.25, -4]  # [1.25, -1.25, -0.5, 1.25]
y_m = [0.905, 0.905, -0.905, -0.905]  # [-0.905, -0.905, 0.905, 0.905]
origin = (0, 0)

# Coordenadas de la camara en pixeles
cx = [256, 544, 364, 120]  # [632, 1144, 672, 332]
cy = [106, 414, 554, 262]  # [238, 570, 866, 530]

# Determinar la matriz de transformación
M = calibration_utils.get_calibration_matrix(x_m, y_m, cx, cy, origin, transform=False)

# Ejemplo de uso
# Colocar un punto en la escena
x_cam = 423  # 174  # 636  # centro- 926  # Coordenada X en píxeles de la cámara
y_cam = 455  # 300  # 324  # centro- 390  # Coordenada Y en píxeles de la cámara
print(f"Coordenadas camara: X={x_cam}, Y={y_cam}")

# Convertir las coordenadas de la cámara a las globales (metros)
x, y = calibration_utils.mapear_a_coordenadas_globales(x_cam, y_cam, M)
print(f"Coordenadas convertidas: X={x:.6f}, Y={y:.6f}")

# Calcular la distancia entre el punto y el origen global
d = calibration_utils.distance_meter((0, 0), (x, y))
print(f"Distancia de punto al origen: {d:.2f} metros")
