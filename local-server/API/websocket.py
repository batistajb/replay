import asyncio
import json
import websockets
import camera
import logging

from db import database
from . import button

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalServer:
    def __init__(self, server_url, server_slug):
        self.server_url = server_url
        self.server_slug = server_slug
        self.websocket = None
        self.token = None

    async def connect(self):
        try:
            connection_url = f"{self.server_url}?server_slug={self.server_slug}"
            self.websocket = await websockets.connect(connection_url)
            logger.info("Conexão estabelecida com sucesso")

            await self.listen_for_messages()

        except Exception as e:
            logger.error(f"Erro na conexão: {str(e)}")
            await asyncio.sleep(5)
            await self.connect()

    async def listen_for_messages(self):
        if not self.websocket:
            return

        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)

                if data["type"] == "token":
                    self.token = data["token"]
                    await self.request_configs()

                elif data["type"] == "get_configs":
                    await self.handle_configs(data)

                elif data["type"] == "request_replay":
                    logger.info(f"Solicitação de replay recebida: {data}")
                    await self.handle_replay_request(data)

                else:
                    logger.warning(f"Tipo de mensagem desconhecido: {data['type']}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("Conexão fechada. Tentando reconectar...")
            await asyncio.sleep(5)
            await self.connect()

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            await asyncio.sleep(5)
            await self.connect()

    async def request_configs(self):
        if not self.websocket:
            logger.error("Websocket não está conectado")
            return

        try:
            await self.send_message({"server_slug": self.server_slug}, "get_configs")
            logger.info("Solicitação de configurações enviada")

        except Exception as e:
            logger.error(f"Erro ao solicitar configurações: {str(e)}")
        return

    async def handle_configs(self, data):
        try:
            database.save_configs(data)
            logger.info("Configurações salvas com sucesso")

            # Envia confirmação
            #await self.send_message({"status": "success", "subject": "confirmation"}, 'configs_received')

            await button.start_thread_button()
           # await camera.start_capture_threads()

        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {str(e)}")
            await self.websocket.send(json.dumps({
                "subject": "confirmation",
                "type": "configs_received",
                "status": "error",
                "message": str(e)
            }))

    async def handle_replay_request(self, data):
        court_id = data.get("court_id")

        if not court_id:
            logger.error("Dados incompletos na solicitação de replay")
            return

        try:
            camera.keyboard_pressed[court_id] = True

            await self.send_message({
                "subject": "confirmation",
                "status": "success",
                "court_id": court_id,
                "message": "Replay iniciado"
            }, 'replay_response')

        except Exception as e:
            logger.error(f"Erro ao processar solicitação de replay: {str(e)}")
            await self.send_message({
                "subject": "confirmation",
                "status": "error",
                "court_id": court_id,
                "message": str(e)
            }, 'replay_response')

    async def send_message(self, data, type):
        if not self.token:
            logger.error("Token não encontrado")
            return

        data['type'] = type
        data['token'] = self.token
        await self.websocket.send(json.dumps(data))
