import subprocess
import time
import argparse
import os
import signal
import shutil


def start_gst_pipelines(record_time, output_path):
    # Obtener la fecha y hora actual para generar nombres de archivo
    current_datetime = time.strftime("%Y%m%d_%H%M%S")

    commands = [
        f"gst-launch-1.0 rtspsrc location=rtsp://admin:2Mini001.@192.168.88.122 ! application/x-rtp, media=video, encoding-name=H265! queue ! rtph265depay ! h265parse ! nvv4l2decoder ! nvvidconv ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location={output_path}/camera122_{current_datetime}_h265.mkv",
        f"gst-launch-1.0 rtspsrc location=rtsp://admin:2Mini001.@192.168.88.52 ! application/x-rtp, media=video, encoding-name=H265! queue ! rtph265depay ! h265parse ! nvv4l2decoder ! nvvidconv ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location={output_path}/camera52_{current_datetime}_h265.mkv",
        f"gst-launch-1.0 rtspsrc location=rtsp://admin:2Mini001.@192.168.88.62 ! application/x-rtp, media=video, encoding-name=H265! queue ! rtph265depay ! h265parse ! nvv4l2decoder ! nvvidconv ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location={output_path}/camera62_{current_datetime}_h265.mkv",
        f"gst-launch-1.0 rtspsrc location=rtsp://admin:2Mini001.@192.168.88.71 ! application/x-rtp, media=video, encoding-name=H265! queue ! rtph265depay ! h265parse ! nvv4l2decoder ! nvvidconv ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location={output_path}/camera71_{current_datetime}_h265.mkv",
    ]

    process_group = []
    video_files = []  # Lista para almacenar nombres de archivos MKV

    for command in commands:
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        process_group.append(process)

    # Esperar el tiempo de grabación especificado
    time.sleep(record_time)

    # Enviar la señal SIGINT (2) a cada proceso en el grupo
    for process in process_group:
        os.killpg(os.getpgid(process.pid), signal.SIGINT)

    # Esperar a que todos los procesos se detengan
    for process in process_group:
        process.wait()

    # Convertir archivos MKV a MP4 y eliminar los archivos MKV
    for command in commands:
        mkv_file = f"{command.split()[-1].replace('location=', '')}"
        mp4_file = mkv_file.replace(".mkv", ".mp4")

        # Comando GStreamer para la conversión
        convert_command = f'gst-launch-1.0 filesrc location={mkv_file} ! matroskademux ! h265parse ! nvv4l2decoder ! nvvidconv ! "video/x-raw(memory:NVMM),width=1280,height=720" ! nvv4l2h264enc ! h264parse ! mp4mux ! filesink location={mp4_file}'
        subprocess.run(convert_command, shell=True)

        # Agregar el archivo MP4 a la lista
        video_files.append(mp4_file)

        # Eliminar el archivo MKV
        os.remove(mkv_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Iniciar pipelines GStreamer con opciones configurables."
    )
    parser.add_argument(
        "--record-time", type=int, default=120, help="Tiempo de grabación en segundos"
    )

    parser.add_argument(
        "--output_path",
        type=str,
        default="./videos_capturados",
        help="Tiempo de grabación en segundos",
    )

    args = parser.parse_args()

    start_gst_pipelines(args.record_time, args.output_path)
