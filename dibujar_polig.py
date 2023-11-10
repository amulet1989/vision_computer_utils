import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import numpy as np

# Crear una ventana Tkinter
root = tk.Tk()
root.title("Editor de Polígonos")

# Variables para dibujar el polígono
dibujando = False
vertices = []
file_path = ""
# Agregar una variable para el factor de zoom
zoom_factor = 1  # Factor de zoom inicial


# Función para cargar una imagen
def cargar_imagen():
    global imagen, canvas, vertices, file_path, zoom_factor, imagen_zoom
    zoom_factor = 1.0
    file_path = filedialog.askopenfilename()
    if file_path:
        imagen = cv2.imread(file_path)
        imagen_zoom = imagen
        actualizar_canvas()
        vertices = []
        # borrar texto
        coordenadas_texto.delete(1.0, tk.END)


def borrar_poligono():
    global imagen, vertices, file_path
    imagen = cv2.imread(file_path)
    actualizar_canvas()
    vertices = []
    # borrar texto
    coordenadas_texto.delete(1.0, tk.END)


# Función para actualizar el canvas
def actualizar_canvas_old():
    global imagen, canvas
    canvas.delete("all")
    if imagen is not None:
        image_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image=image_pil)
        canvas.image = image_tk
        canvas.create_image(0, 0, anchor="nw", image=image_tk)


# Función para actualizar el canvas con el factor de zoom
def actualizar_canvas_no():
    global imagen, canvas, zoom_factor, imagen_zoom
    canvas.delete("all")
    if imagen is not None:
        # Escalar la imagen con el factor de zoom
        imagen_zoom = cv2.resize(imagen, None, fx=zoom_factor, fy=zoom_factor)
        image_rgb = cv2.cvtColor(imagen_zoom, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image=image_pil)
        canvas.image = image_tk
        canvas.create_image(0, 0, anchor="nw", image=image_tk)


# Función para actualizar el canvas
def actualizar_canvas():
    global imagen, canvas, canvas_frame, canvas_scroll_x, canvas_scroll_y
    canvas.delete("all")
    if imagen is not None:
        image_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image=image_pil)
        canvas.image = image_tk
        canvas.create_image(0, 0, anchor="nw", image=image_tk)
        canvas.config(scrollregion=canvas.bbox("all"))  # Configurar el área desplazable


# Función para agregar coordenadas al texto
def agregar_coordenada(x, y):
    coordenadas_texto.insert(tk.END, f"({x}, {y})\n")


# Función para iniciar el dibujo del polígono
def iniciar_dibujo(event):
    global dibujando, vertices, zoom_factor
    dibujando = True
    # vertices = []
    x, y = event.x, event.y
    # imprimir punto en la imagen
    cv2.circle(imagen, (x, y), 5, (0, 0, 255), -1)
    actualizar_canvas()

    vertices.append((x, y))
    agregar_coordenada(x, y)


# Función para finalizar el dibujo del polígono
def dibujar_linea(event):
    global dibujando, vertices, imagen, imagen_zoom
    if dibujando and len(vertices) >= 2:
        # dibujando = False
        # cv2.polylines(imagen, [np.array(vertices)], isClosed=True, color=(0, 0, 255), thickness=2)
        cv2.line(imagen, vertices[-2], (event.x, event.y), (0, 0, 255), 2)
        actualizar_canvas()


def finalizar_dibujo(event):
    global dibujando, vertices, imagen, imagen_zoom
    if dibujando and len(vertices) >= 3:
        dibujando = False
        cv2.polylines(
            imagen,
            [np.array(vertices)],
            isClosed=True,
            color=(0, 0, 255),
            thickness=2,
        )
        # cv2.line(imagen, vertices[0], (event.x, event.y), (0, 0, 255), 2)
        actualizar_canvas()
        print(vertices)


def show_position(event):
    canvas.master.title(f"x={event.x}, y={event.y}")


# Función para aplicar zoom in
def zoom_in():
    global zoom_factor, imagen
    zoom_factor *= 1.2  # Aumentar el zoom en un 20%
    actualizar_canvas()  # Actualizar el lienzo con el nuevo factor de zoom


# Función para aplicar zoom out
def zoom_out():
    global zoom_factor, imagen
    zoom_factor /= 1.2  # Reducir el zoom en un 20%
    actualizar_canvas()  # Actualizar el lienzo con el nuevo factor de zoom

    # actualizar_coordenadas()


# Crear un liezo
canvas = tk.Canvas(root, width=704, height=576)
canvas.pack()

# Crear botones y menús
cargar_btn = tk.Button(root, text="Cargar Imagen", command=cargar_imagen)
cargar_btn.pack()

# Crear boton para borrar poligono
borrar_polig_btn = tk.Button(root, text="Borrar Polígono", command=borrar_poligono)
borrar_polig_btn.pack()

# Crear botones o menús para aplicar zoom in y zoom out
# zoom_in_btn = tk.Button(root, text="Zoom In", command=zoom_in)
# zoom_in_btn.pack()

# zoom_out_btn = tk.Button(root, text="Zoom Out", command=zoom_out)
# zoom_out_btn.pack()

# Ventana de texto para mostrar las coordenadas
coordenadas_texto = tk.Text(root, width=30, height=10)
coordenadas_texto.pack()

# Asociar eventos de mouse para dibujar el polígono
canvas.bind("<ButtonPress-1>", iniciar_dibujo)
# canvas.bind("<ButtonPress-1>", dibujar_polígono)
canvas.bind("<ButtonRelease-1>", dibujar_linea)
# click derecho para finalizar dibujo
canvas.bind("<Button-3>", finalizar_dibujo)

canvas.bind("<Motion>", show_position)


# Inicializar la aplicación
root.mainloop()
