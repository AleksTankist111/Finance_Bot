from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from utils.decorators import safe_handler
from utils.excel_export import export_transactions_to_excel
from translations import ru
from utils.keyboards import make_inline_keyboard
from utils.middlewares import retrieve_stored_data, send_and_store, delete_starting_message

router = Router()


@router.message(lambda msg: msg.text == ru.STATISTICS)
@safe_handler
async def show_statistics_menu(message: types.Message, state: FSMContext):

    await delete_starting_message(message, state)

    keyboard = make_inline_keyboard([
        [(ru.STATISTICS_SHOW_STATISTICS, "show_statistics")],
        [(ru.BUTTON_BACK, "back_to_main")]
    ])
    await send_and_store(message=message,
                         text=ru.CHOOSE_ACTION,
                         state=state,
                         reply_markup=keyboard)


@router.message(lambda msg: msg.text == ru.EXPORT_EXCEL)
@safe_handler
async def export_excel(message: types.Message, state: FSMContext):

    await delete_starting_message(message, state)

    path = export_transactions_to_excel()
    await message.answer_document(types.FSInputFile(path), caption=ru.EXPORT_EXCEL)

