import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "app.db")))

mcp = FastMCP("sqlite-readonly")


def _connect_readonly() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Banco SQLite não encontrado em: {DB_PATH}")
    conn = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_tables() -> list[str]:
    """Retorna os nomes das tabelas existentes no banco SQLite."""
    with closing(_connect_readonly()) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT GLOB 'sqlite_*' ORDER BY name"
        ).fetchall()
    return [str(row["name"]) for row in rows]


@mcp.tool()
def describe_table(table_name: str) -> list[dict[str, Any]]:
    """Retorna as colunas e tipos da tabela informada via PRAGMA table_info."""
    if table_name not in list_tables():
        raise ValueError(f"Tabela inválida ou inexistente: {table_name}")
    with closing(_connect_readonly()) as conn:
        rows = conn.execute("SELECT * FROM pragma_table_info(?)", (table_name,)).fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def run_readonly_query(query: str) -> list[dict[str, Any]]:
    """Executa apenas consultas SELECT somente leitura no banco SQLite."""
    cleaned = query.lstrip()
    if re.match(r"SELECT\b", cleaned, re.IGNORECASE) is None:
        raise ValueError("Apenas queries SELECT únicas são permitidas.")
    # execute() aceita uma única instrução e a conexão usa mode=ro.
    with closing(_connect_readonly()) as conn:
        rows = conn.execute(cleaned).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    mcp.run(transport="stdio")
