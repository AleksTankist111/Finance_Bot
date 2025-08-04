from aiogram import Router, types
from aiogram.filters import CommandStart
from translations import ru

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.TRANSACTIONS)],
        [types.KeyboardButton(text=ru.SOURCES), types.KeyboardButton(text=ru.CATEGORIES)],
        [types.KeyboardButton(text=ru.STATISTICS), types.KeyboardButton(text=ru.PLANNING)],
        [types.KeyboardButton(text=ru.EXPORT_EXCEL)],
        [types.KeyboardButton(text=ru.FAMILY)]
    ])
    await message.answer(ru.STARTING_MESSAGE, reply_markup=keyboard)


@router.message(lambda msg: msg.text == ru.BUTTON_BACK)
async def show_sources(message: types.Message):
    await message.delete()
    await start_handler(message)
