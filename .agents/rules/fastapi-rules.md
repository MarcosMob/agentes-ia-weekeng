---
trigger: glob
globs: "app/**/*.py"
description: "Regras de qualidade de código para arquivos do backend FastAPI (app/**/*.py)."
---

# Regras FastAPI — Backend

Estas regras aplicam-se **exclusivamente** aos arquivos dentro de `app/`.

## Tipagem

- Use type hints em **todas** as funções: parâmetros, retornos e variáveis locais relevantes.
- Nunca use `Any` sem justificativa explícita em comentário.
- Para coleções, prefira `list[T]`, `dict[K, V]`, `tuple[T, ...]` ao invés de `List`, `Dict`, `Tuple` do `typing`.

## Pydantic v2

- Todos os schemas de entrada e saída devem herdar de `pydantic.BaseModel`.
- Use `model_config = ConfigDict(from_attributes=True)` em schemas de resposta (ORM mode).
- Use `Field(...)` com validações (`min_length`, `gt`, `le`, etc.) em schemas de criação.
- Nunca acesse atributos de um `Row` SQLite como `row.coluna` — use sempre `row["coluna"]` ou `dict(row)`.

## SQL Seguro

- **Nunca** use f-string ou `.format()` para montar queries SQL. Sempre use parâmetros `?`.
  - ✅ Correto: `conn.execute("SELECT * FROM events WHERE id = ?", (event_id,))`
  - ❌ Errado: `conn.execute(f"SELECT * FROM events WHERE id = {event_id}")`

## Status Codes

- Sempre use constantes de `fastapi.status` ao definir `status_code`:
  - `status.HTTP_200_OK`, `status.HTTP_201_CREATED`, `status.HTTP_404_NOT_FOUND`, etc.
- Nunca use literais numéricos (`201`, `404`) diretamente nos decoradores de rota.

## Estrutura de Rotas

- Rotas da API ficam em `app/main.py` ou em routers dedicados em `app/routers/`.
- Cada endpoint deve ter: docstring explicando o que faz, tipagem de entrada/saída e status code explícito.
- Use `HTTPException` para erros previsíveis com `detail` descritivo em português.
