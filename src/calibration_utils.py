import math
import cv2
import numpy as np
from typing import Tuple, List


def latlon_to_xy(origin, point):
    """
    Example usage:
    origin = (longitudeOrigin, latitudeOrigin)
    point = (longitudePoint, latitudePoint)
    x, y = latlon_to_xy(origin, point)
    print(f'x: {x}, y: {y}')
    """
    # Convert degrees to radians
    lon1, lat1 = map(math.radians, origin)
    lon2, lat2 = map(math.radians, point)

    # Radius of the Earth in meters (you can use other values if needed)
    radius = 6371000  # Approximate radius of the Earth

    # Calculate the differences in longitude and latitude
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Calculate the distance between the two points using the haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    # Calculate the initial bearing from the origin to the point
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        dlon
    )
    initial_bearing = math.atan2(y, x)

    # Convert initial bearing to radians
    initial_bearing = math.degrees(initial_bearing)

    # Calculate x and y coordinates
    x_offset = distance * math.sin(math.radians(initial_bearing))
    y_offset = distance * math.cos(math.radians(initial_bearing))

    return x_offset, y_offset


# calcular distancia en tre dos puntos
def distance_meter(p1, p2):
    """
    Example usage:
    distance = distance_meter((0, 0), (10, 10))
    print(f'Distance: {distance}')
    """
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def mapear_a_coordenadas_globales(x_y, M):
    # Mapear desde coordenadas de la cámara a coordenadas globales
    # punto_cam = np.array([[x_cam, y_cam, 1]])
    # punto_global = np.dot(M, punto_cam.T)
    # punto_global /= punto_global[2, 0]  # Normalización
    # return punto_global[0, 0], punto_global[1, 0]
    punto_plano_planta = cv2.perspectiveTransform(
        x_y,
        M,  # puede usar la matriz de perspectiva o la de homografía
    )


def get_calibration_matrix(
    x_lat: List,
    y_lon: List,
    cx: List,
    cy: List,
    origin: Tuple = (0, 0),
    transform=False,
):
    """
    Obtener las matriz de transformaci'on de perspectiva
    xlat:List -> Lista de coordenadas de latitud
    ylon:List -> Lista de coordenadas de longitud
    origin:Tuple -> Punto de origen global
    return:Matriz de transformación de perspectiva
    Example usage:
    M = get_calibration_matrix(x_lat, y_lon, origin)
    """

    # Coordenadas latitud-longitud
    x_lat = np.array(x_lat)
    y_lon = np.array(y_lon)

    # origin = (-73.997463, 40.730841)

    # Coordenadas globales
    if transform:
        gx = []
        gy = []
        for i, j in zip(x_lat, y_lon):
            # print((i, j))
            x, y = latlon_to_xy(origin, (i, j))
            # print(f"x: {x:.6f} lat, y: {y:.6f} long")
            gx.append(x)
            gy.append(y)

        # Coordenadas de la cámara
        gx = np.array(gx)
        gy = np.array(gy)
        cx = np.array(cx)
        cy = np.array(cy)

        # Asegúrate de que las coordenadas estén en el formato correcto
        src_points = np.float32([(cx, cy)]).T
        dst_points = np.float32([(gx, gy)]).T

        # Calcular la matriz de transformación
        # Utilizamos una transformación de perspectiva
        return cv2.getPerspectiveTransform(src_points, dst_points)
    else:
        # Coordenadas de la cámara
        gx = np.array(x_lat)
        gy = np.array(y_lon)
        cx = np.array(cx)
        cy = np.array(cy)

        # Asegúrate de que las coordenadas estén en el formato correcto
        src_points = np.float32([(cx, cy)]).T
        dst_points = np.float32([(gx, gy)]).T

        # Calcular la matriz de transformación
        # Utilizamos una transformación de perspectiva
        return cv2.getPerspectiveTransform(src_points, dst_points)
