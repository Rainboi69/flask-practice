"""Database connection and schema setup for Recipe Box API."""

import sqlite3
from flask import current_app


def get_db_connection():
    """Open a SQLite connection using the configured database."""
    database_path = current_app.config["DATABASE"]

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db(app):
    """Create the database tables if they do not exist."""
    database_path = app.config["DATABASE"]

    connection = sqlite3.connect(database_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL DEFAULT '',
                is_public INTEGER NOT NULL DEFAULT 1,
                owner_id INTEGER,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            );
        """)

        connection.commit()

    finally:
        connection.close()