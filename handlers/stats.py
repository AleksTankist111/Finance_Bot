from aiogram import Router, types
from utils.decorators import safe_handler
from utils.excel_export import export_transactions_to_excel
from translations import ru

router = Router()

@router.message(lambda msg: msg.text == ru.EXPORT_EXCEL)
@safe_handler
async def export_excel(message: types.Message):
    path = export_transactions_to_excel()
    await message.answer_document(types.FSInputFile(path), caption=ru.EXPORT_EXCEL)


@router.message(lambda msg: msg.text == ru.TRANSACTIONS_SHOW_TRANSACTIONS)
@safe_handler
async def show_transactions(message: types.Message):
    from database.crud import get_transactions
    transactions = get_transactions()
    if not transactions:
        await message.answer(ru.TRANSACTIONS_NO_TRANSACTIONS)
