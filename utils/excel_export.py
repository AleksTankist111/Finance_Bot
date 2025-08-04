import pandas as pd
from database.db import SessionLocal
from database.models import Transaction
from translations import ru
import os


def export_transactions_to_excel(path="transactions.xlsx"):
    session = SessionLocal()
    transactions = session.query(Transaction).all()
    data = [{
        "ID": t.id,
        "Amount": t.amount,
        "Currency": t.currency,
        "Type": ru.TRANSACTIONS_TYPE_INCOME if t.is_income else ru.TRANSACTIONS_TYPE_OUTCOME,
        "Source": t.source.name,
        "Category": t.category.name,
        "Comment": t.comment,
        "Date": t.date.strftime("%Y-%m-%d %H:%M")
    } for t in transactions]

    df = pd.DataFrame(data)
    if os.path.exists(path):
        os.remove(path)
    df.to_excel(path, index=False)
    return path
