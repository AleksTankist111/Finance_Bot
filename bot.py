from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, transactions, sources, categories, stats, trash
from database.db import init_db
from utils.middlewares import MessageTrackingMiddleware
import asyncio


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хендлеров
    dp.include_router(start.router)
    dp.include_router(transactions.router)
    dp.include_router(sources.router)
    dp.include_router(categories.router)
    dp.include_router(stats.router)




    dp.include_router(trash.router)  # Trash messages router (SHOULD BE THE LAST)
    dp.message.middleware(MessageTrackingMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

