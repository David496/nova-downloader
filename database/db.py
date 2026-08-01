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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            thumbnail TEXT,
            track_count INTEGER,
            date TEXT
        )
    ''')
    # Clean up existing duplicates from database
    cursor.execute('''
        DELETE FROM downloads 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM downloads 
            GROUP BY title, path
        )
    ''')
    conn.commit()
    conn.close()

def add_download(title, url, file_type, quality, size, path):
    if not title or not path:
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM downloads WHERE title = ? AND path = ?', (title, path))
    if cursor.fetchone():
        conn.close()
        return

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

def add_saved_playlist(title, url, thumbnail="", track_count=0):
    if not url:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT OR REPLACE INTO saved_playlists (title, url, thumbnail, track_count, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (title or "Playlist de YouTube", url, thumbnail, track_count, date_str))
    conn.commit()
    conn.close()

def get_saved_playlists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, title, url, thumbnail, track_count, date FROM saved_playlists ORDER BY id DESC')
        rows = cursor.fetchall()
    except Exception:
        rows = []
    conn.close()
    return rows

def delete_saved_playlist(playlist_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_playlists WHERE id = ?', (playlist_id,))
    conn.commit()
    conn.close()

init_db()
