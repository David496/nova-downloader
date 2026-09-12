import sqlite3
import os
from datetime import datetime
from core.config import get_storage_path

DB_PATH = get_storage_path("history.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA busy_timeout=5000;')
    return conn

def init_db():
    conn = get_connection()
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
    # Clean up orphan audio records that were falsely registered with .mp4 path when a corresponding .mp3 exists
    cursor.execute('''
        DELETE FROM downloads
        WHERE file_type = 'audio' AND path LIKE '%.mp4'
        AND title IN (
            SELECT title FROM downloads WHERE file_type = 'audio' AND (path LIKE '%.mp3' OR path LIKE '%.m4a' OR path LIKE '%.opus' OR path LIKE '%.webm')
        )
    ''')
    # Clean up existing duplicates from database
    cursor.execute('''
        DELETE FROM downloads 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM downloads 
            GROUP BY title, path, file_type
        )
    ''')
    conn.commit()
    conn.close()

def add_download(title, url, file_type, quality, size, path):
    if not title or not path:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    if file_type == 'audio':
        cursor.execute('''
            SELECT id FROM downloads 
            WHERE file_type = 'audio' AND (path = ? OR (title = ? AND (path LIKE '%.mp3' OR path LIKE '%.m4a' OR path LIKE '%.wav' OR path LIKE '%.flac')))
        ''', (path, title))
        if cursor.fetchone():
            conn.close()
            return
    else:
        cursor.execute('SELECT id FROM downloads WHERE title = ? AND path = ? AND file_type = ?', (title, path, file_type))
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM downloads ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_from_history(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM downloads WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def clear_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM downloads')
    conn.commit()
    conn.close()

def add_saved_playlist(title, url, thumbnail="", track_count=0):
    if not url:
        return
    conn = get_connection()
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT OR REPLACE INTO saved_playlists (title, url, thumbnail, track_count, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (title or "Playlist de YouTube", url, thumbnail, track_count, date_str))
    conn.commit()
    conn.close()

def get_saved_playlists():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, title, url, thumbnail, track_count, date FROM saved_playlists ORDER BY id DESC')
        rows = cursor.fetchall()
    except Exception:
        rows = []
    conn.close()
    return rows

def delete_saved_playlist(playlist_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_playlists WHERE id = ?', (playlist_id,))
    conn.commit()
    conn.close()

init_db()
