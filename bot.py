# bot.py

import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import all_routers

import os

PORT = int(os.getenv("PORT", 10000))


# ===== Мини веб-сервер для Render =====
async def handle(request):
    return web.Response(text="✅ Bot is running!")


async def run_web_server():
    """Запускаем простой HTTP сервер чтобы Render не ругался"""
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Web server started on port {PORT}")


# ===== Основной бот =====
async def run_bot():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await init_db()
    logger.info("✅ База данных инициализирована")

    for router in all_routers:
        dp.include_router(router)
    logger.info(f"✅ Загружено {len(all_routers)} роутеров")

    logger.info("🤖 Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    # Запускаем веб-сервер И бота одновременно
    await asyncio.gather(
        run_web_server(),
        run_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
