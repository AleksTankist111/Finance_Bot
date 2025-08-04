from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.decorators import safe_handler
from database.crud import add_source, get_sources, soft_delete_source
from config import DEFAULT_CURRENCY

router = Router()

class SourceState(StatesGroup):
    entering_name = State()
    deleting_by_id = State()

@router.message(lambda msg: msg.text == "💼 Источники")
@safe_handler
async def show_sources(message: types.Message):
    sources = get_sources()
    if not sources:
        await message.answer("Нет активных источников.")
        return
    text = "\n".join([f"{s.name} ({s.currency})" for s in sources])
    await message.answer(f"💼 Источники:\n{text}")


@router.message(lambda msg: msg.text == "➕💼 Добавить Источники")
@safe_handler
async def add_source_handler(message: types.Message, state: FSMContext):
    await state.set_state(SourceState.entering_name)
    await message.answer("Введите название кошелька:")


# TODO: Обработать ошибку "Такое имя уже существует"
@router.message(SourceState.entering_name)
@safe_handler
async def add_source_entering_name(message: types.Message, state: FSMContext):
    parts = message.text
    name = parts
    currency = DEFAULT_CURRENCY
    source = add_source(name, currency)
    await message.answer(f"Источник '{source.name}' добавлен.")
    await state.clear()


# TODO: Изменить на ввод из меню (по тексту)
@router.message(lambda msg: msg.text.startswith("/delete_source"))
@safe_handler
async def delete_source_handler(message: types.Message):
    name = message.text.split(maxsplit=1)[1]
    if soft_delete_source(name):
        await message.answer(f"Источник '{name}' помечен как удалённый.")
    else:
        await message.answer("Источник не найден.")
