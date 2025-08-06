from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from utils.decorators import safe_handler
from utils.currency import parse_amount_currency
from utils.keyboards import make_inline_keyboard
from utils.middlewares import send_and_store, delete_trash_messages, retrieve_stored_data
from database.crud import get_sources, get_categories, add_transaction, delete_transaction, get_limit_transactions, \
    get_category_id_by_name, get_source_name_by_id
from handlers.start import start_handler, back_to_main
from translations import ru
from tabulate import tabulate

router = Router()


class TransactionState(StatesGroup):
    choosing_type = State()
    choosing_source = State()
    choosing_category = State()
    entering_amount = State()
    entering_comment = State()
    deleting_by_id = State()
    transfer_amount = State()


@router.message(lambda msg: msg.text == ru.TRANSACTIONS)
@safe_handler
async def start_transactions(message: types.Message, state: FSMContext):

    # Очистка истории сообщений от мусора (вход в ветку "Транзакция")
    await message.delete()
    m_remove_keyboard = await message.answer(ru.STARTING_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await m_remove_keyboard.delete()
    last_msg_id = await retrieve_stored_data(state, "start_bot_message_id")
    if last_msg_id:
        try:
            await message.chat.delete_message(last_msg_id)
        except Exception:
            pass  # сообщение могло быть уже удалено

    keyboard = make_inline_keyboard([
        [(ru.TRANSACTIONS_SHOW_TRANSACTIONS, "show_transactions")],
        [(ru.TRANSACTIONS_ADD_TRANSACTION, "add_transaction")],
        [(ru.TRANSACTIONS_DELETE_TRANSACTION, "delete_transaction")],
        [(ru.BUTTON_BACK, "back_to_main")]
    ])
    await send_and_store(message=message,
                         text=ru.CHOOSE_ACTION,
                         state=state,
                         reply_markup=keyboard)


@router.callback_query(F.data == "add_transaction")
@safe_handler
async def start_add_transaction(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    keyboard = make_inline_keyboard([
        [(ru.TRANSACTIONS_TYPE_INCOME, "type_income")],
        [(ru.TRANSACTIONS_TYPE_OUTCOME, "type_outcome")],
        [(ru.TRANSACTIONS_TYPE_TRANSFER, "type_transfer")]
    ])
    await state.set_state(TransactionState.choosing_type)
    bot_msg_ids = await retrieve_stored_data(state, 'tracked_messages')
    bot_msg_ids.append(callback.message.message_id)
    await state.update_data(bot_msg_ids=bot_msg_ids)
    await callback.message.edit_text(ru.TRANSACTIONS_CHOOSE_TYPE, reply_markup=keyboard)


@router.callback_query(F.data.in_({"type_income", "type_outcome"}))
@safe_handler
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    is_income = callback.data == "type_income"
    await state.update_data(is_income=is_income)

    sources = get_sources()

    if len(sources) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.ERROR_NO_SOURCES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(s.name, f"add-source_{s.id}")] for s in sources
    ])
    await state.set_state(TransactionState.choosing_source)
    await callback.message.edit_text(ru.TRANSACTIONS_CHOOSE_SOURCE, reply_markup=keyboard)


@router.callback_query(F.data.startswith("add-source_"))
@safe_handler
async def choose_source(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    source_id = int(callback.data.split("_")[1])
    await state.update_data(source_id=source_id)

    categories = get_categories()

    if len(categories) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.ERROR_NO_CATEGORIES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(c.name, f"add-category_{c.id}")] for c in categories
    ])
    await state.set_state(TransactionState.choosing_category)
    await callback.message.edit_text(ru.TRANSACTIONS_CHOOSE_CATEGORY, reply_markup=keyboard)


@router.callback_query(F.data.startswith("add-category_"))
@safe_handler
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)

    await state.set_state(TransactionState.entering_amount)
    await callback.message.edit_text(ru.TRANSACTIONS_WRITE_SUM)


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

    await delete_trash_messages(message, state, exceptions=(final_msg.message_id,))

    await state.clear()
    await start_handler(message, state)


