# Telegram бот курса валют
Бот для получения курса валют (USD, EUR, RUB, AMD, CNY). Работает в асинхронном режиме.

## Настройка
Создайте `.env` с токенами:
```bash
TELEGRAM_TOKEN=ваш_telegram_token
API_TOKEN=ваш_openexchangerates_token
MINI_APP_URL=https://<ваш-логин>.github.io/<репозиторий>/
```

## Запуск
Локально:
```bash
poetry install
poetry run python rates.py
```

Docker:
```bash
docker compose up --build -d
```

## GitHub Pages (мини-приложение)
В репозитории есть статическая страница с конвертером валют в `app/`.

Как включить GitHub Pages:
1. Запушьте репозиторий на GitHub.
2. Откройте Settings -> Pages.
3. В Source выберите "Deploy from a branch".
4. Branch: `main`, Folder: `/app`.
5. Сохраните и дождитесь адреса сайта.

Локальный просмотр:
```bash
python -m http.server 8000
```
и откройте `http://localhost:8000/app/`.

## API токен в мини-приложении
Страница в `app/` запрашивает курсы напрямую у openexchangerates.org.
Токен зашит в `app/app.js` (переменная `apiToken`) и будет публичным.
Ссылка для кнопки бота берется из `MINI_APP_URL` в `.env`.
