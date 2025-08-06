from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.crud import add_category, is_name_exist_in_category
from database.models import Base
from config import SQL_DB
from translations import ru

engine = create_engine(SQL_DB, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def init_user_objects():
    # Категории по умолчанию
    if is_name_exist_in_category(ru.TRANSACTIONS_TYPE_TRANSFERS):   #TODO: Когда user_id появится, чекать дополнительно user_id
        add_category(ru.TRANSACTIONS_TYPE_TRANSFERS)
