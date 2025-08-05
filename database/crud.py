from database.db import SessionLocal
from database.models import Source, Category, Transaction
from translations import ru
from sqlalchemy import func

session = SessionLocal()


def get_sources():
    return session.query(Source).filter_by(is_deleted=False).all()


def get_categories():
    return session.query(Category).filter_by(is_deleted=False).all()


def get_source_name_by_id(source_id: int) -> str:
    source = session.query(Source).filter(Source.id == source_id, Source.is_deleted == False).first()
    return source.name if source else "—"


def is_name_exist(table, name: str) -> bool:
    return session.query(table).filter(
        table.name == name,
        table.is_deleted == False
    ).first() is not None


def is_name_exist_in_source(name: str) -> bool:
    return is_name_exist(Source, name)


def is_name_exist_in_category(name: str) -> bool:
    return is_name_exist(Category, name)


def get_source_amounts():
    results = session.query(
        Source.name,
        func.coalesce(func.sum(Transaction.amount), 0).label("amount_sum")
    ).outerjoin(Transaction, Source.id == Transaction.source_id)\
     .filter(Source.is_deleted == False)\
     .group_by(Source.name)\
     .all()
    return results


def add_source(name):
    if is_name_exist_in_source(name):
        raise Exception(ru.ERROR_NAME_EXIST)
    source = Source(name=name)
    session.add(source)
    session.commit()
    return source


def add_category(name):
    if is_name_exist_in_category(name):
        raise Exception(ru.ERROR_NAME_EXIST)
    category = Category(name=name)
    session.add(category)
    session.commit()
    return category


def add_transaction(amount, currency, is_income, source_id, category_id, comment):
    transaction = Transaction(
        amount=amount if is_income else -amount,
        currency=currency,
        is_income=is_income,
        source_id=source_id,
        category_id=category_id,
        comment=comment
    )
    session.add(transaction)
    session.commit()
    return transaction


def delete_transaction(transaction_id):
    transaction = session.query(Transaction).get(transaction_id)
    if transaction:
        session.delete(transaction)
        session.commit()
        return True
    return False


def soft_delete_source(id):
    source = session.query(Source).filter_by(id=id, is_deleted=False).first()
    if source:
        source.is_deleted = True
        session.commit()
        return True
    return False

def soft_delete_category(name):
    category = session.query(Category).filter_by(name=name, is_deleted=False).first()
    if category:
        category.is_deleted = True
        session.commit()
        return True
    return False


def get_transactions():
    return session.query(Transaction).all()


def get_limit_transactions(limit=20):
    return session.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
