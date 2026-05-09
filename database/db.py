import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            file_type TEXT,
            quality TEXT,
            date TEXT,
            size TEXT,
            path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_download(title, url, file_type, quality, size, path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO downloads (title, url, file_type, quality, date, size, path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, url, file_type, quality, date_str, size, path))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM downloads ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_from_history(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM downloads WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM downloads')
    conn.commit()
    conn.close()

init_db()
