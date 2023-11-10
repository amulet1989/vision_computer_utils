from src import utils

images_path = utils.seleccionar_directorio()
utils.resize_images_in_directory(images_path, width=704, height=576)
print("se preprocesaron las imagenes")

# image_path = utils.seleccionar_imagen()
# utils.resize_image(image_path, width=704, height=576)
