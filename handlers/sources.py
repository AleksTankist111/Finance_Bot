from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.start import start_handler
from utils.decorators import safe_handler
from database.crud import add_source, get_sources, soft_delete_source, get_source_amounts
from translations import ru
from config import DEFAULT_CURRENCY


router = Router()


class SourceState(StatesGroup):
    entering_name = State()
    deleting_by_name = State()


@router.message(lambda msg: msg.text == ru.SOURCES)
@safe_handler
async def start_sources(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.SOURCES_SHOW_SOURCES)],
        [types.KeyboardButton(text=ru.SOURCES_ADD_SOURCE)],
        [types.KeyboardButton(text=ru.SOURCES_DELETE_SOURCE)],
        [types.KeyboardButton(text=ru.BUTTON_BACK)]
    ])
    await message.answer(ru.CHOOSE_ACTION, reply_markup=keyboard)


@router.message(lambda msg: msg.text == ru.SOURCES_SHOW_SOURCES)
@safe_handler
async def show_sources(message: types.Message):
    sources = get_source_amounts()
    if not sources:
        await message.answer(ru.SOURCES_NO_ACTIVE_SOURCES)
        return
    text = "\n".join([f"{name}: {amount} ({DEFAULT_CURRENCY})" for name, amount in sources])
    await message.answer(f"{ru.SOURCES}:\n{text}")


@router.message(lambda msg: msg.text == ru.SOURCES_ADD_SOURCE)
@safe_handler
async def add_source_handler(message: types.Message, state: FSMContext):
    await state.set_state(SourceState.entering_name)
    await message.answer(ru.SOURCES_CHOOSE_SOURCE_NAME)


@router.message(SourceState.entering_name)
@safe_handler
async def add_source_entering_name(message: types.Message, state: FSMContext):
    parts = message.text
    name = parts
    source = add_source(name)
    await message.answer(ru.SOURCES_ADDED.format(source.name))
    await state.clear()


@router.message(lambda msg: msg.text == ru.SOURCES_DELETE_SOURCE)
@safe_handler
async def delete_source_handler(message: types.Message, state: FSMContext):
    await state.set_state(SourceState.deleting_by_name)
    await message.answer(ru.SOURCES_CHOOSE_SOURCE_NAME)


@router.message(SourceState.deleting_by_name)
@safe_handler
async def delete_source_by_name(message: types.Message, state: FSMContext):
    name = message.text
    if soft_delete_source(name):
        await message.answer(ru.SOURCES_DELETED.format(name))
        await state.clear()
        await start_handler(message)
    else:
        await message.answer(ru.SOURCES_NOT_FOUND)
