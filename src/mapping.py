import yaml
import numpy as np
import cv2

# Luego, se puede cargar la matriz desde el archivo YAML
with open("config/mapping_cfg.yaml", "r") as archivo_yaml:
    diccionario_cargado = yaml.load(archivo_yaml, Loader=yaml.FullLoader)
    # M = np.array(M)


# Recibir un BBox y determinar su posicion en el plano d eplanta
def bbox_to_planta(bbox, cam_id):
    # print("BBox", bbox)

    M = np.array(diccionario_cargado[cam_id])

    # Obtener el punto de referencia
    ref_point = diccionario_cargado[f"{cam_id}_ref"]
    if ref_point == "down_center":
        punto_bbox = np.array([[[(bbox[0] + bbox[2]) / 2, bbox[3]]]], dtype=np.float32)
    elif ref_point == "down_corner":
        punto_bbox = np.array([[[bbox[2], bbox[3]]]], dtype=np.float32)
    else:
        # Usar centro del bbox como punto de referencia
        punto_bbox = np.array(
            [[[(bbox[2] + bbox[0]) / 2, (bbox[3] + bbox[1]) / 2]]], dtype=np.float32
        )

    # Aplicar la transformación al punto
    punto_bbox_planta = cv2.perspectiveTransform(
        punto_bbox,
        M,  # puede usar la matriz de perspectiva o la de homografía
    )
    plano_x_y = [x for x in np.array(punto_bbox_planta[0][:][:], dtype=np.int16)]
    punto_bbox = [x for x in np.array(punto_bbox[0][:][:], dtype=np.int16)]

    # print("Punto en plano", plano_x_y)
    return plano_x_y, punto_bbox