@router.callback_query(F.data == "delete_transaction")
@safe_handler
async def delete_transaction_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TransactionState.deleting_by_id)
    await callback.message.edit_text(ru.TRANSACTIONS_WRITE_TRANSACTION_ID)


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


@router.callback_query(F.data == "show_transactions")
@safe_handler
async def show_transaction_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    data = get_limit_transactions(20)
    formatted = []
    for tx in data:
        formatted.append({
            "ID": tx.id,
            "SUM": f"{tx.amount:.2f} ({tx.currency})",
            "Type": ru.TRANSACTIONS_TYPE_INCOME if tx.is_income else ru.TRANSACTIONS_TYPE_OUTCOME,
            "Source": tx.source.name if tx.source else "—",
            "Category": tx.category.name if tx.category else "—",
            "Comment": tx.comment or "",
            "Date": tx.date.strftime("%Y-%m-%d %H:%M"),
        })

    headers = ["ID", "Sum", "Type", "Source", "Category", "Comment", "Date"]
    rows = [[
        tx["ID"], tx["SUM"], tx["Type"], tx["Source"],
        tx["Category"], tx["Comment"], tx["Date"]
    ] for tx in formatted]

    table = tabulate(rows, headers=headers, tablefmt="grid")
    table_text = f"<pre>{table}</pre>"

    await callback.message.edit_text(table_text, parse_mode="HTML")


@router.callback_query(F.data == "type_transfer")
@safe_handler
async def transaction_transfer_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    sources = get_sources()

    if len(sources) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.ERROR_NO_SOURCES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(s.name, f"transfer-from-source_{s.id}")] for s in sources
    ])
    await callback.message.edit_text(ru.TRANSACTIONS_TYPE_TRANSFER_FROM, reply_markup=keyboard)


@router.callback_query(F.data.startswith == "transfer-from-source_")
@safe_handler
async def transaction_transfer_from_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    from_source_id = int(callback.data.split("_")[1])
    await state.update_data(from_source_id=from_source_id)
    sources = get_sources()

    if len(sources) == 0:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(ru.ERROR_NO_SOURCES)
        # await back_to_main(callback, state)
        return

    keyboard = make_inline_keyboard([
        [(s.name, f"transfer-to-source_{s.id}")] for s in sources
    ])
    await callback.message.edit_text(ru.TRANSACTIONS_TYPE_TRANSFER_TO, reply_markup=keyboard)


@router.callback_query(F.data.startswith == "transfer-to-source_")
@safe_handler
async def transaction_transfer_from_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    to_source_id = int(callback.data.split("_")[1])
    await state.update_data(to_source_id=to_source_id)

    await state.set_state(TransactionState.transfer_amount)
    await callback.message.edit_text(ru.TRANSACTIONS_WRITE_SUM)


@router.message(TransactionState.transfer_amount)
@safe_handler
async def enter_amount(message: types.Message, state: FSMContext):
    try:
        amount, currency = parse_amount_currency(message.text)
        data = await state.get_data()
        from_source_id = data["from_source_id"]
        to_source_id = data["to_source_id"]

        transfer_category_id = get_category_id_by_name(ru.TRANSACTIONS_TYPE_TRANSFERS) #TODO replace when user added
        to_source_name = get_source_name_by_id(to_source_id)
        from_source_name = get_source_name_by_id(from_source_id)

        transaction_from = add_transaction(
            amount=amount,
            currency=currency,
            is_income=False,
            source_id=from_source_id,
            category_id=transfer_category_id,
            comment=ru.TRANSFER_FROM_TO.format(from_source_name, to_source_name)
        )

        transaction_to = add_transaction(
            amount=amount,
            currency=currency,
            is_income=True,
            source_id=to_source_id,
            category_id=transfer_category_id,
            comment=ru.TRANSFER_FROM_TO.format(from_source_name, to_source_name)
        )

        await delete_trash_messages(message, state)

        await message.answer(ru.TRANSFER_COMPLETED.format(from_source_name,
                                                          to_source_name,
                                                          amount,
                                                          currency,
                                                          transaction_from.id,
                                                          transaction_to.id))

    except ValueError:
        await message.answer(ru.ERROR_WRONG_TRANSACTION_FORMAT)
