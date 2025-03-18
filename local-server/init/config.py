import os

from dotenv import load_dotenv

load_dotenv()

WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')
API_CONFIG_URL = os.getenv('API_CONFIG_URL')
DB_FILE = os.getenv('DB_FILE')
SERVER_LOCAL_ID = os.getenv('SERVER_LOCAL_ID')
