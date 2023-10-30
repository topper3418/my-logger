from app import Session
from app.models import LogType


def get_log_type(log_type: str) -> LogType|None:
    """returns the LogType object with the given log_type, or None if it doesn't exist"""
    with Session() as session:
        result =  session.query(LogType).filter(LogType.log_type == log_type).first()
    return result

def get_log_types() -> list[str]:
    """returns a list of all LogType objects"""
    with Session() as session:
        result = session.query(LogType).all()
    return [log_type.log_type for log_type in result]