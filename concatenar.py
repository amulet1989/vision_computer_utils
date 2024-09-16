import os

# import subprocess
import argparse
from tqdm import tqdm
import cv2


def concatenar_carpeta(camera_folder, output_folder):
    # Define the path to the camera folder
    # camera_folder = "/media/minigo/DATA/Alexander_frigate/reformado/2024-01-18/c11"

    # Get the list of all videos in the folder
    video_files = os.listdir(camera_folder)

    # Sort the videos by timestamp
    # video_files.sort(key=lambda x: get_timestamp(x))
    video_files.sort()

    # for file in video_files:
    #    print(os.path.basename(file))

    # Create the output video file
    output_file_path = os.path.join(
        output_folder, f"{os.path.basename(camera_folder)}.mp4"
    )
    output_video = cv2.VideoWriter(
        output_file_path, cv2.VideoWriter_fourcc(*"mp4v"), 10, (704, 576)
    )  # (1920, 1080)

    # Iterate over the videos and concatenate them
    for video_file in video_files:
        # Get the video timestamp
        # timestamp = get_timestamp(video_file)

        # Load the video
        video = cv2.VideoCapture(os.path.join(camera_folder, video_file))

        # Check if the video is readable
        if not video.isOpened():
            continue

        # Read the video frames
        while True:
            # Read the next frame
            success, frame = video.read()

            # Check if the end of the video has been reached
            if not success:
                break

            # Write the frame to the output video
            output_video.write(frame)

    # Release the output video
    output_video.release()

    # Close the video files
    for video_file in video_files:
        video = cv2.VideoCapture(os.path.join(camera_folder, video_file))
        video.release()


# Obtener la lista de carpetas de cámaras en el directorio base
def main():

    parser = argparse.ArgumentParser(
        description="Pipeline para procesar videos y detección de objetos"
    )
    parser.add_argument(
        "--dir_base",
        default="/media/minigo/DATA/Alexander_frigate/reformado/2024-01-18",
        type=str,
        help="Ruta al archivo de video",
    )
    parser.add_argument(
        "--output_dir",
        default="/media/minigo/DATA/Alexander_frigate/concatenado",
        type=str,
        help="Ruta al directorio de imágenes",
    )
    args = parser.parse_args()

    carpetas_camaras = [
        d
        for d in os.listdir(args.dir_base)
        if os.path.isdir(os.path.join(args.dir_base, d))
    ]

    # Iterar sobre las carpetas de cámaras
    for camara in tqdm(carpetas_camaras, desc="Concatenando cámaras"):
        # print(f"concatenando {camara}")
        concatenar_carpeta(os.path.join(args.dir_base, camara), args.output_dir)

    print("concatenacion terminada")


if __name__ == "__main__":
    main()
