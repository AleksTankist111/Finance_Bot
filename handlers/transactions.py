from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from utils.decorators import safe_handler
from utils.currency import parse_amount_currency
from utils.middlewares import send_and_store
from database.crud import get_sources, get_categories, add_transaction, delete_transaction
from handlers.start import start_handler
from translations import ru

router = Router()


class TransactionState(StatesGroup):
    choosing_type = State()
    choosing_source = State()
    choosing_category = State()
    entering_amount = State()
    entering_comment = State()
    deleting_by_id = State()


@router.message(lambda msg: msg.text == ru.TRANSACTIONS)
@safe_handler
async def start_transactions(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.TRANSACTIONS_SHOW_TRANSACTIONS)], #TODO
        [types.KeyboardButton(text=ru.TRANSACTIONS_ADD_TRANSACTION)],
        [types.KeyboardButton(text=ru.TRANSACTIONS_DELETE_TRANSACTION)],
        [types.KeyboardButton(text=ru.BUTTON_BACK)]
    ])
    await message.answer(ru.CHOOSE_ACTION, reply_markup=keyboard)


@router.message(lambda msg: msg.text == ru.TRANSACTIONS_ADD_TRANSACTION)
@safe_handler
async def start_add_transaction(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text=ru.TRANSACTIONS_TYPE_INCOME)],
        [types.KeyboardButton(text=ru.TRANSACTIONS_TYPE_OUTCOME)]
    ])
    await state.set_state(TransactionState.choosing_type)
    await send_and_store(message=message,
                         text=ru.TRANSACTIONS_CHOOSE_TYPE,
                         state=state,
                         reply_markup=keyboard)


@router.message(TransactionState.choosing_type, F.text.in_({ru.TRANSACTIONS_TYPE_INCOME, ru.TRANSACTIONS_TYPE_OUTCOME}))
@safe_handler
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(is_income=(message.text == ru.TRANSACTIONS_TYPE_INCOME))
    sources = get_sources()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
        keyboard=[[types.KeyboardButton(text=s.name)] for s in sources])
    await state.set_state(TransactionState.choosing_source)
    await send_and_store(message=message,
                         text=ru.TRANSACTIONS_CHOOSE_SOURCE,
                         state=state,
                         reply_markup=keyboard)


@router.message(TransactionState.choosing_source)
@safe_handler
async def choose_source(message: types.Message, state: FSMContext):
    sources = get_sources()
    source = next((s for s in sources if s.name == message.text), None)
    if not source:
        await message.answer(ru.SOURCES_NOT_FOUND)
        return
    await state.update_data(source_id=source.id)
    categories = get_categories()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
        keyboard=[[types.KeyboardButton(text=c.name)] for c in categories])
    await state.set_state(TransactionState.choosing_category)
    await send_and_store(message=message,
                            text=ru.TRANSACTIONS_CHOOSE_CATEGORY,
                            state=state,
                            reply_markup=keyboard)


@router.message(TransactionState.choosing_category)
@safe_handler
async def choose_category(message: types.Message, state: FSMContext):
    categories = get_categories()
    category = next((c for c in categories if c.name == message.text), None)
    if not category:
        await message.answer(ru.CATEGORIES_NOT_FOUND)
        return
    await state.update_data(category_id=category.id)
    await state.set_state(TransactionState.entering_amount)
    await send_and_store(message=message,
                            text=ru.TRANSACTIONS_WRITE_SUM,
                            state=state,
                            reply_markup=ReplyKeyboardRemove())


@router.message(TransactionState.entering_amount)
@safe_handler
async def enter_amount(message: types.Message, state: FSMContext):
    try:
        amount, currency = parse_amount_currency(message.text)
        await state.update_data(amount=amount, currency=currency)
        await state.set_state(TransactionState.entering_comment)
        await send_and_store(message=message,
                                text=ru.TRANSACTIONS_WRITE_COMMENT,
                                state=state)
    except ValueError:
        await message.answer(ru.ERROR_WRONG_TRANSACTION_FORMAT)


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
    final_msg = await message.answer(
        ru.TRANSACTIONS_TRANSACTION_ADDED.format(transaction.id) +
        ru.TRANSACTIONS_TRANSACTION_ADDED_TYPE.format(
                ru.TRANSACTIONS_TYPE_INCOME if transaction.is_income else ru.TRANSACTIONS_TYPE_OUTCOME) +
        ru.TRANSACTIONS_TRANSACTION_ADDED_SOURCE.format(transaction.source.name) +
        ru.TRANSACTIONS_TRANSACTION_ADDED_CATEGORY.format(transaction.category.name) +
        ru.TRANSACTIONS_TRANSACTION_ADDED_AMOUNT.format(transaction.amount, transaction.currency) +
        ru.TRANSACTIONS_TRANSACTION_ADDED_COMMENT.format(transaction.comment or '—') +
        ru.TRANSACTIONS_TRANSACTION_ADDED_DATE.format(transaction.date.strftime('%Y-%m-%d %H:%M'))
    )

    data = await state.get_data()
    tracked = data.get("tracked_messages", [])
    for msg_id in tracked:
        if msg_id != final_msg.message_id:
            await message.chat.delete_message(msg_id)

    await state.clear()
    await start_handler(message)


@router.message(lambda msg: msg.text == ru.TRANSACTIONS_DELETE_TRANSACTION)
@safe_handler
async def delete_transaction_handler(message: types.Message, state: FSMContext):
    await state.set_state(TransactionState.deleting_by_id)
    await message.answer(ru.TRANSACTIONS_WRITE_TRANSACTION_ID)


@router.message(TransactionState.deleting_by_id)
@safe_handler
async def delete_transaction_by_id(message: types.Message, state: FSMContext):
    try:
        transaction_id = int(message.text)
        if delete_transaction(transaction_id):
            await message.answer(ru.TRANSACTIONS_DELETED.format(transaction_id))
        else:
            await message.answer(ru.TRANSACTIONS_NOT_FOUND)
        await state.clear()
    except Exception:
        await message.answer(ru.ERROR_WRONG_FORMAT)
