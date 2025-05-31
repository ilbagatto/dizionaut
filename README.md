# Dizionaut

**Dizionaut** is a Telegram bot for translating words and expressions using the [Glosbe API](https://glosbe.com/).

The project is written in Python with `aiogram` and supports two execution modes:

* `poll` — for local development,
* `webhook` — for production deployment.

---

## Getting Started

### 1. Install dependencies

```bash
poetry install
```

### 2. Create `.env` file

```dotenv
TELEGRAM_TOKEN=your_token_here
WEBHOOK_URL=https://your.domain.com
MODE=poll  # or webhook
```

### 3. Run the bot

```bash
PYTHONPATH=src poetry run python -m dizionaut.main
```

---

## Tech Stack

* Python 3.10+
* [aiogram](https://docs.aiogram.dev/)
* [httpx](https://www.python-httpx.org/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [aiohttp](https://docs.aiohttp.org/)
* [loguru](https://github.com/Delgan/loguru) — for structured logging

---

## Production Deployment

### 1. Export dependencies

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

### 2. Install via pip

```bash
pip install -r requirements.txt
```

---

## Notes

* HTTPS is required for webhook mode (e.g. via nginx + certbot).
* Telegram must be able to access your webhook URL publicly.

---

MIT Licensed.
