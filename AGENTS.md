# AGENTS.md — Gerenciador de Eventos da Semana Acadêmica

## Visão Geral

Este repositório é a base prática do workshop **"Desenvolvimento com Agentes de IA na Prática"**. O objetivo é evoluir um Gerenciador de Eventos simples usando o Antigravity CLI (`agy`), passando por 5 camadas de engenharia de agentes.

---

## Stack Técnica

| Componente | Tecnologia |
|:-----------|:-----------|
| Backend | Python 3.10+ + FastAPI |
| Banco de Dados | SQLite local (`app.db`) |
| Frontend | HTML / CSS / JavaScript puro |
| Testes | `pytest` + `httpx` |
| Agente CLI | Antigravity CLI (`agy`) |

---

## Comandos Essenciais

```bash
# Subir a aplicação (acesse http://127.0.0.1:8000)
uvicorn app.main:app --reload

# Rodar todos os testes
pytest -v

# Rodar testes silencioso (usado pelo hook automático)
pytest -q
```

---

## Estrutura de Pastas

```text
.
├── AGENTS.md                        # Este arquivo — lido em toda sessão
├── app/
│   ├── __init__.py
│   ├── database.py                  # Conexão SQLite, tabelas e seed
│   ├── schemas.py                   # Schemas Pydantic v2
│   └── main.py                      # Endpoints FastAPI + estáticos
├── static/
│   └── index.html                   # Interface web
├── tests/
│   └── test_events.py               # Testes automatizados
├── mcp_server/
│   └── sqlite_mcp.py                # Servidor MCP local (FastMCP/stdio)
└── .agents/
    ├── rules/
    │   └── fastapi-rules.md         # Regras ativas ao editar app/**/*.py
    ├── skills/
    │   └── criar-endpoint/
    │       └── SKILL.md             # Playbook de criação de endpoints
    ├── agents/
    │   ├── dev-backend.md           # Subagente especialista em implementação
    │   └── qa-reviewer.md           # Subagente revisor somente leitura
    ├── hooks.json                   # Hook determinístico: pytest após edições
    └── mcp_config.json              # Registro do servidor MCP SQLite local
```

---

## Schema do Banco de Dados

> **Regra crítica:** Nunca assuma o schema do banco sem consultar o MCP `sqlite` via `list_tables()` e `describe_table()`. O banco pode evoluir ao longo do workshop.

**Tabela `events`**
- `id` INTEGER PK AUTOINCREMENT
- `title` TEXT NOT NULL
- `speaker` TEXT NOT NULL
- `capacity` INTEGER NOT NULL CHECK (capacity > 0)
- `created_at` TEXT NOT NULL DEFAULT (datetime('now'))

**Tabela `registrations`** *(a ser implementada durante o workshop)*
- `id` INTEGER PK AUTOINCREMENT
- `event_id` INTEGER FK → events(id)
- `participant_name` TEXT NOT NULL
- `participant_email` TEXT NOT NULL
- `created_at` TEXT NOT NULL DEFAULT (datetime('now'))

---

## Convenções do Projeto

- **Tipagem estrita:** Use type hints em todas as funções Python.
- **Pydantic v2:** Schemas em `app/schemas.py`. Use `model_config = ConfigDict(from_attributes=True)`.
- **SQL parametrizado:** Nunca use f-string em queries SQL. Sempre use `?` com parâmetros.
- **Status codes explícitos:** Use constantes de `fastapi.status` (ex.: `status.HTTP_201_CREATED`).
- **Testes isolados:** Cada test fixture usa um banco SQLite temporário via `tmp_path`.

---

## Orquestração Hub-and-Spoke

Ao implementar **novas funcionalidades completas**, siga este fluxo obrigatório:

1. **Consulte o schema atual** via MCP `sqlite` antes de qualquer implementação (`list_tables`, `describe_table`).
2. **Delegue a implementação** ao subagente `dev-backend` (invoque via `invoke_subagent`).
3. **Aguarde a conclusão** e confirme que `pytest` passou (o hook automático garante isso).
4. **Delegue a auditoria** ao subagente `qa-reviewer`, passando o `git diff` como contexto.
5. **Responda ao usuário** apenas após receber o parecer do `qa-reviewer`.

> Para tarefas simples de leitura, exploração ou dúvidas pontuais, o Hub pode responder diretamente sem delegar.
