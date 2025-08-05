from functools import wraps
from aiogram.types import Message
from translations import ru


def safe_handler(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        try:
            return await func(message, *args, **kwargs)
        except Exception as e:
            await message.answer(f'\n{e or ru.ERROR_COMMON}')
            print(f"Error in {func.__name__}: {e}")
    return wrapper
