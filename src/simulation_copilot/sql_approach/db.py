import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


def make_engine(db_url):
    return sa.create_engine(db_url)


def database_url():
    return os.environ.get("DATABASE_URL") or "sqlite://"


def make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


engine = make_engine(database_url())
session = make_session(engine)
