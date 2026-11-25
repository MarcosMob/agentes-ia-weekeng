import os
import sqlite3
from pathlib import Path

DB_PATH: Path = Path(os.getenv("DATABASE_PATH", "app.db"))


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Retorna uma conexão SQLite configurada com Row factory e foreign keys."""
    target = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Cria as tabelas iniciais do banco caso ainda não existam."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                speaker TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                participant_name TEXT NOT NULL,
                participant_email TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


def seed_data(db_path: Path | None = None) -> None:
    """Insere 2 eventos de exemplo caso a tabela events esteja vazia."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM events").fetchone()
        if row is not None and row["total"] > 0:
            return

        sample_events = [
            (
                "Dos Transformers ao Terminal: Agentes de IA na Prática",
                "Profa. Ana Paula Ribeiro",
                40,
            ),
            (
                "Arquitetura Hub-and-Spoke com FastAPI e MCP",
                "Prof. Carlos Eduardo Lima",
                30,
            ),
        ]
        conn.executemany(
            "INSERT INTO events (title, speaker, capacity) VALUES (?, ?, ?)",
            sample_events,
        )
        conn.commit()
