from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from translations import ru
from utils.decorators import safe_handler

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, state:FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.TRANSACTIONS)],
        [types.KeyboardButton(text=ru.SOURCES), types.KeyboardButton(text=ru.CATEGORIES)],
        [types.KeyboardButton(text=ru.STATISTICS), types.KeyboardButton(text=ru.PLANNING)],
        [types.KeyboardButton(text=ru.EXPORT_EXCEL)],
        [types.KeyboardButton(text=ru.FAMILY)]
    ])

    msg = await message.answer(ru.STARTING_MESSAGE, reply_markup=keyboard)
    await state.update_data(start_bot_message_id=msg.message_id)


@router.callback_query(F.data == "back_to_main")
@safe_handler
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    data = await state.get_data()
    tracked = data.get("tracked_messages", [])
    for msg_id in tracked:
        try:
            await callback.message.chat.delete_message(msg_id)
        except Exception:
            pass

    # Удаляем inline-клавиатуру
    await callback.message.delete()

    # Показываем стартовое меню с обычной клавиатурой
    await start_handler(callback.message, state)