import os
import httpx
from fastapi import APIRouter, Request

router = APIRouter()

BOT_TOKEN = os.environ["BOT_TOKEN"]
APP_URL   = os.environ["APP_URL"]  # https://your-app.railway.app

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text    = message.get("text", "")

    if not chat_id:
        return {"ok": True}

    if text in ["/start", "/open"]:
        await send_message(chat_id, "Открываю трекер 👇", reply_markup={
            "inline_keyboard": [[{
                "text": "📋 Открыть Job Tracker",
                "web_app": {"url": APP_URL}
            }]]
        })
    else:
        await send_message(chat_id, "Нажми /start чтобы открыть трекер")

    return {"ok": True}

async def set_webhook(app_url: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/setWebhook", json={
            "url": f"{app_url}/webhook"
        })
