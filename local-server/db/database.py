import sqlite3
from init import config

def create_database():
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY,
            establishmentId INTEGER,
            time_replay INTEGER
        )
    ''')

    cursor.execute('''
           CREATE TABLE IF NOT EXISTS courts (
               id INTEGER PRIMARY KEY,
               establishmentId INTEGER,
               name TEXT
           )
       ''')

    cursor.execute('''
           CREATE TABLE IF NOT EXISTS cameras (
               id INTEGER PRIMARY KEY,
               establishmentId INTEGER,
               courtId INTEGER,
               camera_url VARCHAR(255),
               button_gpio VARCHAR(255)
           )
       ''')


    print("banco de dados configurado...")

    conn.commit()
    conn.close()

def save_configs(data):
    create_database()

    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM configs")
    cursor.execute("DELETE FROM courts")
    cursor.execute("DELETE FROM cameras")

    cursor.execute('''
        INSERT INTO configs (establishmentId, time_replay)
        VALUES (?, ?)
    ''', (data['configs']['establishment_id'], data['configs']['time_replay']))

    for court in data['courts']:
        cursor.execute('''
            INSERT INTO courts (establishmentId, name)
            VALUES (?, ?)
        ''', (court['establishment_id'], court['name']))

    for camera in data['cameras']:
        cursor.execute('''
            INSERT INTO cameras (establishmentId, courtId, camera_url, button_gpio)
            VALUES (?, ?, ?, ?)
        ''', (camera['establishment_id'], camera['court_id'], camera['camera_url'], camera['button_gpio']))

    conn.commit()
    conn.close()

def get_configs():
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM configs")
    data = cursor.fetchall()

    conn.close()
    return data

def get_cameras_info(establishment_id, court_id):
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cameras WHERE establishmentId = ? AND courtId = ?", (establishment_id, court_id))
    data = cursor.fetchall()

    conn.close()
    return data

async def get_all_cameras():
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cameras")
    data = cursor.fetchall()

    conn.close()
    return data

def get_cam_by_button(button):
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cameras WHERE button = ?", button)
    data = cursor.fetchone()

    conn.close()
    return data