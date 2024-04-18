"""Database access API."""

import os

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, Session as SASession

from simulation_copilot.prosimos_relational_model import Base

load_dotenv()


_DB_URL = "sqlite://"
if not os.environ.get("TESTING"):
    _DB_URL = os.environ.get("DATABASE_URL") or "sqlite://"
else:
    print("Testing mode")

_IN_MEMORY = False
if _DB_URL in ("sqlite://", "sqlite:///:memory:"):
    _IN_MEMORY = True

_engine = sa.create_engine(_DB_URL)

Session = sessionmaker(bind=_engine)
_session = Session()


def create_tables():
    """Creates tables associated with Base from simulation_copilot.prosimos_relational_model."""
    print(f"Creating database for {_DB_URL}")
    Base.metadata.create_all(_engine)


def get_session() -> SASession:
    """Returns the module-scoped database session.

    If using not in-memory database, it's safe to use Session().
    """
    return _session


def tables_schema():
    """Returns tables schema associated with Base from simulation_copilot.prosimos_relational_model as a string."""
    output = ""
    for table in Base.metadata.tables.keys():
        output += sa.schema.CreateTable(Base.metadata.tables[table]).compile(_engine).string
    return output
