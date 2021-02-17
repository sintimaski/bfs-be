from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from contextlib import contextmanager
from typing import ContextManager

from sqlalchemy.orm import Session

db: SQLAlchemy = SQLAlchemy()
migrate = Migrate()


@contextmanager
def session() -> ContextManager[Session]:
    yield Session(...)
