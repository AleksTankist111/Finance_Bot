from functools import wraps
from aiogram.types import Message


def safe_handler(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        try:
            return await func(message, *args, **kwargs)
        except Exception as e:
            await message.answer("Произошла ошибка. Попробуйте позже.")
            print(f"Error in {func.__name__}: {e}")
    return wrapper
