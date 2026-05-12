import json
import os
import anthropic
from tools import MAYA_TOOLS
import supabase_client as db

MODEL = "claude-sonnet-4-6"
MAX_TOOL_ITERATIONS = 8

SYSTEM_PROMPT = open(
    os.path.join(os.path.dirname(__file__), "system_prompt.txt"),
    encoding="utf-8",
).read()

_anthropic = anthropic.Anthropic()


def _execute_tool(name: str, input_data: dict) -> str:
    try:
        if name == "buscar_vagas_abertas":
            vagas = db.buscar_vagas_abertas(input_data.get("area"))
            if not vagas:
                return "Nenhuma vaga aberta encontrada para essa área no momento."
            linhas = []
            for v in vagas:
                salario = v.get("salario_base") or "a combinar"
                linhas.append(f"- {v['title']} | Salário: {salario} | Must-have: {v.get('must_have', '')}")
            return "\n".join(linhas)

        elif name == "buscar_candidato_por_telefone":
            candidato = db.buscar_candidato_por_telefone(input_data["telefone"])
            if not candidato:
                return "Candidato não encontrado."
            return json.dumps(candidato, ensure_ascii=False)

        elif name == "criar_candidato":
            candidate_id = db.criar_candidato(
                nome=input_data["nome"],
                telefone=input_data["telefone"],
                area_interesse=input_data["area_interesse"],
                cargo_interesse=input_data["cargo_interesse"],
            )
            return json.dumps({"candidate_id": candidate_id, "status": "novo"})

        elif name == "atualizar_status_candidato":
            db.atualizar_status_candidato(
                candidate_id=input_data["candidate_id"],
                status=input_data["status"],
            )
            return f"Status atualizado para '{input_data['status']}'."

        else:
            return f"Tool '{name}' não reconhecida."

    except Exception as exc:
        return f"Erro ao executar {name}: {exc}"


def process_message(history: list[dict], user_text: str) -> tuple[str, dict]:
    """Returns (reply_text, usage) where usage has input_tokens and output_tokens
    accumulated across all tool-loop iterations."""
    messages = list(history)
    messages.append({"role": "user", "content": user_text})

    total_input = 0
    total_output = 0
    response = None

    for _ in range(MAX_TOOL_ITERATIONS):
        response = _anthropic.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # Cache the system prompt — it's large and stable across all requests
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=MAYA_TOOLS,
            messages=messages,
        )

        total_input += response.usage.input_tokens
        total_output += response.usage.output_tokens

        # Append assistant turn to messages
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    return block.text, {"input_tokens": total_input, "output_tokens": total_output}
            return "Olá! Pode me falar mais?", {"input_tokens": total_input, "output_tokens": total_output}

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    result = _execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    for block in (response.content if response else []):
        if hasattr(block, "type") and block.type == "text":
            return block.text, {"input_tokens": total_input, "output_tokens": total_output}
    return "Desculpe, tive um problema interno. Pode repetir?", {"input_tokens": total_input, "output_tokens": total_output}
