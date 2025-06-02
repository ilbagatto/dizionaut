import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiohttp import web
from dotenv import load_dotenv

from .logger import logger
from .handlers import translate, start, errors, success



load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
MODE = os.getenv("MODE", "poll")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(translate.router)
dp.include_router(start.router)
dp.include_router(errors.router)
dp.include_router(success.router)

# Webhook handlers
async def webhook_handler(request: web.Request):
    data = await request.json
    # Convert raw JSON to Update object and feed it into the dispatcher
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL + "/webhook")

async def on_shutdown(app):
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

def run_webhook():
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=8080)

async def run_polling():
    # Disable webhook to switch to polling mode
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info(f"Running in {MODE!r} mode")
    if MODE == "webhook":
        logger.info("Starting webhook server...")
        run_webhook()
    else:
        logger.info("Starting polling...")
        asyncio.run(run_polling())
