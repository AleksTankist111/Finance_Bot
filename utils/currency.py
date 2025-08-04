import re
from config import DEFAULT_CURRENCY


def parse_amount_currency(text: str):
    match = re.match(r"([\d.]+)\s*([A-Z]{3})?", text.strip())
    if match:
        amount = float(match.group(1))
        currency = match.group(2) or DEFAULT_CURRENCY
        return amount, currency
    raise ValueError("Неверный формат суммы. Пример: '118.86 RSD' или '118.86'")
