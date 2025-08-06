from aiogram import BaseMiddleware
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from typing import Callable, Awaitable, Dict, Any, Mapping

from translations import ru


class MessageTrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")
        if state is not None:
            state_data = await state.get_data()
            tracked = state_data.get("tracked_messages", [])
            tracked.append(event.message_id)
            await state.update_data(tracked_messages=tracked)

        return await handler(event, data)


async def send_and_store(message: Message, text: str, state: FSMContext, key: str = 'tracked_messages', **kwargs):
    bot_msg = await message.answer(text, **kwargs)
    data = await state.get_data()
    bot_msg_ids = data.get(key, [])
    bot_msg_ids.append(bot_msg.message_id)
    await state.update_data(bot_msg_ids=bot_msg_ids)
    return bot_msg


async def retrieve_stored_data(state: FSMContext, option: str) -> Any:
    data = await state.get_data()
    return data.get(option, [])


async def delete_trash_messages(message: Message, state: FSMContext, exceptions: tuple[int] = ()):
    tracked = await retrieve_stored_data(state, 'tracked_messages')
    for msg_id in tracked:
        if msg_id not in exceptions:
            try:
                await message.chat.delete_message(msg_id)
            except Exception:
                pass


async def delete_starting_message(message, state):
    await message.delete()
    m_remove_keyboard = await message.answer(ru.WAIT, reply_markup=ReplyKeyboardRemove())
    await m_remove_keyboard.delete()
    last_msg_id = await retrieve_stored_data(state, "start_bot_message_id")
    if last_msg_id:
        try:
            await message.chat.delete_message(last_msg_id)
        except Exception:
            pass  # сообщение могло быть уже удалено


