import os
import csv
import json
from PIL import Image


def generate_crops(input_folder, output_folder, embeddings_file):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Lista para almacenar los datos de los recortes
    results = []

    # Leer el archivo embeddings.csv
    with open(embeddings_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            source_id = row["sourceId"]
            frame_id = row["frameId"]
            object_id = row["objectId"]
            top = float(row["top"])
            left = float(row["left"])
            width = float(row["width"])
            height = float(row["height"])
            embeddings = [
                float(val) for val in row["embeddings"].split(";") if val.strip()
            ]

            # Cargar la imagen del frame
            frame_path = os.path.join(input_folder, f"frame_{frame_id.zfill(7)}.jpg")

            if not os.path.exists(frame_path):
                print(f"Error: El archivo {frame_path} no existe.")
                continue
            frame_image = Image.open(frame_path)

            # Recortar la región de interés (ROI) de la imagen
            bbox = (left, top, left + width, top + height)
            cropped_image = frame_image.crop(bbox)

            # Guardar el recorte
            output_path = os.path.join(
                output_folder,
                f"{object_id.zfill(4)}_c{source_id}s1_{frame_id.zfill(7)}.jpg",
            )
            cropped_image.save(output_path)

            # Agregar los datos a la lista de resultados
            result_data = {
                "img_path": os.path.relpath(output_path, start=output_folder),
                "embedding": embeddings,
            }
            results.append(result_data)

    # Guardar todos los datos en un archivo JSON único
    json_output_path = os.path.join(output_folder, "results.json")
    with open(json_output_path, "w") as json_file:
        json.dump(results, json_file, indent=4)


if __name__ == "__main__":
    s = "03"
    input_folder = f"./verificar/frames/source{s}"
    output_folder = f"./verificar/output{s}"
    embeddings_file = os.path.join(input_folder, "embeddings.csv")
    generate_crops(input_folder, output_folder, embeddings_file)
