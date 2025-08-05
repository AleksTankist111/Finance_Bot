from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, transactions, sources, categories, stats
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

    dp.message.middleware(MessageTrackingMiddleware())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


# TODO: При ошибке с добавлением дубликата имени, выводить ошибку в чат.
# TODO: Чекнуть, что state.clear() выполняется после errors и везде где нужно
# TODO: решить проблему с записью названий операций в БД как имена
# TODO: добавить остальные действия
# TODO: Добавить планирование на месяц (установить ожидаемое значение трат на выбранную категорию) (доходы не учитываются!)
# TODO: После добавления планирования, добавление транзакции должно сопровождаться ещё одной информационной строкой на каждый план - сколько осталось (абсолют, и в процентах, а также средняя скорость трат в день)
# TODO: Добавить security через user-id, чтоб другой чел не мог вывести чужую информацию
# TODO: Добавить функцию "добавить в семью", чтоб другой человек мог быть добавлен в группу и работать с финансами семьи
# TODO: Добавить хендлер мусорных сообщений
# TODO: Вывести общий экран планирования
# TODO: Ввести функицю "Повторить" план для категории
# TODO: Поиск транзакций по тегам (в описании) ????
# TODO: Вынести логику start handler в отдельную комнату чтобы при завершении действия вызывать её, а не start handler - тогда приветственное сообщение не будет выводиться
# TODO: Перед удалением спрашивать "точно хотите удалить?" и для источников написать в этом соо "все средства с этого источника будут удалены"
# TODO: Заменить на inline keyboards
# TODO: в каждой финальной сцене добавить соо со ссылкой на старт (или автоматически перейти на старт но по умолчанию скрыть меню в трее)
# TODO: Для удаления кошелька или категории, выведи лист и выбирай из них через inline keyboard
# TODO: Заменить удаление функцией