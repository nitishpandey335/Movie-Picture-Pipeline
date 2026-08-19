import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "movies.db")

SEED_MOVIES = [
    (123, "Top Gun: Maverick", "Fighter planes"),
    (456, "Sonic the Hedgehog", "Blue Sega character"),
    (789, "A Quiet Place", "Scary monsters"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT
        )
        """
    )
    conn.executemany(
        "INSERT OR IGNORE INTO movies (id, title, description) VALUES (?, ?, ?)",
        SEED_MOVIES,
    )
    conn.commit()
    conn.close()


def get_all_movies():
    conn = get_connection()
    rows = conn.execute("SELECT id, title FROM movies ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_movie(movie_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, title, description FROM movies WHERE id = ?", (movie_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
