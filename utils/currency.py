import re
from config import DEFAULT_CURRENCY
from translations import ru


def parse_amount_currency(text: str):
    data = text.split()
    if len(data) < 1 or len(data) > 2:
        raise ValueError(ru.ERROR_WRONG_TRANSACTION_FORMAT)
    else:
        amount = float(data[0])
        currency = data[1] if len(data) == 2 else DEFAULT_CURRENCY
        return amount, currency

