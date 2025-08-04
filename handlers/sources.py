from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.decorators import safe_handler
from database.crud import add_source, get_sources, soft_delete_source
from config import DEFAULT_CURRENCY
from translations import ru

router = Router()


class SourceState(StatesGroup):
    entering_name = State()
    deleting_by_id = State()


@router.message(lambda msg: msg.text == ru.SOURCES)
@safe_handler
async def show_sources(message: types.Message):
    sources = get_sources()
    if not sources:
        await message.answer(ru.SOURCES_NO_ACTIVE_SOURCES)
        return
    text = "\n".join([f"{s.name} ({s.currency})" for s in sources])
    await message.answer(f"{ru.SOURCES}:\n{text}")


@router.message(lambda msg: msg.text == ru.SOURCES_ADD_SOURCE)
@safe_handler
async def add_source_handler(message: types.Message, state: FSMContext):
    await state.set_state(SourceState.entering_name)
    await message.answer(ru.SOURCES_CHOOSE_SOURCE_NAME)


# TODO: Обработать ошибку "Такое имя уже существует"
@router.message(SourceState.entering_name)
@safe_handler
async def add_source_entering_name(message: types.Message, state: FSMContext):
    parts = message.text
    name = parts
    currency = DEFAULT_CURRENCY
    source = add_source(name, currency)
    await message.answer(ru.SOURCES_ADDED.format(source.name))
    await state.clear()


# TODO: Изменить на ввод из меню (по тексту)
@router.message(lambda msg: msg.text == ru.SOURCES_DELETE_SOURCE)
@safe_handler
async def delete_source_handler(message: types.Message):
    name = message.text.split(maxsplit=1)[1]
    if soft_delete_source(name):
        await message.answer(ru.SOURCES_DELETED.format(name))
    else:
        await message.answer(ru.SOURCES_NOT_FOUND)
