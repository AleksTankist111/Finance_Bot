from aiogram import Router, types
from aiogram.filters import CommandStart
from translations import ru

router = Router()

# TODO: добавить остальные действия
# TODO: Перенести имена в отдельный файл и заменить на переменные
@router.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.TRANSACTIONS)],
        [types.KeyboardButton(text=ru.SOURCES), types.KeyboardButton(text=ru.CATEGORIES)],
        [types.KeyboardButton(text=ru.STATISTICS), types.KeyboardButton(text=ru.EXPORT_EXCEL)],
        [types.KeyboardButton(text=ru.PLANNING)],
        [types.KeyboardButton(text=ru.FAMILY)]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)
