from database.db import SessionLocal
from database.models import Source, Category, Transaction

session = SessionLocal()


# TODO: forbid creating source with same name as existing not deleted ones
# TODO: remove currency
def add_source(name, currency="RSD"):
    source = Source(name=name, currency=currency)
    session.add(source)
    session.commit()
    return source

# TODO: forbid creating source with same name as existing not deleted ones
def add_category(name):
    category = Category(name=name)
    session.add(category)
    session.commit()
    return category

def get_sources():
    return session.query(Source).filter_by(is_deleted=False).all()

def get_categories():
    return session.query(Category).filter_by(is_deleted=False).all()

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

# TODO: Fix bug when create new source with the same name is deleted;
def soft_delete_source(name):
    source = session.query(Source).filter_by(name=name).first()
    if source:
        source.is_deleted = True
        session.commit()
        return True
    return False

# TODO: Fix bug when create new category with the same name is deleted;
def soft_delete_category(name):
    category = session.query(Category).filter_by(name=name).first()
    if category:
        category.is_deleted = True
        session.commit()
        return True
    return False

def get_transactions():
    return session.query(Transaction).all()
