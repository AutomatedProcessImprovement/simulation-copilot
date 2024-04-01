import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


def make_engine(db_url):
    if not db_url:
        db_url = "sqlite://:memory:"
    return sa.create_engine(db_url)


def make_session(engine):
    engine = make_engine(os.environ.get("DATABASE_URL"))

    Session = sessionmaker(bind=engine)
    return Session()


engine = make_engine()
session = make_session(engine)
