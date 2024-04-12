import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

in_memory = False


def make_engine(db_url):
    return sa.create_engine(db_url)


def database_url():
    return os.environ.get("DATABASE_URL") or "sqlite://"


def make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


db_url = database_url()
if db_url == "sqlite://" or db_url == "sqlite:///:memory:":
    in_memory = True

engine = make_engine(db_url)
session = make_session(engine)
