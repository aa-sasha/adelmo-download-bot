# Telegram Video Downloader Bot

Простой телеграм-бот для скачивания видео из социальных сетей (Instagram, Twitter, TikTok и др.) с использованием `yt-dlp`.

## Особенности
- Скачивание видео по ссылке.
- Использование Docker для стабильной работы.
- Автоматическая очистка временных файлов.
- Простая архитектура на `aiogram 3`.

## Установка и запуск (на сервере)

1. Клонируйте репозиторий.
2. Создайте файл `.env` с вашим токеном:
   ```env
   TELEGRAM_BOT_TOKEN=ваш_токен
   ```
3. Соберите и запустите контейнер:
   ```bash
   docker build -t tg_bot .
   docker run -d --name tg_bot --env-file .env -v $(pwd)/downloads:/app/downloads --restart always tg_bot
   ```

## Лицензия
MIT
