import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from simulation_copilot.prosimos_relational_model import Base


def create_tables(engine):
    Base.metadata.create_all(engine)


def make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def make_engine(db_url):
    return sa.create_engine(db_url)


def get_database_url():
    return os.environ.get("DATABASE_URL") or "sqlite://"


in_memory = False

db_url = get_database_url()
if db_url == "sqlite://" or db_url == "sqlite:///:memory:":
    in_memory = True

engine = make_engine(db_url)
session = make_session(engine)
