from moviepy.editor import VideoFileClip, concatenate_videoclips
import os


def concatenar_videos(carpeta):
    # Ruta de la carpeta que contiene los videos
    # carpeta = '/ruta/a/la/carpeta'

    # Obtener la lista de archivos de video en la carpeta
    videos = [f for f in os.listdir(carpeta) if f.endswith(".mp4")]

    # Crear una lista de objetos VideoFileClip
    video_clips = [VideoFileClip(os.path.join(carpeta, video)) for video in videos]

    # Concatenar los clips de video
    video_final = concatenate_videoclips(video_clips, method="compose")

    # Guardar el video final
    video_final.write_videofile(os.path.join(carpeta, "camara.mp4"))
