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

    left = int(cx - half_size)
    upper = int(cy - half_size)
    right = int(cx + half_size)
    lower = int(cy + half_size)

    # Reflecting the required parts
    if left < 0 or right > width or upper < 0 or lower > height:
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

                if i < 0:  # reflect left side
                    crop.paste(ImageOps.mirror(region), (width + i, max(0, j)))
                if j < 0:  # reflect top side
                    crop.paste(ImageOps.flip(region), (max(0, i), height + j))
                if i < 0 and j < 0:  # reflect top-left corner
                    crop.paste(
                        ImageOps.mirror(ImageOps.flip(region)), (width + i, height + j)
                    )
    else:
        crop = image.crop((left, upper, right, lower))

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
