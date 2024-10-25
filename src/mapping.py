import yaml
import numpy as np
import cv2

# Cargar la matrices de transformacion desde el archivo YAML
with open("config/mapping_640x480.yaml", "r") as archivo_yaml:
    diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)
    # M = np.array(M)


# Recibir un BBox y el id de camara y determinar su posicion en el plano de planta
def bbox_to_planta(bbox, cam_id):
    # print("BBox", bbox)

    # Leer la matriz de transformación correspondiente
    M = np.array(diccionario_cargado[cam_id])

    # Obtener el punto de referencia
    ref_point = diccionario_cargado[f"{cam_id}_ref"]
    if ref_point == "down_center":
        punto_bbox = np.array([[[(bbox[0] + bbox[2]) / 2, bbox[3]]]], dtype=np.float32)
    elif ref_point == "down_corner":
        punto_bbox = np.array([[[bbox[2], bbox[3]]]], dtype=np.float32)
    else:
        # Sino es ninguno de los anteriores usar "center" del bbox por defecto
        punto_bbox = np.array(
            [[[(bbox[2] + bbox[0]) / 2, (bbox[3] + bbox[1]) / 2]]], dtype=np.float32
        )

    # Aplicar la transformación al punto
    punto_bbox_planta = cv2.perspectiveTransform(
        punto_bbox,
        M,  # puede usar la matriz de perspectiva o la de homografía
    )

    # Llevar los puntos a las coordenadas de enteros mas cercano (np.rint) o al entero inferior (np.floor)
    punto_bbox = np.floor(np.array(punto_bbox)).astype(np.int16)[0]
    plano_x_y = np.floor(np.array(punto_bbox_planta)).astype(np.int16)[0]

    # plano_x_y = [x for x in np.array(punto_bbox_planta[0][:][:], dtype=np.int16)]
    # punto_bbox = [x for x in np.array(punto_bbox[0][:][:], dtype=np.int16)]

    # print("Punto en plano", plano_x_y, "Punto camara", punto_bbox)
    return plano_x_y, punto_bbox


def cam_point2planta(point, cam_id):
    M = np.array(diccionario_cargado[cam_id])
    point = np.array([point], dtype=np.float32)
    punto_planta = cv2.perspectiveTransform(point, M)
    return np.floor(np.array(punto_planta)).astype(np.int16)[0]
