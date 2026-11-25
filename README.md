
# Desenvolvimento com Agentes de IA na Prática: dos Transformers ao Terminal

Repositório oficial do workshop prático (3h) sobre engenharia de software assistida por agentes de IA via linha de comando (**Antigravity CLI — `agy`**).

O objetivo do minicurso é conectar a base teórica das IAs generativas modernas (embeddings, transformers e LLMs) à prática real de mercado, evoluindo uma aplicação do zero de um simples comando no terminal até uma arquitetura **Hub-and-Spoke** com **Context Engineering**, **Skills**, **Hooks Determinísticos** e **MCP (Model Context Protocol)**.

---

## O que vamos construir

Vamos evoluir um **Gerenciador de Eventos da Semana Acadêmica**, construído propositalmente com uma stack leve e sem build pesado para focarmos 100% na engenharia de agentes:

- **Backend:** Python 3.10+ e FastAPI
- **Banco de Dados:** SQLite local (`app.db`)
- **Frontend:** HTML, CSS e JavaScript puro servido pelo próprio FastAPI
- **Testes:** `pytest` + `httpx`
- **Agente CLI:** Antigravity CLI (`agy`)

A aplicação começa apenas listando e cadastrando eventos. Ao longo do workshop, vamos implementar novas regras de negócio (como **inscrição de participantes com controle de vagas**, **cancelamento** e **auditoria de segurança**) orquestrando agentes especializados.

---

## Roteiro de Desenvolvimento (5 Camadas)

O desenvolvimento é dividido em etapas progressivas para mostrar na prática o papel de cada componente:

| Etapa                               | Conceito Aplicado                                 | O que fazemos no projeto                                                                                                                                                                                                                                         |
| :---------------------------------- | :------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Agente Base**            | Tool Calling e Loop ReAct                         | Exploramos o repositório com o agente "cru" no terminal, observando o ciclo *Pensar → Executar Ferramenta → Observar → Corrigir*.                                                                                                                          |
| **2. Context Engineering**    | `AGENTS.md` e `.agents/rules/`                | Estruturamos as regras fixas do repositório e regras modulares por tipo de arquivo (`globs`) para manter consistência sem poluir a janela de contexto.                                                                                                       |
| **3. Skills**                 | `.agents/skills/*/SKILL.md`                     | Criamos a skill reutilizável `criar-endpoint` com um playbook passo a passo (schema → rota → testes), acionada automaticamente ou via `/criar-endpoint`.                                                                                                  |
| **4. Hooks Determinísticos** | `.agents/hooks.json`                            | Configuramos um hook `PostToolUse` que roda `pytest -q` depois de `write_to_file` e `replace_file_content`. |
| **5. MCP + Hub-and-Spoke**    | `.agents/mcp_config.json` e `.agents/agents/` | Conectamos um servidor **MCP** local ao SQLite e dividimos o trabalho entre o **Hub** (Orquestrador) e dois **Spokes** com contextos isolados: `dev-backend` (implementa) e `qa-reviewer` (audita o `git diff` em modo somente leitura). |

### Arquitetura Hub-and-Spoke do Projeto

```text
                    [ Aluno / Dev ]
                           │
                           ▼
               ┌───────────────────────┐
               │   HUB (Sessão agy)    │  ← Lê AGENTS.md, planeja e consolida
               └─────┬───────────┬─────┘
                     │           │
         invoke_subagent     invoke_subagent
                     │           │
                     ▼           ▼
       ┌──────────────────┐ ┌──────────────────┐
       │ SPOKE: dev-backend│ │ SPOKE: qa-reviewer│
       │ • Skill endpoint │ │ • Contexto limpo │
       │ • MCP SQLite     │ │ • Somente leitura│
       │ • Hook: pytest   │ │ • Audita git diff│
       └──────────────────┘ └──────────────────┘
```

---

## Estrutura de Pastas

