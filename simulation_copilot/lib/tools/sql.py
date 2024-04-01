from typing import Any
from langchain.tools import tool
from sqlalchemy import text, Result

from simulation_copilot.sql_approach.db import session


@tool("run_sql")
def run_sql(sql: str) -> Result[Any]:
    """
    Run the given SQL statement.
    """

    result = session.execute(text(sql))
    session.commit()
    return result
