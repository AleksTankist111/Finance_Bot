from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from handlers.start import start_handler
from utils.decorators import safe_handler
from database.crud import add_source, get_sources, soft_delete_source, get_source_amounts, get_source_name_by_id
from translations import ru
from config import DEFAULT_CURRENCY
from utils.keyboards import make_inline_keyboard
from utils.middlewares import send_and_store, delete_trash_messages, retrieve_stored_data, delete_starting_message

router = Router()


class SourceState(StatesGroup):
    entering_name = State()
    deleting_by_name = State()


@router.message(lambda msg: msg.text == ru.SOURCES)
@safe_handler
async def start_sources(message: types.Message, state: FSMContext):

    # Очистка истории сообщений от мусора (вход в ветку "Кошелек")
    await delete_starting_message(message, state)

    keyboard = make_inline_keyboard([
        [(ru.SOURCES_SHOW_SOURCES, "show_sources")],
        [(ru.SOURCES_ADD_SOURCE, "add_source")],
        [(ru.SOURCES_DELETE_SOURCE, "delete_source")],
        [(ru.BUTTON_BACK, "back_to_main")]
    ])
    await send_and_store(message=message,
                         text=ru.CHOOSE_ACTION,
                         state=state,
                         reply_markup=keyboard)


@router.callback_query(F.data == "show_sources")
@safe_handler
async def show_sources(callback: types.CallbackQuery):
    await callback.answer()
    sources = get_source_amounts()
    if not sources:
        await callback.message.edit_text(ru.SOURCES_NO_ACTIVE_SOURCES)
        return
    text = "\n".join([f"{name}: {amount} ({DEFAULT_CURRENCY})" for name, amount in sources])
    await callback.message.edit_text(f"{ru.SOURCES}:\n{text}")


@router.callback_query(F.data == "add_source")
@safe_handler
async def add_source_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SourceState.entering_name)
    bot_msg_ids = await retrieve_stored_data(state, 'tracked_messages')
    bot_msg_ids.append(callback.message.message_id)
    await state.update_data(bot_msg_ids=bot_msg_ids)
    await callback.message.edit_text(ru.SOURCES_CHOOSE_SOURCE_NAME)


@router.message(SourceState.entering_name)
@safe_handler
async def add_source_entering_name(message: types.Message, state: FSMContext):
    name = message.text
    source = add_source(name)

    await message.delete()
    await delete_trash_messages(message, state)

    await message.answer(ru.SOURCES_ADDED.format(source.name))
    await state.clear()


@router.callback_query(F.data == "delete_source")
@safe_handler
async def delete_source_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SourceState.deleting_by_name)
    bot_msg_ids = await retrieve_stored_data(state, 'tracked_messages')
    bot_msg_ids.append(callback.message.message_id)
    await state.update_data(bot_msg_ids=bot_msg_ids)

    sources = get_sources()

    if len(sources) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.SOURCES_NO_ACTIVE_SOURCES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(s.name, f"delete-source_{s.id}")] for s in sources
    ])

    await callback.message.edit_text(ru.SOURCES_CHOOSE_SOURCE_NAME, reply_markup=keyboard)


@router.callback_query(F.data.startswith("delete-source_"))
@safe_handler
async def delete_source_by_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    source_id = int(callback.data.split("_")[1])
    deleted_name = get_source_name_by_id(source_id)
    if soft_delete_source(source_id):
        await callback.message.edit_text(ru.SOURCES_DELETED.format(deleted_name))
        await state.clear()
        #await start_handler(message, state)
    else:
        await callback.message.edit_text(ru.SOURCES_NOT_FOUND)
