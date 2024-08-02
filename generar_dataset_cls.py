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
    """
    Pads or reflects an image with edge cases to achieve a cropped region
    of target_size around the bounding box.

    Args:
        image (PIL.Image): The image to be padded or reflected.
        bbox (tuple): Bounding box coordinates (xtl, ytl, xbr, ybr).
        target_size (int, optional): Desired size of the cropped region (default: 608).

    Returns:
        PIL.Image: The padded or reflected cropped image.
    """

    width, height = image.size
    xtl, ytl, xbr, ybr = bbox

    cx = (xtl + xbr) / 2
    cy = (ytl + ybr) / 2

    half_size = target_size // 2

    left = int(cx - half_size)
    upper = int(cy - half_size)
    right = int(cx + half_size)
    lower = int(cy + half_size)

    crop = Image.new("RGB", (target_size, target_size))

    for i in range(left, right, width):
        for j in range(upper, lower, height):
            box = (
                max(0, -i),
                max(0, -j),
                min(width, width - i),
                min(height, height - j),
            )
            region = image.crop(box)
            crop.paste(region, (max(0, i), max(0, j)))

    # Reflecting based on edge cases
    if left < 0:
        crop.paste(ImageOps.mirror(region), (width + i, max(0, j)))
    if upper < 0:
        crop.paste(ImageOps.flip(region), (max(0, i), height + j))
    if left < 0 and upper < 0:
        crop.paste(ImageOps.mirror(ImageOps.flip(region)), (width + i, height + j))
    if right > width:
        crop.paste(region, (0, max(0, j)))  # Paste right side within bounds
    if lower > height:
        crop.paste(region, (max(0, i), 0))  # Paste bottom side within bounds

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
