import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps

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


# Función para reflejar la imagen si es necesario
def pad_and_reflect(image, bbox, target_size=608):
    width, height = image.size
    xtl, ytl, xbr, ybr = bbox

    cx = (xtl + xbr) / 2
    cy = (ytl + ybr) / 2

    half_size = target_size // 2

    left = max(0, int(cx - half_size))
    upper = max(0, int(cy - half_size))
    right = min(width, int(cx + half_size))
    lower = min(height, int(cy + half_size))

    crop = image.crop((left, upper, right, lower))

    # Reflect the padding if necessary
    delta_w = target_size - (right - left)
    delta_h = target_size - (lower - upper)
    padding = (
        delta_w // 2,
        delta_h // 2,
        delta_w - (delta_w // 2),
        delta_h - (delta_h // 2),
    )

    if left == 0 or right == width:
        crop = ImageOps.expand(crop, (padding[0], 0, padding[2], 0), fill=0)
        crop = ImageOps.mirror(crop)
    if upper == 0 or lower == height:
        crop = ImageOps.expand(crop, (0, padding[1], 0, padding[3]), fill=0)
        crop = ImageOps.flip(crop)

    return crop


# Procesar cada imagen en las anotaciones
for image in root.findall("image"):
    image_name = image.get("name")
    image_path = os.path.join(images_folder, image_name)
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found.")
        continue

    img = Image.open(image_path)
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
        cropped_image.save(os.path.join(label_folder, crop_name))

print("Proceso completado.")
