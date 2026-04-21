# Job Tracker — Telegram Mini App

## Структура проекта
```
job-tracker/
├── main.py          # FastAPI бэкенд + Google Sheets API
├── bot.py           # Telegram Bot webhook
├── templates/
│   └── app.html     # Mini App (фронтенд)
├── static/          # Статичные файлы (если нужны)
├── requirements.txt
└── railway.toml     # Конфиг деплоя
```

## Переменные окружения (Railway)
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SHEET_ID=1bXnGtl1a_ojF8X0FSt-HRAuilI0zbc5WRFFi6mKFeIU
BOT_TOKEN=...
APP_URL=https://your-app.railway.app
REDIRECT_URI=https://your-app.railway.app/callback
```

## Деплой на Railway
1. Залей код на GitHub
2. Создай проект на railway.app → Deploy from GitHub
3. Добавь переменные окружения
4. После деплоя скопируй URL и обнови APP_URL и REDIRECT_URI
5. Добавь REDIRECT_URI в Google OAuth (Authorized redirect URIs)
6. Открой APP_URL в браузере → авторизуйся через Google
7. В Telegram найди своего бота → /start → открой трекер

## Google Sheet
Лист называется "Отклики", заголовки в строке 1:
| A        | B         | C        | D          | E       | F     |
|----------|-----------|----------|------------|---------|-------|
| Компания | Должность | Зарплата | Прочитано  | Статус  | Дата  |
