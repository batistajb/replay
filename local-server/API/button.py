import threading
import pygame
import camera
import logging

from db import database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_thread_button():
    cameras = await database.get_all_cameras()
    threads = []
    for cam in cameras:
        court_id = cam[2]
        button_gpio = cam[4]

        thread = threading.Thread(target=on_press, args=(button_gpio, court_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    return

def on_press(court_id, button_gpio):
    if pygame.joystick.get_count() == 0:
        print("Nenhum gamepad encontrado.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print("Gamepad encontrado:", joystick.get_name())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_gpio:
                print(f"Botão {event.button} pressionado")
                camera.keyboard_pressed[court_id] = True
