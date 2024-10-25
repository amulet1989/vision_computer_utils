import subprocess
import glob
import os
from datetime import datetime, timedelta


def get_video_metadata(video_path):
    # Extraer el tiempo de inicio y duración
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_entries",
        "stream=start_time",
        "-of",
        "default=noprint_wrappers=1",
        video_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error obteniendo metadatos de {video_path}: {result.stderr}")
        return None, None

    metadata = result.stdout.strip().splitlines()
    try:
        start_time_unix = float(metadata[0].split("=")[1])  # Extraer start_time
        duration = float(metadata[1].split("=")[1])  # Extraer duration
        return start_time_unix, duration
    except (IndexError, ValueError) as e:
        print(f"Error procesando metadatos de {video_path}: {e}")
        return None, None


def find_camera_time_range(clips_folder):
    # Encontrar el inicio más temprano y el fin más tarde dentro de los clips de una cámara
    clips = sorted(glob.glob(os.path.join(clips_folder, "*.mkv")))
    start_times = []
    end_times = []

    for clip in clips:
        start_time, duration = get_video_metadata(clip)
        if start_time is not None and duration is not None:
            start_times.append(start_time)
            end_times.append(start_time + duration)
        else:
            print(f"Clip inválido omitido: {clip}")

    if start_times and end_times:
        earliest_start = min(start_times)
        latest_end = max(end_times)
        return earliest_start, latest_end
    else:
        return None, None


def concatenate_clips(clips_folder, output_concat_path):
    # Crear un archivo de lista para concatenación en FFmpeg
    with open("concat_list.txt", "w") as f:
        for clip in sorted(glob.glob(os.path.join(clips_folder, "*.mkv"))):
            f.write(f"file '{clip}'\n")

    # Ejecutar la concatenación de clips
    concat_command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "concat_list.txt",
        "-c",
        "copy",
        output_concat_path,
    ]
    subprocess.run(concat_command, check=True)
    print("Concatenación completada:", output_concat_path)
    os.remove("concat_list.txt")


def synchronize_videos(
    concatenated_videos, global_start, global_end, camera_time_ranges
):
    # Calcular y aplicar los recortes de sincronización para cada video concatenado
    sync_duration = global_end - global_start

    for i, video in enumerate(concatenated_videos):
        cam_start, cam_end = camera_time_ranges[i]

        # Calcular recorte al inicio y al final
        start_offset = global_start - cam_start
        end_offset = cam_end - global_end
        output_sync_path = f"{os.path.splitext(video)[0]}_synced.mkv"

        crop_command = [
            "ffmpeg",
            "-i",
            video,
            "-ss",
            str(start_offset),  # Tiempo a eliminar desde el inicio
            "-t",
            str(sync_duration),  # Duración final sincronizada
            "-c",
            "copy",
            output_sync_path,
        ]
        subprocess.run(crop_command, check=True)
        print(f"Video sincronizado guardado en: {output_sync_path}")


def process_videos_directory(main_directory):
    concatenated_videos = []
    camera_time_ranges = []

    # Buscar todas las carpetas en el directorio principal
    for cam_folder in sorted(glob.glob(os.path.join(main_directory, "*/"))):
        camera_name = os.path.basename(os.path.normpath(cam_folder))
        output_concat_path = os.path.join(
            main_directory, f"{camera_name}_concatenated.mkv"
        )

        # Obtener los tiempos de inicio y fin de la cámara
        earliest_start, latest_end = find_camera_time_range(cam_folder)
        if earliest_start is not None and latest_end is not None:
            camera_time_ranges.append((earliest_start, latest_end))

            # Concatenar videos en la carpeta de cada cámara
            concatenate_clips(cam_folder, output_concat_path)
            concatenated_videos.append(output_concat_path)
        else:
            print(f"No se encontraron clips válidos en {cam_folder}")

    # Calcular los tiempos de inicio y fin globales
    global_start = max(start for start, _ in camera_time_ranges)
    global_end = min(end for _, end in camera_time_ranges)

    # Sincronizar todos los videos concatenados
    synchronize_videos(
        concatenated_videos, global_start, global_end, camera_time_ranges
    )
    return global_start, global_end


# Directorio principal que contiene las carpetas de cada cámara
main_directory = "videos_capturados/Concatenar"
global_start, global_end = process_videos_directory(main_directory)

print(f"Tiempo de inicio global: {datetime.fromtimestamp(global_start)}")
print(f"Tiempo de fin global: {datetime.fromtimestamp(global_end)}")
