from sqlalchemy.sql import text

from simulation_copilot.database import get_session


def clean_db():
    session = get_session()
    session.execute(text("DELETE FROM calendar_intervals"))
    session.execute(text("DELETE FROM calendars"))
    session.execute(text("DELETE FROM activities"))
    session.execute(text("DELETE FROM activity_distributions"))
    session.execute(text("DELETE FROM resources"))
    session.execute(text("DELETE FROM resource_profiles"))
    session.commit()


if __name__ == "__main__":
    clean_db()
