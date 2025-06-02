
"""
Main module for handling Telegram bot updates via polling or webhook.

This script initializes the bot, sets up update handling, and routes incoming
Telegram updates to the appropriate FSM (finite state machine) logic.
"""
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


async def webhook_handler(request: web.Request):
    """
    Handle incoming webhook requests from Telegram.

    Parses the incoming JSON payload into an Update object and dispatches it.

    Args:
        request (web.Request): Incoming HTTP POST request.

    Returns:
        web.Response: Simple "OK" response.
    """    
    data = await request.json
    # Convert raw JSON to Update object and feed it into the dispatcher
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def on_startup(_):
    """
    Called when the aiohttp app starts.

    Sets the Telegram webhook.
    """    
    logger.info("Starting up...")
    await bot.set_webhook(WEBHOOK_URL + "/webhook")

async def on_shutdown(app):
    """
    Called when the aiohttp app shuts down.

    Deletes the webhook and closes the bot session.
    """    
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

def run_webhook():
    """
    Run the aiohttp server to handle Telegram webhooks.
    """    
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=8080)

async def run_polling():
    """
    Run the bot in long polling mode.
    """    
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
