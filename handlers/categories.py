from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.decorators import safe_handler
from database.crud import add_category, get_categories, soft_delete_category
from translations import ru


router = Router()


class CategoryState(StatesGroup):
    entering_name = State()
    deleting_by_id = State()


@router.message(lambda msg: msg.text == ru.CATEGORIES_SHOW_CATEGORIES)
@safe_handler
async def show_categories(message: types.Message):
    categories = get_categories()
    if not categories:
        await message.answer(ru.CATEGORIES_NO_ACTIVE_CATEGORIES)
        return
    text = "\n".join([f"- {c.name}" for c in categories])
    await message.answer(f"{ru.CATEGORIES}:\n{text}")


@router.message(lambda msg: msg.text == ru.CATEGORIES_ADD_CATEGORY)
@safe_handler
async def add_category_handler(message: types.Message, state: FSMContext):
    await state.set_state(CategoryState.entering_name)
    await message.answer(ru.CATEGORIES_CHOOSE_CATEGORY_NAME)


# TODO: Обработать ошибку "Такое имя уже существует"
@router.message(CategoryState.entering_name)
@safe_handler
async def add_category_entering_name(message: types.Message, state: FSMContext):
    parts = message.text
    name = parts
    category = add_category(name)
    await message.answer(ru.CATEGORIES_ADDED.format(category.name))
    await state.clear()


# TODO: Изменить на ввод из меню (по тексту)
@router.message(lambda msg: msg.text == ru.CATEGORIES_DELETE_CATEGORY)
@safe_handler
async def delete_category_handler(message: types.Message):
    name = message.text.split(maxsplit=1)[1]
    if soft_delete_category(name):
        await message.answer(ru.CATEGORIES_DELETED.format(name))
    else:
        await message.answer(ru.CATEGORIES_NOT_FOUND)
