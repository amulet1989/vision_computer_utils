import yaml
import numpy as np
import cv2

# Luego, se puede cargar la matriz desde el archivo YAML
with open("mapping_cfg.yaml", "r") as archivo_yaml:
    diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)
    # M = np.array(M)


# Recibir un BBox y determinar su posicion en el plano d eplanta
def bbox_to_planta(bbox, M, cam_id):
    M = np.array(diccionario_cargado[cam_id])
    # Obtener el punto medio del segmento de bbox inferior
    punto_bbox = [int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3])]
    punto_bbox = np.array([punto_bbox], dtype=np.float32)

    # Aplicar la transformación al punto
    punto_bbox_planta = cv2.perspectiveTransform(
        punto_bbox,
        M,  # puede usar la matriz de perspectiva o la de homografía
    )
    return punto_bbox_planta
