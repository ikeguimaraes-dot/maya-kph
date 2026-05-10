MAYA_TOOLS = [
    {
        "name": "buscar_vagas_abertas",
        "description": (
            "Busca as vagas abertas no banco de dados do KPH. "
            "Use quando o candidato perguntar sobre vagas disponíveis ou quiser saber opções de cargo numa área. "
            "Filtre por área se o candidato já escolheu uma (cozinha, bar, salão, administrativo)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {
                    "type": "string",
                    "description": (
                        "Área para filtrar as vagas. "
                        "Valores possíveis: 'cozinha', 'bar', 'salão', 'administrativo'. "
                        "Omita para retornar todas as áreas."
                    ),
                }
            },
            "required": [],
        },
    },
    {
        "name": "buscar_candidato_por_telefone",
        "description": (
            "Verifica se já existe um candidato cadastrado com esse telefone. "
            "Use no início de toda conversa nova para evitar duplicatas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "telefone": {
                    "type": "string",
                    "description": "Número de telefone no formato recebido pelo Twilio, ex: 'whatsapp:+5511999999999'",
                }
            },
            "required": ["telefone"],
        },
    },
    {
        "name": "criar_candidato",
        "description": (
            "Cria um novo candidato no banco de dados após coletar nome, área e cargo de interesse. "
            "Use somente quando tiver nome, telefone, área_interesse e cargo_interesse confirmados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome completo do candidato"},
                "telefone": {
                    "type": "string",
                    "description": "Telefone no formato Twilio, ex: 'whatsapp:+5511999999999'",
                },
                "area_interesse": {
                    "type": "string",
                    "description": "Área de interesse: 'cozinha', 'bar', 'salão' ou 'administrativo'",
                },
                "cargo_interesse": {
                    "type": "string",
                    "description": "Cargo específico de interesse, ex: 'Garçom', 'Cozinheiro'",
                },
            },
            "required": ["nome", "telefone", "area_interesse", "cargo_interesse"],
        },
    },
    {
        "name": "atualizar_status_candidato",
        "description": (
            "Atualiza o status de um candidato no banco de dados. "
            "Use para avançar o candidato no funil após cada etapa confirmada. "
            "Status possíveis: 'novo', 'triagem', 'entrevista', 'aprovado', 'reprovado', 'desistiu'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "UUID do candidato retornado por criar_candidato ou buscar_candidato_por_telefone",
                },
                "status": {
                    "type": "string",
                    "enum": ["novo", "triagem", "entrevista", "aprovado", "reprovado", "desistiu"],
                    "description": "Novo status do candidato",
                },
            },
            "required": ["candidate_id", "status"],
        },
    },
]
