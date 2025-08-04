import pandas as pd
from database.db import SessionLocal
from database.models import Transaction


def export_transactions_to_excel(path="transactions.xlsx"):
    session = SessionLocal()
    transactions = session.query(Transaction).all()
    data = [{
        "ID": t.id,
        "Amount": t.amount,
        "Currency": t.currency,
        "Type": "Доход" if t.is_income else "Расход",
        "Source": t.source.name,
        "Category": t.category.name,
        "Comment": t.comment,
        "Date": t.date.strftime("%Y-%m-%d %H:%M")
    } for t in transactions]

    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return path
