-- Rodar no Supabase SQL Editor do KPH OS
-- Compartilhado entre Maya, Theo e Serena (campo agent discrimina)

CREATE TABLE IF NOT EXISTS agent_metrics (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  agent        TEXT        NOT NULL,
  phone_last4  TEXT,
  input_tokens INT,
  output_tokens INT,
  cost_usd     NUMERIC(10,6),
  latency_ms   INT,
  intencao     TEXT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS agent_metrics_agent_created
  ON agent_metrics(agent, created_at DESC);
