import logging
from typing import Optional, Sequence

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from sqlalchemy import text, Row

from simulation_copilot.sql_approach.db import session


class RunSQLite3QueryInput(BaseModel):
    sql: str = Field(description="SQLite3 single statement. Multiple statements not supported.")


@tool("run_sqlite3_query", args_schema=RunSQLite3QueryInput)
def run_sqlite3_query(sql: str) -> Optional[Sequence[Row]]:
    """
    This functions runs a single SQLite3 statement and returns results.
    """
    result = session.execute(text(sql))
    session.commit()
    if int(result.rowcount) == 0 or result.closed:
        return None
    try:
        return result.all()
    except Exception as e:
        logging.warning(e)
        return None
