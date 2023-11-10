import cv2
import numpy as np
from src import calibration_utils

"""
suposiciones:

    Los puntos de referencia son precisos y están bien definidos tanto en las coordenadas de la cámara como en las coordenadas globales.

    Los puntos de referencia están en el mismo plano (o que la diferencia en Z entre los puntos es despreciable).

    La cámara está mirando directamente a la escena (sin ángulos de inclinación significativos).
"""

# Datos de los puntos de referencia
# Coordenadas latitud-longitud
x_lat = [-73.998613, -73.995694, -73.996613, -73.999565]
y_lon = [40.732174, 40.730717, 40.729618, 40.731081]
origin = (-73.997463, 40.730841)

# Coordenadas de la camara en pixeles
cx = [460, 900, 632, 188]  # [791, 1131, 1026, 686]
cy = [188, 448, 640, 296]  # [184, 409, 573, 352]

# [460, 188],[900, 448],[632, 640],[188, 296],[464, 184]

# Determinar la matriz de transformación
M = calibration_utils.get_calibration_matrix(
    x_lat, y_lon, cx, cy, origin, transform=True
)

# Ejemplo de uso
# Colocar un punto en la escena
x_cam = 159  # 174  # 636  # centro- 926  # Coordenada X en píxeles de la cámara
y_cam = 289  # 300  # 324  # centro- 390  # Coordenada Y en píxeles de la cámara
print(f"Coordenadas camara: X={x_cam}, Y={y_cam}")

# Convertir las coordenadas de la cámara a las globales (metros)
x, y = calibration_utils.mapear_a_coordenadas_globales(x_cam, y_cam, M)
print(f"Coordenadas convertidas: X={x:.6f}, Y={y:.6f}")

# Calcular la distancia entre el punto y el origen global
d = calibration_utils.distance_meter((0, 0), (x, y))
print(f"Distancia de punto al origen: {d:.2f} metros")
