from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from app.database import get_connection, init_db, seed_data
from app.schemas import EventCreate, EventResponse

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Inicializa o schema SQLite e popula eventos de exemplo ao subir a API."""
    init_db()
    seed_data()
    yield


app = FastAPI(
    title="Gerenciador de Eventos da Semana Acadêmica",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/api/events", response_model=list[EventResponse], status_code=status.HTTP_200_OK)
def list_events() -> list[EventResponse]:
    """Lista todos os eventos cadastrados em ordem crescente de ID."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, title, speaker, capacity, created_at FROM events ORDER BY id ASC"
        ).fetchall()
    return [EventResponse(**dict(row)) for row in rows]


@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate) -> EventResponse:
    """Cadastra um novo evento na Semana Acadêmica."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO events (title, speaker, capacity) VALUES (?, ?, ?)",
            (payload.title, payload.speaker, payload.capacity),
        )
        created = conn.execute(
            "SELECT id, title, speaker, capacity, created_at FROM events WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        if created is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recuperar evento recém-criado.",
            )

    return EventResponse(**dict(created))


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
