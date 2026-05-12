import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

import claude_client
import conversation
import instrumentation
import supabase_client as db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("maya")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Maya iniciando...")
    yield
    log.info("Maya encerrando.")


app = FastAPI(title="Maya — Agente R&S KPH", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "maya"}


@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()
    telefone: str = form.get("From", "")
    body: str = form.get("Body", "").strip()

    log.info("Mensagem de %s: %s", telefone, body[:80])

    if not telefone or not body:
        resp = MessagingResponse()
        resp.message("Não recebi sua mensagem. Pode tentar de novo?")
        return Response(content=str(resp), media_type="application/xml")

    history = conversation.get_history(telefone)

    t0 = time.monotonic()
    response_text, usage = claude_client.process_message(history, body)
    latency_ms = (time.monotonic() - t0) * 1000

    # Persist turns after successful response
    conversation.append_message(telefone, "user", body)
    conversation.append_message(telefone, "assistant", response_text)

    intencao = instrumentation.detectar_intencao(body)
    metrics = instrumentation.log_turn(
        phone=telefone,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        latency_ms=latency_ms,
        intencao=intencao,
    )

    asyncio.create_task(
        asyncio.to_thread(db.save_metric, {
            "agent": "maya",
            "phone_last4": telefone[-4:],
            **metrics,
        })
    )

    resp = MessagingResponse()
    resp.message(response_text)
    return Response(content=str(resp), media_type="application/xml")
