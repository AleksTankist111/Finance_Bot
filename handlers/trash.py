from aiogram import types, Router
from aiogram.filters import StateFilter
from translations import ru

router = Router()


@router.message(StateFilter(None))
async def trash_message_handler(message: types.Message):

    known_buttons = {ru.TRANSACTIONS,
                     ru.CATEGORIES,
                     ru.SOURCES,
                     ru.STATISTICS,
                     ru.PLANNING,
                     ru.EXPORT_EXCEL,
                     ru.FAMILY,
                     }
    if message.text not in known_buttons:
        await message.answer(ru.ERROR_NOT_RECOGNIZED_COMMAND)
