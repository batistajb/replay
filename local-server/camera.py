import os
import cv2
import threading
import logging

from db import database

from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

keyboard_pressed = {}
stop_recording = False
start_recording = False

def create_capture_system(ip_camera_url, output_folder, court_id):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(ip_camera_url)

    if not cap.isOpened():
        raise Exception("Não foi possível conectar à câmera IP.")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    buffer_size = int(fps * 20)
    frame_buffer = []

    try:
        global keyboard_pressed
        global start_recording
        global stop_recording

        while True:
            ret, frame = cap.read()
            if not ret:
                raise Exception("Erro ao ler frame da câmera. Reconectando...")

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)

            frame_buffer.append(frame.copy())
            if len(frame_buffer) > buffer_size:
                frame_buffer.pop(0)

            if keyboard_pressed.get(court_id, False):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                replay_path = f"{output_folder}/replay_{timestamp}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                replay_out = cv2.VideoWriter(replay_path, fourcc, fps, (frame_width, frame_height))

                print(f"Salvando replay em {replay_path}")
                for replay_frame in frame_buffer:
                    replay_out.write(replay_frame)

                replay_out.release()
                keyboard_pressed[court_id] = False
                logger.info(f"Replay salvo em {replay_path}")

            if start_recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{output_folder}/match_{timestamp}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
                logger.info(f"Iniciando gravação em {output_path}")

            if stop_recording:
                out.release()
                out.write(frame)
                stop_recording = False
                start_recording = False
                logger.info(f"Gravação finalizada em {output_path}")

    finally:
        cap.release()
        if 'out' in locals() and out.isOpened():
            out.release()

async def start_capture_threads():
    cameras = await database.get_all_cameras()
    threads = []
    for camera in cameras:
        court_id = camera[2]
        camera_url = camera[3]
        output_folder = f'replays/{court_id}'
        keyboard_pressed[court_id] = False

        thread = threading.Thread(target=create_capture_system, args=(camera_url,output_folder, court_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    return
