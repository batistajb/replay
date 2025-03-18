import requests
import config

from db import database

def setup_config():
    try:
        response = requests.get(f"{config.API_CONFIG_URL}?server_id={config.SERVER_LOCAL_ID}")
        if response.status_code == 200:
            configs = response.json()
            database.save_configs(configs)
            print("Configurações atualizadas!")
        else:
            print(f"Erro ao baixar configurações: {response.status_code}")
    except Exception as e:
        print(f"Erro na comunicação com o servidor: {e}")

if __name__ == "__main__":
    database.create_database()
    setup_config()
