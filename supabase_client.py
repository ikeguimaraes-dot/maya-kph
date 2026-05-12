import os
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


def buscar_vagas_abertas(area: str | None = None) -> list[dict]:
    sb = get_client()
    query = (
        sb.table("job_openings")
        .select("id, title, unit_id, salario_base, sla_dias, must_have")
        .eq("status", "open")
    )
    if area:
        # title contains the area keyword (case-insensitive handled at DB level)
        query = query.ilike("title", f"%{area}%")
    response = query.order("created_at", desc=True).execute()
    return response.data or []


def buscar_candidato_por_telefone(telefone: str) -> dict | None:
    sb = get_client()
    phone_clean = telefone.replace("whatsapp:", "").strip()
    # Two separate queries to avoid '+' encoding issues in PostgREST .or_()
    for phone in (phone_clean, f"whatsapp:{phone_clean}"):
        response = (
            sb.table("candidatos_maya")
            .select("id, nome, status, area_interesse, cargo_interesse")
            .eq("telefone", phone)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
    return None


def criar_candidato(
    nome: str,
    telefone: str,
    area_interesse: str,
    cargo_interesse: str,
) -> str:
    sb = get_client()
    phone_clean = telefone.replace("whatsapp:", "").strip()
    response = (
        sb.table("candidatos_maya")
        .insert(
            {
                "nome": nome,
                "telefone": phone_clean,
                "area_interesse": area_interesse,
                "cargo_interesse": cargo_interesse,
                "status": "novo",
                "source": "whatsapp",
            }
        )
        .execute()
    )
    return response.data[0]["id"]


def atualizar_status_candidato(candidate_id: str, status: str) -> None:
    sb = get_client()
    sb.table("candidatos_maya").update({"status": status}).eq("id", candidate_id).execute()


def save_metric(data: dict) -> None:
    try:
        row = {k: v for k, v in data.items() if k != "timestamp"}
        get_client().table("agent_metrics").insert(row).execute()
    except Exception as exc:
        import logging
        logging.getLogger("maya.metrics").warning("Falha ao salvar métrica: %s", exc)
