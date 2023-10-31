# this module contains functions that interact with the database
# this includes returning objects from the models database, adding to the database
# and returning other data structures from the database

from app import Session
from app.models import (LogType, 
                        Log, 
                        Activity, 
                        Comment, 
                        TimeSpan)

from icecream import ic
from datetime import datetime
from typing import List


#############################################################
## setters
#############################################################

def set_activity(log_id: int) -> None:
    with Session() as session:
        activity = Activity(timestamp=datetime.now(), 
                            active_log_id=log_id)
        session.add(activity)
        session.commit()


def add_log(comment: Comment, log_type_default: str=None)  -> None:
    # use comment log type id if it exists, otherwise use the default
    log_type_id = int(comment.log_type_id or log_type_default)
    with Session() as session:
        # get the current activity from db
        current_activity = get_current_activity(session)
        # logic for parent id
        if comment.parent_id == 0:  # 0 means the user wants an orphan comment
            parent_id = None
        elif comment.parent_id is None and current_activity:  # none means the user did not specify parent
            parent_id = current_activity.active_log_id # (so use the current activity)
        else:  # otherwise use the parent id from the comment
            parent_id = comment.parent_id  # this will be None if the user does not specify, which is what we want. 
        # add to database
        log = Log(timestamp=datetime.now(),
                  log_type_id=log_type_id, 
                  comment=comment.comment, 
                  parent_id=parent_id)
        session.add(log)
        session.commit()


def add_log_type(log_type: str, color: str) -> None:
    with Session() as session:
        log_type = LogType(log_type=log_type, color=color)
        session.add(log_type)
        session.commit()


def delete_log_type(log_type_id: int) -> None:
    with Session() as session:
        log_type = session.query(LogType).filter(LogType.id == log_type_id).first()
        session.delete(log_type)
        session.commit()


#############################################################
## native object getters
#############################################################

def get_log_types(as_dict: bool=False) -> list[str]:
    """returns a list of all LogType objects"""
    with Session() as session:
        result = session.query(LogType).all()
    if as_dict:
        return [{'id': log_type.id, 
                 'log_type': log_type.log_type, 
                 'color': log_type.color} 
                 for log_type in result]
    return [log_type.log_type for log_type in result]


def get_log_type_id(log_type: str) -> int|None:
    """returns the LogType object with the given log_type, or None if it doesn't exist"""
    with Session() as session:
        log_type = session.query(LogType).filter(LogType.log_type == log_type).first()
    if log_type:
        return log_type.id


def get_current_activity_comment() -> str|None:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return current_activity.active_log.comment


#############################################################
## models getters
#############################################################
# these all take a session as an argument, so they can be used in a session context


def query_logs(session, time_span: TimeSpan=None) -> List[Log]:
    if time_span:
        logs = session.query(Log).filter(Log.timestamp >= time_span.start, Log.timestamp <= time_span.end).all()
    else:
        logs = session.query(Log).all()
    return logs


def query_activities(session, time_span: TimeSpan=None) -> List[Activity]:
    if time_span:
        activities = session.query(Activity).filter(Activity.timestamp >= time_span.start, Activity.timestamp <= time_span.end).all()
    else:
        activities = session.query(Activity).all()
    return activities


def get_current_activity(session) -> Activity|None:
    return session.query(Activity).order_by(Activity.timestamp.desc()).first()


def get_children(session, log: Log) -> List[Log]:
    """returns a list of the children of the given log"""
    return session.query(Log).filter(Log.parent_id == log.id).all()


#############################################################
## other getters
#############################################################
# these return native objects but still maintain the context of a session


def get_activity_duration(session, activity: Activity) -> int:
    """returns the amount of time between the given activity and the next one"""
    next_activity = session.query(Activity).filter(Activity.id == activity.id + 1).first()
    if next_activity:
        return (next_activity.timestamp - activity.timestamp).total_seconds()
    else:
        return (datetime.now() - activity.timestamp).total_seconds()


def get_log_active_time(session, log: Log) -> int:
    """gets the total duration of activities with this log as the parent"""
    activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
    return sum([get_activity_duration(session, activity) for activity in activities])


def has_children(session, log: Log) -> bool:
    """returns True if the log has children, False otherwise"""
    return bool(session.query(Log).filter(Log.parent_id == log.id).first())


def assemble_tree(session, log: Log) -> dict:
    """returns a dictionary representing the given log and its children"""
    children = get_children(session, log)
    has_complete = any(child.log_type.log_type == 'complete' for child in children)
    dict_out = {'id': log.id,
                'timestamp': log.timestamp,
                'log_type': log.log_type.log_type if log.log_type else None,
                'comment': log.comment,
                'parent_id': log.parent_id if log.parent_id else None,
                'complete': has_complete,
                'children': [assemble_tree(session, child) for child in children]}
    return dict_out