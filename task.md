Atue como um engenheiro de software sênior preparando um repositório base para um workshop prático de 3 horas sobre Desenvolvimento com Agentes de IA usando o Antigravity CLI (`agy`).

Crie a estrutura completa de pastas e arquivos abaixo na raiz deste projeto, respeitando rigorosamente os nomes de arquivos, chaves YAML/JSON e nomes de ferramentas do `agy`.

### 1. Aplicação Starter (Gerenciador de Eventos da Semana Acadêmica)

- `requirements.txt`: inclua `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx` e `mcp` (para o servidor MCP local).
- `.gitignore`: ignore `__pycache__/`, `.venv/`, `*.pyc`, `.pytest_cache/` e `app.db`.
- `app/__init__.py`
- `app/database.py`: conexão SQLite nativa (`app.db`) criando automaticamente duas tabelas ao iniciar:
  - `events` (`id`, `title`, `speaker`, `capacity`, `created_at`)
  - `registrations` (`id`, `event_id`, `participant_name`, `participant_email`, `created_at`)
  - Adicione uma função `seed_data()` que insere 2 eventos de exemplo caso a tabela `events` esteja vazia.
- `app/schemas.py`: schemas Pydantic v2 para criação e leitura de eventos (`EventCreate`, `EventResponse`).
- `app/main.py`: aplicação FastAPI que inicializa o banco no lifespan, serve arquivos estáticos de `static/` na rota `/` e implementa apenas 2 endpoints iniciais:
  - `GET /api/events` (lista todos os eventos)
  - `POST /api/events` (cria um evento retornando HTTP 201)
    *(Deixe propositalmente de fora os endpoints de inscrição e cancelamento, pois eles serão desenvolvidos ao vivo com os agentes).*
- `static/index.html`: interface simples, limpa e responsiva em HTML/CSS/JS puro que lista os eventos via `fetch('/api/events')` e permite cadastrar um novo evento.
- `tests/test_events.py`: 2 testes básicos usando `TestClient` do FastAPI validando `GET /api/events` e `POST /api/events` com um banco temporário isolado.

### 2. Servidor MCP Local (SQLite)

- `mcp_server/sqlite_mcp.py`: servidor MCP minimalista (~40 linhas) usando `FastMCP` da biblioteca oficial `mcp`, operando via `stdio` e expondo 3 tools somente leitura/inspeção para o banco `./app.db`:
  - `list_tables()`: retorna as tabelas existentes no SQLite.
  - `describe_table(table_name: str)`: retorna as colunas e tipos via `PRAGMA table_info`.
  - `run_readonly_query(query: str)`: executa apenas queries `SELECT` (bloqueando `INSERT`, `UPDATE`, `DELETE`, `DROP` ou `ALTER`).

### 3. Arquitetura Padrão Antigravity CLI (`.agents/` e `AGENTS.md`)

Crie os seguintes arquivos de contexto, regras, skills, hooks, MCP e subagentes:

- `AGENTS.md` (na raiz):

  - Documente a stack (Python, FastAPI, SQLite, HTML/JS), comandos (`uvicorn app.main:app --reload`, `pytest -v`), estrutura de pastas e convenções do projeto.
  - Inclua a seção **Orquestração (Hub-and-Spoke)** instruindo o agente principal (Hub) a:
    1. Nunca assumir o schema do banco sem consultar o MCP `sqlite`.
    2. Para novas funcionalidades completas, delegar a implementação ao subagente `dev-backend` e, em seguida, delegar a auditoria de `git diff` ao subagente `qa-reviewer` antes de responder ao usuário.
- `.agents/rules/fastapi-rules.md`:

  - Frontmatter YAML com `description` e `globs: ["app/**/*.py"]`.
  - Regras curtas: usar tipagem estrita, Pydantic v2, queries SQL parametrizadas (nunca f-string em SQL) e status codes explícitos do `fastapi.status`.
- `.agents/skills/criar-endpoint/SKILL.md`:

  - Frontmatter YAML com `name: criar-endpoint` e `description` clara para ativação automática e manual (`/criar-endpoint`).
  - Passos obrigatórios: inspecionar schema via MCP `sqlite` → criar/atualizar schemas em `app/schemas.py` → implementar rota em `app/main.py` (ou router dedicado) → escrever no mínimo 2 testes (sucesso e erro/edge case) em `tests/` → rodar `pytest -v`.
- `.agents/agents/dev-backend.md`:

  - Frontmatter YAML com:
    - `name: dev-backend`
    - `description`: especialista em implementação backend FastAPI + SQLite + testes.
    - `subagent: true`
    - `tools: ["view_file", "write_to_file", "replace_file_content", "grep_search", "find_by_name", "run_command"]`
    - `skills: ["criar-endpoint"]`
    - `mcpServers: ["sqlite"]`
  - Corpo com instruções objetivas para implementar a subtarefa recebida do Hub, garantir `pytest` verde e devolver apenas um resumo estruturado dos arquivos alterados e resultados.
- `.agents/agents/qa-reviewer.md`:

  - Frontmatter YAML com:
    - `name: qa-reviewer`
    - `description`: revisor de código, segurança e edge cases com contexto isolado e acesso somente leitura.
    - `subagent: true`
    - `tools: ["view_file", "grep_search", "run_command"]`
  - Corpo instruindo a rodar `git diff` via `run_command`, auditar SQL injection, validação de capacidade/concorrência, códigos HTTP e testes, sem editar nenhum arquivo, devolvendo um parecer estruturado (Aprovado / Ajustes Necessários).
- `.agents/hooks.json`:

  - Configure um hook `PostToolUse` com `matcher: "write_to_file|replace_file_content"` que executa `pytest -q` automaticamente após edições.
- `.agents/mcp_config.json`:

  - Configure o servidor `sqlite` apontando para o script local:
    - `command`: `"python3"` (ou o executável do `.venv` se preferir indicar no comentário do README)
    - `args`: `["mcp_server/sqlite_mcp.py"]`

Ao final, crie o ambiente virtual `.venv`, instale as dependências do `requirements.txt`, rode `pytest -v` para confirmar que os testes iniciais passam e me mostre a árvore final de arquivos criada.
