import re
from config import DEFAULT_CURRENCY
from translations import ru


# TODO: упростить
def parse_amount_currency(text: str):
    match = re.match(r"([\d.]+)\s*([A-Z]{3})?", text.strip())
    if match:
        amount = float(match.group(1))
        currency = match.group(2) or DEFAULT_CURRENCY
        return amount, currency
    raise ValueError(ru.ERROR_WRONG_TRANSACTION_FORMAT)
