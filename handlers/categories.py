from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from handlers.start import start_handler
from utils.decorators import safe_handler
from database.crud import add_category, get_categories, soft_delete_category, get_category_name_by_id
from translations import ru
from utils.keyboards import make_inline_keyboard
from utils.middlewares import send_and_store, retrieve_stored_data, delete_trash_messages, delete_starting_message

router = Router()


class CategoryState(StatesGroup):
    entering_name = State()
    deleting_by_name = State()


@router.message(lambda msg: msg.text == ru.CATEGORIES)
@safe_handler
async def start_categories(message: types.Message, state: FSMContext):

    await delete_starting_message(message, state)

    keyboard = make_inline_keyboard([
        [(ru.CATEGORIES_SHOW_CATEGORIES, "show_categories")],
        [(ru.CATEGORIES_ADD_CATEGORY, "add_category")],
        [(ru.CATEGORIES_DELETE_CATEGORY, "delete_category")],
        [(ru.BUTTON_BACK, "back_to_main")]
    ])
    await send_and_store(message=message,
                         text=ru.CHOOSE_ACTION,
                         state=state,
                         reply_markup=keyboard)


@router.callback_query(F.data == "show_categories")
@safe_handler
async def show_categories(callback: types.CallbackQuery):
    categories = get_categories()
    if not categories:
        await callback.message.edit_text(ru.CATEGORIES_NO_ACTIVE_CATEGORIES)
        return
    text = "\n".join([f"- {c.name}" for c in categories])
    await callback.message.edit_text(f"{ru.CATEGORIES}:\n{text}")


@router.callback_query(F.data == "add_category")
@safe_handler
async def add_category_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CategoryState.entering_name)
    bot_msg_ids = await retrieve_stored_data(state, 'tracked_messages')
    bot_msg_ids.append(callback.message.message_id)
    await state.update_data(bot_msg_ids=bot_msg_ids)
    await callback.message.edit_text(ru.CATEGORIES_CHOOSE_CATEGORY_NAME)


@router.message(CategoryState.entering_name)
@safe_handler
async def add_category_entering_name(message: types.Message, state: FSMContext):
    name = message.text
    category = add_category(name)

    await message.delete()
    await delete_trash_messages(message, state)

    await message.answer(ru.CATEGORIES_ADDED.format(category.name))
    await state.clear()


@router.callback_query(F.data == "delete_category")
@safe_handler
async def delete_category_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CategoryState.deleting_by_name)

    bot_msg_ids = await retrieve_stored_data(state, 'tracked_messages')
    bot_msg_ids.append(callback.message.message_id)

    sources = get_categories()

    if len(sources) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.CATEGORIES_NO_ACTIVE_CATEGORIES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(s.name, f"delete-category_{s.id}")] for s in sources
    ])

    await callback.message.edit_text(ru.CATEGORIES_CHOOSE_CATEGORY_NAME, reply_markup=keyboard)


@router.callback_query(F.data.startswith("delete-category_"))
@safe_handler
async def delete_category_by_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    category_id = int(callback.data.split("_")[1])
    deleted_name = get_category_name_by_id(category_id)
    if soft_delete_category(category_id):
        await callback.message.edit_text(ru.CATEGORIES_DELETED.format(deleted_name))
        await state.clear()
        # await start_handler(message, state)
    else:
        await callback.message.edit_text(ru.CATEGORIES_NOT_FOUND)
