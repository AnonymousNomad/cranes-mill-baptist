import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('CHURCH_DB_PATH', ROOT / 'data' / 'church.sqlite3'))
SEED_PATH = ROOT / 'content' / 'seed.json'


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            speaker TEXT NOT NULL,
            published_on TEXT NOT NULL,
            scripture TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            video_url TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )''')
        connection.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL DEFAULT '',
            location TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )''')
        connection.execute('''CREATE TABLE IF NOT EXISTS prayer_requests (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        connection.execute('''CREATE TABLE IF NOT EXISTS site_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )''')
        connection.execute('''CREATE TABLE IF NOT EXISTS ministries (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            action_label TEXT NOT NULL DEFAULT '',
            action_route TEXT NOT NULL DEFAULT 'contact',
            image_url TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )''')
        connection.execute('''CREATE TABLE IF NOT EXISTS music_tracks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL DEFAULT '',
            audio_url TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )''')
        connection.execute('CREATE INDEX IF NOT EXISTS idx_sermons_published ON sermons (published_on DESC, id DESC)')
        connection.execute('CREATE INDEX IF NOT EXISTS idx_events_schedule ON events (event_date ASC, event_time ASC, id ASC)')
        connection.execute('CREATE INDEX IF NOT EXISTS idx_ministries_order ON ministries (sort_order ASC, id ASC)')
        connection.execute('CREATE INDEX IF NOT EXISTS idx_prayer_created ON prayer_requests (created_at DESC, id DESC)')
        connection.execute('CREATE INDEX IF NOT EXISTS idx_music_order ON music_tracks (sort_order ASC, id ASC)')
        connection.execute('PRAGMA optimize')
        seed_if_empty(connection)


def seed_if_empty(connection):
    sermon_count = connection.execute('SELECT COUNT(*) FROM sermons').fetchone()[0]
    event_count = connection.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    seed = json.loads(SEED_PATH.read_text(encoding='utf-8'))
    timestamp = datetime.now(timezone.utc).isoformat()
    if not sermon_count and not event_count:
        connection.executemany('''INSERT INTO sermons
            (title, speaker, published_on, scripture, summary, video_url, image_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', [
            (item['title'], item['speaker'], item['published_on'], item.get('scripture', ''), item.get('summary', ''), item.get('video_url', ''), item.get('image_url', ''), timestamp)
            for item in seed.get('sermons', [])
        ])
        connection.executemany('''INSERT INTO events
            (title, event_date, event_time, location, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)''', [
            (item['title'], item['event_date'], item.get('event_time', ''), item.get('location', ''), item.get('description', ''), timestamp)
            for item in seed.get('events', [])
        ])
    settings_count = connection.execute('SELECT COUNT(*) FROM site_settings').fetchone()[0]
    site_records = list(seed.get('site', {}).items())
    if not settings_count:
        connection.executemany('INSERT INTO site_settings (key, value) VALUES (?, ?)', site_records)
    else:
        connection.executemany('INSERT OR IGNORE INTO site_settings (key, value) VALUES (?, ?)', site_records)
    ministries_count = connection.execute('SELECT COUNT(*) FROM ministries').fetchone()[0]
    if not ministries_count:
        connection.executemany('''INSERT INTO ministries
            (title, summary, action_label, action_route, image_url, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', [
            (item['title'], item['summary'], item.get('action_label', ''), item.get('action_route', 'contact'), item.get('image_url', ''), index, timestamp)
            for index, item in enumerate(seed.get('ministries', []), start=1)
        ])


def list_sermons():
    with connect() as connection:
        rows = connection.execute('SELECT id, title, speaker, published_on, scripture, summary, video_url, image_url FROM sermons ORDER BY published_on DESC, id DESC').fetchall()
    return [dict(row) for row in rows]


def list_events():
    with connect() as connection:
        rows = connection.execute('SELECT id, title, event_date, event_time, location, description FROM events ORDER BY event_date ASC, event_time ASC, id ASC').fetchall()
    return [dict(row) for row in rows]


def create_sermon(record):
    with connect() as connection:
        cursor = connection.execute('''INSERT INTO sermons
            (title, speaker, published_on, scripture, summary, video_url, image_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (*record, datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid


def create_event(record):
    with connect() as connection:
        cursor = connection.execute('''INSERT INTO events
            (title, event_date, event_time, location, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)''', (*record, datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid


def create_prayer_request(record):
    with connect() as connection:
        cursor = connection.execute('''INSERT INTO prayer_requests
            (name, email, message, created_at)
            VALUES (?, ?, ?, ?)''', (*record, datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid


def list_prayer_requests():
    with connect() as connection:
        rows = connection.execute('SELECT id, name, email, message, created_at FROM prayer_requests ORDER BY created_at DESC, id DESC').fetchall()
    return [dict(row) for row in rows]


def list_site_content():
    with connect() as connection:
        rows = connection.execute('SELECT key, value FROM site_settings ORDER BY key').fetchall()
    return {row['key']: row['value'] for row in rows}


def set_site_content(records):
    with connect() as connection:
        connection.executemany('''INSERT INTO site_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value''', records)


def list_ministries():
    with connect() as connection:
        rows = connection.execute('''SELECT id, title, summary, action_label, action_route, image_url
            FROM ministries ORDER BY sort_order ASC, id ASC''').fetchall()
    return [dict(row) for row in rows]


def create_ministry(record):
    with connect() as connection:
        cursor = connection.execute('''INSERT INTO ministries
            (title, summary, action_label, action_route, image_url, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (*record, datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid


def list_music_tracks():
    with connect() as connection:
        rows = connection.execute('''SELECT id, title, artist, audio_url, sort_order
            FROM music_tracks ORDER BY sort_order ASC, id ASC''').fetchall()
    return [dict(row) for row in rows]


def create_music_track(record):
    with connect() as connection:
        cursor = connection.execute('''INSERT INTO music_tracks
            (title, artist, audio_url, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?)''', (*record, datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid
