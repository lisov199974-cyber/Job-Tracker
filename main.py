from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
from datetime import datetime
from contextlib import asynccontextmanager
from bot import router as bot_router, set_webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_url = os.environ.get("APP_URL", "")
    if app_url:
        await set_webhook(app_url)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(bot_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GOOGLE_CLIENT_ID     = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
SHEET_ID             = os.environ["SHEET_ID"]
REDIRECT_URI         = os.environ["REDIRECT_URI"]

SCOPES = "https://www.googleapis.com/auth/spreadsheets"
token_store = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if "access_token" not in token_store:
        return RedirectResponse("/login")
    return templates.TemplateResponse("app.html", {"request": request})

@app.get("/login")
async def login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url)

@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        })
    data = resp.json()
    token_store["access_token"]  = data["access_token"]
    token_store["refresh_token"] = data.get("refresh_token")
    return RedirectResponse("/")

async def refresh_access_token():
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": token_store.get("refresh_token"),
            "grant_type": "refresh_token",
        })
    token_store["access_token"] = resp.json()["access_token"]

@app.get("/api/entries")
async def get_entries():
    if "access_token" not in token_store:
        raise HTTPException(401, "Not authenticated")
    token = token_store["access_token"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Отклики!A2:F",
            headers={"Authorization": f"Bearer {token}"}
        )
    if resp.status_code == 401:
        await refresh_access_token()
        return await get_entries()
    rows = resp.json().get("values", [])
    entries = []
    for r in rows:
        while len(r) < 6:
            r.append("")
        entries.append({
            "company": r[0], "role": r[1], "salary": r[2],
            "read": r[3], "status": r[4], "date": r[5]
        })
    return JSONResponse(entries)

@app.post("/api/entries")
async def add_entry(request: Request):
    if "access_token" not in token_store:
        raise HTTPException(401, "Not authenticated")
    body = await request.json()
    token = token_store["access_token"]
    row = [[
        body.get("company", ""),
        body.get("role", ""),
        body.get("salary", ""),
        body.get("read", "Нет"),
        body.get("status", "Без ответа"),
        datetime.now().strftime("%d.%m.%Y"),
    ]]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Отклики!A:F:append"
            f"?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"values": row}
        )
    if resp.status_code == 401:
        await refresh_access_token()
        return await add_entry(request)
    return JSONResponse({"ok": True})
