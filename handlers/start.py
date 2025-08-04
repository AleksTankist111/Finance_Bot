from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

# TODO: добавить остальные действия
# TODO: Перенести имена в отдельный файл и заменить на переменные
@router.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="➕ Добавить транзакцию")],
        [types.KeyboardButton(text="📊 Показать статистику")],
        [types.KeyboardButton(text="🧾 Вывести транзакции"), types.KeyboardButton(text="📤 Экспорт в Excel")],
        [types.KeyboardButton(text="💼 Источники"), types.KeyboardButton(text="📁 Категории")],
        [types.KeyboardButton(text="➕💼 Добавить Источники"), types.KeyboardButton(text="➕📁 Добавить Категории")],
        [types.KeyboardButton(text="❌💼 Удалить Источники"), types.KeyboardButton(text="❌📁 Удалить Категории")],
        [types.KeyboardButton(text="❌ Удалить транзакцию")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)
