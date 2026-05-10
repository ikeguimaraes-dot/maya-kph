from threading import Lock

_conversations: dict[str, list[dict]] = {}
_lock = Lock()

MAX_MESSAGES = 20


def get_history(telefone: str) -> list[dict]:
    with _lock:
        return list(_conversations.get(telefone, []))


def append_message(telefone: str, role: str, content) -> None:
    with _lock:
        history = _conversations.setdefault(telefone, [])
        history.append({"role": role, "content": content})
        if len(history) > MAX_MESSAGES:
            # Remove oldest pair to keep context coherent
            _conversations[telefone] = history[-MAX_MESSAGES:]


def clear_history(telefone: str) -> None:
    with _lock:
        _conversations.pop(telefone, None)
