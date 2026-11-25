import os
import re
import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "app.db")))
FORBIDDEN_SQL_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA|VACUUM)\b",
    re.IGNORECASE,
)

mcp = FastMCP("sqlite-readonly")


def _connect_readonly() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Banco SQLite não encontrado em: {DB_PATH}")
    conn = sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_tables() -> list[str]:
    """Retorna os nomes das tabelas existentes no banco SQLite."""
    with _connect_readonly() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return [str(row["name"]) for row in rows]


@mcp.tool()
def describe_table(table_name: str) -> list[dict[str, Any]]:
    """Retorna as colunas e tipos da tabela informada via PRAGMA table_info."""
    if table_name not in list_tables():
        raise ValueError(f"Tabela inválida ou inexistente: {table_name}")
    with _connect_readonly() as conn:
        rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def run_readonly_query(query: str) -> list[dict[str, Any]]:
    """Executa apenas consultas SELECT somente leitura no banco SQLite."""
    cleaned = query.strip().rstrip(";").strip()
    if not cleaned or ";" in cleaned or not cleaned.upper().startswith("SELECT"):
        raise ValueError("Apenas queries SELECT únicas são permitidas.")
    if FORBIDDEN_SQL_RE.search(cleaned):
        raise ValueError("Operações de escrita ou DDL são bloqueadas neste servidor MCP.")
    with _connect_readonly() as conn:
        rows = conn.execute(cleaned).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    mcp.run(transport="stdio")
