from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.decorators import safe_handler
from utils.currency import parse_amount_currency
from database.crud import get_sources, get_categories, add_transaction, delete_transaction
from handlers.start import start_handler

router = Router()


class TransactionState(StatesGroup):
    choosing_type = State()
    choosing_source = State()
    choosing_category = State()
    entering_amount = State()
    entering_comment = State()
    deleting_by_id = State()

@router.message(lambda msg: msg.text == "➕ Добавить транзакцию")
@safe_handler
async def start_transaction(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="Доход")],
        [types.KeyboardButton(text="Расход")]
    ])
    await state.set_state(TransactionState.choosing_type)
    await message.answer("Выберите тип транзакции:", reply_markup=keyboard)

@router.message(TransactionState.choosing_type, F.text.in_({"Доход", "Расход"}))
@safe_handler
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(is_income=(message.text == "Доход"))
    sources = get_sources()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
        keyboard=[[types.KeyboardButton(text=s.name)] for s in sources])
    await state.set_state(TransactionState.choosing_source)
    await message.answer("Выберите источник:", reply_markup=keyboard)

@router.message(TransactionState.choosing_source)
@safe_handler
async def choose_source(message: types.Message, state: FSMContext):
    sources = get_sources()
    source = next((s for s in sources if s.name == message.text), None)
    if not source:
        await message.answer("Источник не найден.")
        return
    await state.update_data(source_id=source.id)
    categories = get_categories()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
        keyboard=[[types.KeyboardButton(text=c.name)] for c in categories])
    await state.set_state(TransactionState.choosing_category)
    await message.answer("Выберите категорию:", reply_markup=keyboard)

@router.message(TransactionState.choosing_category)
@safe_handler
async def choose_category(message: types.Message, state: FSMContext):
    categories = get_categories()
    category = next((c for c in categories if c.name == message.text), None)
    if not category:
        await message.answer("Категория не найдена.")
        return
    await state.update_data(category_id=category.id)
    await state.set_state(TransactionState.entering_amount)
    await message.answer("Введите сумму (например: 118.86 RSD):")

@router.message(TransactionState.entering_amount)
@safe_handler
async def enter_amount(message: types.Message, state: FSMContext):
    try:
        amount, currency = parse_amount_currency(message.text)
        await state.update_data(amount=amount, currency=currency)
        await state.set_state(TransactionState.entering_comment)
        await message.answer("Введите комментарий (можно оставить пустым):")
    except ValueError:
        await message.answer("Неверный формат. Пример: 118.86 RSD")

@router.message(TransactionState.entering_comment)
@safe_handler
async def enter_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    transaction = add_transaction(
        amount=data["amount"],
        currency=data["currency"],
        is_income=data["is_income"],
        source_id=data["source_id"],
        category_id=data["category_id"],
        comment=message.text
    )
    await message.answer(
        f"✅ Транзакция {transaction.id} добавлена:\n"
        f"Тип: {'Доход' if transaction.is_income else 'Расход'}\n"
        f"Источник: {transaction.source.name}\n"
        f"Категория: {transaction.category.name}\n"
        f"Комментарий: {transaction.comment or '—'}\n"
        f"Дата: {transaction.date.strftime('%Y-%m-%d %H:%M')}"
    )
    await state.clear()
    await start_handler(message)


@router.message(lambda msg: msg.text == "❌ Удалить транзакцию")
@safe_handler
async def delete_transaction_handler(message: types.Message, state: FSMContext):
    await state.set_state(TransactionState.deleting_by_id)
    await message.answer("Введите id транзакции:")


@router.message(TransactionState.deleting_by_id)
@safe_handler
async def delete_transaction_by_id(message: types.Message, state: FSMContext):
    try:
        transaction_id = int(message.text)
        if delete_transaction(transaction_id):
            await message.answer(f"Транзакция {transaction_id} удалена.")
        else:
            await message.answer("Транзакция не найдена.")
        await state.clear()
    except Exception:
        await message.answer("Неверный формат.")
