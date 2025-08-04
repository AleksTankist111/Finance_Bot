from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, transactions, sources, categories, stats
from database.db import init_db
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


    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



# TODO: Донастроить существующие функции
# TODO: Добавить планирование на месяц (установить ожидаемое значение трат на выбранную категорию) (доходы не учитываются!)
# TODO: После добавления планирования, добавление транзакции должно сопровождаться ещё одной информационной строкой на каждый план - сколько осталось (абсолют, и в процентах, а также средняя скорость трат в день)
