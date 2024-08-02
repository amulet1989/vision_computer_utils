import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps
import cv2
import numpy as np

# Ruta del archivo de anotaciones y carpeta de imágenes
annotations_path = "./videos_capturados/Pilar_cellphone/annotations.xml"
images_folder = "./videos_capturados/Pilar_cellphone/images/train"
output_folder = "./videos_capturados/Pilar_cellphone/output"

# Crear la carpeta de salida si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Parsear el archivo XML
tree = ET.parse(annotations_path)
root = tree.getroot()


# Función para centrar el BBox y rellenar con ceros
def pad_with_zeros(image, bbox, target_size=608):
    height, width, _ = image.shape
    xtl, ytl, xbr, ybr = bbox

    cx = int((xtl + xbr) / 2)
    cy = int((ytl + ybr) / 2)

    half_size = target_size // 2

    left = cx - half_size
    upper = cy - half_size
    right = cx + half_size
    lower = cy + half_size

    # Initialize padded image with zeros
    padded_image = np.zeros((target_size, target_size, 3), dtype=image.dtype)

    # Calculate cropping area
    crop_left = max(0, left)
    crop_top = max(0, upper)
    crop_right = min(width, right)
    crop_bottom = min(height, lower)

    # Calculate the placement in the padded image
    pad_left = max(0, -left)
    pad_top = max(0, -upper)
    pad_right = max(0, right - width)
    pad_bottom = max(0, lower - height)

    crop = image[crop_top:crop_bottom, crop_left:crop_right]
    padded_image[
        pad_top : pad_top + crop.shape[0], pad_left : pad_left + crop.shape[1]
    ] = crop

    return padded_image


# Procesar cada imagen en las anotaciones
for image in root.findall("image"):
    image_name = image.get("name")
    image_path = os.path.join(images_folder, image_name)
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found.")
        continue

    img = cv2.imread(image_path)
    label_count = {}

    for box in image.findall("box"):
        label = box.get("label")
        xtl = float(box.get("xtl"))
        ytl = float(box.get("ytl"))
        xbr = float(box.get("xbr"))
        ybr = float(box.get("ybr"))

        bbox = (xtl, ytl, xbr, ybr)

        cropped_image = pad_with_zeros(img, bbox)

        label_folder = os.path.join(output_folder, label)
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)

        # Contador para asegurar nombres únicos
        if label not in label_count:
            label_count[label] = 0
        label_count[label] += 1

        base_name, ext = os.path.splitext(image_name)
        crop_name = f"{base_name}_crop_{label}_{label_count[label]}.jpg"
        cv2.imwrite(os.path.join(label_folder, crop_name), cropped_image)

print("Proceso completado.")
