from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable, Awaitable, Dict, Any


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
