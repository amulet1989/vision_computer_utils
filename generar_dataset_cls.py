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


# Función para reflejar la imagen sin incluir el BBox
def pad_and_reflect(image, bbox, target_size=608):
    height, width, _ = image.shape
    xtl, ytl, xbr, ybr = bbox

    cx = (xtl + xbr) / 2
    cy = (ytl + ybr) / 2

    half_size = target_size // 2

    left = int(cx - half_size)
    upper = int(cy - half_size)
    right = int(cx + half_size)
    lower = int(cy + half_size)

    padded_image = np.zeros((target_size, target_size, 3), dtype=image.dtype)

    # Calculate padding
    pad_left = max(0, -left)
    pad_top = max(0, -upper)
    pad_right = max(0, right - width)
    pad_bottom = max(0, lower - height)

    # Calculate cropping area
    crop_left = max(0, left)
    crop_top = max(0, upper)
    crop_right = min(width, right)
    crop_bottom = min(height, lower)

    crop = image[crop_top:crop_bottom, crop_left:crop_right]

    padded_image[
        pad_top : pad_top + crop.shape[0], pad_left : pad_left + crop.shape[1]
    ] = crop

    if pad_left > 0:
        left_reflect = np.fliplr(crop[:, :pad_left])
        padded_image[pad_top : pad_top + crop.shape[0], :pad_left] = left_reflect

    if pad_top > 0:
        top_reflect = np.flipud(crop[:pad_top, :])
        padded_image[:pad_top, pad_left : pad_left + crop.shape[1]] = top_reflect

    if pad_right > 0:
        right_reflect = np.fliplr(crop[:, -pad_right:])
        padded_image[pad_top : pad_top + crop.shape[0], -pad_right:] = right_reflect

    if pad_bottom > 0:
        bottom_reflect = np.flipud(crop[-pad_bottom:, :])
        padded_image[-pad_bottom:, pad_left : pad_left + crop.shape[1]] = bottom_reflect

    if pad_left > 0 and pad_top > 0:
        top_left_reflect = np.flipud(left_reflect[:pad_top, :])
        padded_image[:pad_top, :pad_left] = top_left_reflect

    if pad_right > 0 and pad_top > 0:
        top_right_reflect = np.flipud(right_reflect[:pad_top, :])
        padded_image[:pad_top, -pad_right:] = top_right_reflect

    if pad_left > 0 and pad_bottom > 0:
        bottom_left_reflect = np.flipud(left_reflect[-pad_bottom:, :])
        padded_image[-pad_bottom:, :pad_left] = bottom_left_reflect

    if pad_right > 0 and pad_bottom > 0:
        bottom_right_reflect = np.flipud(right_reflect[-pad_bottom:, :])
        padded_image[-pad_bottom:, -pad_right:] = bottom_right_reflect

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

        cropped_image = pad_and_reflect(img, bbox)

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
