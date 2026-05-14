import sqlite3
from contextlib import contextmanager
from backend.config import config


@contextmanager
def get_db():
    #менеджер для работы с бд
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB Error] {e}")
        raise
    finally:
        conn.close()


def init_db():
    #инициализация бд
    from backend.database.models import create_tables
    create_tables()