```text
.
├── .gitignore
├── AGENTS.md                           # Contexto principal lido em toda sessão
├── dados_exemplo.sql                   # Eventos e inscrições fictícios para a aula
├── README.md
├── requirements.txt
├── task.md                             # Especificação do starter
├── app/
│   ├── __init__.py
│   ├── database.py                     # Conexão SQLite, criação de tabelas e seed
│   ├── schemas.py                      # Modelos de validação Pydantic
│   └── main.py                         # Endpoints FastAPI e servidor de estáticos
├── static/
│   └── index.html                      # Interface web simples
├── tests/
│   ├── __init__.py
│   └── test_events.py                  # Testes automatizados (pytest)
├── mcp_server/
│   └── sqlite_mcp.py                   # Servidor MCP local (FastMCP) para o SQLite
└── .agents/
    ├── rules/
    │   └── fastapi-rules.md            # Regras para arquivos Python em app/
    ├── skills/
    │   └── criar-endpoint/
    │       └── SKILL.md                # Playbook reutilizável de criação de rotas
    ├── agents/
    │   ├── dev-backend.md              # Subagente especialista em implementação
    │   └── qa-reviewer.md              # Subagente revisor (somente leitura)
    ├── hooks.json                      # Automação determinística pós-edição
    └── mcp_config.json                 # Registro do servidor MCP local
```

---

## Pré-requisitos e Setup Rápido

### 1. Clonar o repositório e preparar o Python

```bash
git clone --branch preparacao/workshop https://github.com/MarcosMob/agentes-ia-weekeng.git
cd agentes-ia-weekeng

python3 -m venv .venv
source .venv/bin/activate       # No Windows (Git Bash): source .venv/Scripts/activate

pip install -r requirements.txt
```

O projeto usa o SDK MCP 1.x para manter a API `FastMCP` usada no exercício.

### 2. Validar se o projeto base está funcionando

```bash
# Rodar os testes iniciais
pytest -v

# Subir a aplicação (acesse [http://127.0.0.1:8000](http://127.0.0.1:8000))
uvicorn app.main:app --reload
```

### 3. Iniciar o Antigravity CLI (`agy`)

Com a aplicação iniciada para criar `app.db`, abra um segundo terminal na raiz do projeto, ative a `.venv` e inicie o agente. O servidor MCP usa o `python3` desse ambiente.

```bash
agy
```

### Carregar dados de exemplo

Copie e execute o bloco abaixo na raiz do projeto. Ele inicializa o `app.db` se necessário e aplica `dados_exemplo.sql` com o SQLite do Python.

```bash
python - <<'PY'
from contextlib import closing
from pathlib import Path

from app.database import get_connection, init_db, seed_data

init_db()
seed_data()
with closing(get_connection()) as conn:
    conn.executescript(Path("dados_exemplo.sql").read_text(encoding="utf-8"))
PY
```

Os eventos com prefixo `[Demo]` cobrem três cenários para o exercício de inscrições. Um está lotado, um tem vagas disponíveis e um ainda está sem inscritos. Executar o bloco novamente preserva os dados existentes e evita duplicatas.

---

## Comandos Úteis no `agy` Durante a Aula

- `/usage` — Consulta o uso da cota do modelo.
- `/mcp` — Lista e testa a conexão com o servidor MCP do SQLite.
- `/hooks` — Confere se o grupo `auto-pytest` foi carregado.
- `/criar-endpoint <tarefa>` — Invoca manualmente a Skill de criação de endpoints.
- `/agents` — Abre o painel ao vivo dos subagentes (pressione `Enter` em um Spoke para inspecionar a janela de contexto isolada dele).

No painel `/mcp`, confira se `sqlite` está ativo. Para validar o acesso ao banco, peça ao agente para executar `list_tables` e `describe_table` para `events` e `registrations`.

O `agy` 1.5.17 lê `globs` como texto. O `dev-backend` recebe `sqlite` via `inheritMcp` da configuração do workspace. [Regras do Antigravity](https://antigravity.google/docs/rules-workflows/) · [Configuração de subagentes](https://antigravity.google/docs/build-plugins#subagents)
