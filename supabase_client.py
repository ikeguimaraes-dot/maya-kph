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
    # Normalize: strip 'whatsapp:' prefix for storage comparison
    phone_clean = telefone.replace("whatsapp:", "")
    response = (
        sb.table("candidates")
        .select("id, nome, status, area_interesse, cargo_interesse")
        .or_(f"telefone.eq.{telefone},telefone.eq.{phone_clean}")
        .limit(1)
        .execute()
    )
    data = response.data
    return data[0] if data else None


def criar_candidato(
    nome: str,
    telefone: str,
    area_interesse: str,
    cargo_interesse: str,
) -> str:
    sb = get_client()
    phone_clean = telefone.replace("whatsapp:", "")
    response = (
        sb.table("candidates")
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
    sb.table("candidates").update({"status": status}).eq("id", candidate_id).execute()
