-- Dados fictícios para exercitar inscrições e controle de vagas.
-- Execute com as tabelas do projeto já criadas.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

WITH exemplos(title, speaker, capacity) AS (
    VALUES
        ('[Demo] Primeiros passos com FastAPI', 'Marina Costa', 1),
        ('[Demo] Consultas SQLite com MCP', 'Rafael Lima', 4),
        ('[Demo] Revisão de código com agentes', 'Luiza Rocha', 8)
)
INSERT INTO events (title, speaker, capacity)
SELECT exemplo.title, exemplo.speaker, exemplo.capacity
FROM exemplos AS exemplo
WHERE NOT EXISTS (
    SELECT 1 FROM events AS evento
    WHERE evento.title = exemplo.title AND evento.speaker = exemplo.speaker
);

-- Uma inscrição por evento deixa um evento lotado e outro com vagas.
WITH exemplos(title, speaker, participant_name, participant_email) AS (
    VALUES
        ('[Demo] Primeiros passos com FastAPI', 'Marina Costa', 'Camila Exemplo', 'camila.workshop@example.org'),
        ('[Demo] Consultas SQLite com MCP', 'Rafael Lima', 'Bruno Exemplo', 'bruno.workshop@example.org')
)
INSERT INTO registrations (event_id, participant_name, participant_email)
SELECT evento.id, exemplo.participant_name, exemplo.participant_email
FROM exemplos AS exemplo
JOIN events AS evento ON evento.id = (
    SELECT MIN(id) FROM events
    WHERE title = exemplo.title AND speaker = exemplo.speaker
)
WHERE NOT EXISTS (
    SELECT 1 FROM registrations AS inscricao
    WHERE inscricao.event_id = evento.id
      AND inscricao.participant_email = exemplo.participant_email
)
AND evento.capacity > (
    SELECT COUNT(*) FROM registrations AS inscricao
    WHERE inscricao.event_id = evento.id
);

COMMIT;
