---
name: criar-endpoint
description: >-
  Use esta skill quando o usuário pedir para criar, implementar ou adicionar um
  novo endpoint ou funcionalidade à API FastAPI. Ativada automaticamente ao
  receber pedidos como "implemente a rota de inscrição", "adicione o endpoint de
  cancelamento" ou "crie o CRUD de X". Também pode ser invocada manualmente
  via /criar-endpoint.
---

# Skill: Criar Endpoint FastAPI

Playbook passo a passo para adicionar um novo endpoint à API do Gerenciador de Eventos.

## Passo 1 — Inspecione o Schema via MCP

Antes de qualquer código, consulte o banco atual:

```
list_tables()
describe_table("events")
describe_table("registrations")  # se relevante
```

Nunca assuma colunas ou tipos. O schema é fonte de verdade.

## Passo 2 — Atualize os Schemas Pydantic

Edite `app/schemas.py`:
- Crie um schema de **criação** (`XCreate`) com `Field(...)` e validações.
- Crie um schema de **resposta** (`XResponse`) com `ConfigDict(from_attributes=True)`.
- Nunca duplique campos já existentes em schemas de outros recursos.

## Passo 3 — Implemente a Rota

Edite `app/main.py` (ou crie `app/routers/<recurso>.py` para routers dedicados):
- Use `@app.<método>("/api/<recurso>", response_model=..., status_code=status.HTTP_<X>_<Y>)`.
- Feche a conexão com `with closing(get_connection()) as conn` e use `with conn` para delimitar transações de escrita.
- Use **sempre** queries parametrizadas com `?`.
- Trate erros com `HTTPException` e `detail` descritivo.

## Passo 4 — Escreva os Testes

Edite (ou crie) `tests/test_<recurso>.py`:
- Mínimo de **2 testes**: um de sucesso (happy path) e um de erro/edge case.
- Use o padrão da fixture `client` de `tests/test_events.py`, com banco temporário via `tmp_path`.
- Verifique: status code, estrutura do JSON de resposta, persistência no banco.

Exemplos de edge cases para inscrições:
- Tentar inscrever em evento inexistente → 404.
- Tentar inscrever quando capacidade está esgotada → 409.
- Tentar inscrever com e-mail inválido → 422.

## Passo 5 — Valide com pytest

Rode os testes e confirme que passam:

```bash
pytest -v
```

O hook `PostToolUse` roda `pytest -q` após edições por `write_to_file` e `replace_file_content`. Se falhar, leia o output, corrija e re-rode.

## Checklist Final

- [ ] Schema consultado via MCP antes do código.
- [ ] Schemas Pydantic criados/atualizados em `app/schemas.py`.
- [ ] Rota implementada com tipagem, status code explícito e SQL parametrizado.
- [ ] Mínimo 2 testes: sucesso + edge case.
- [ ] `pytest -v` passando completamente (zero falhas).
