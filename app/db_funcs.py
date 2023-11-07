# this module contains functions that interact with the database
# this includes returning objects from the models database, adding to the database
# and returning other data structures from the database

from app import Session, default_log_types#, get_color

from app.models import (Log, 
                        Activity, 
                        Comment, 
                        TimeSpan)
from app.util import get_duration_string

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


def add_log(comment: Comment, log_type_default: str=None) -> None:
    # use comment log type id if it exists, otherwise use the default
    log_type = comment.log_type or log_type_default
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
                  log_type=log_type, 
                  comment=comment.comment, 
                  parent_id=parent_id)
        session.add(log)
        session.commit()


def edit_log(log_id: int, comment: Comment, log_type_default: str=None, parent_id: int=None) -> None:
    with Session() as session:
        log = get_log(session, log_id)
        log.log_type = comment.log_type or log_type_default
        log.comment = comment.comment
        log.parent_id = parent_id
        session.commit()

#############################################################
## native object getters
#############################################################

def get_current_activity_comment() -> str|None:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return current_activity.active_log.comment


def get_current_tree_data() -> List[dict]|None:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return [assemble_tree(session, current_activity.active_log, propagate_up=True)]


def get_logs_object(time_span: TimeSpan=None, reversed: bool=True) -> List[dict]:
    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        data = [{'id': log.id,
                 'timestamp': log.timestamp.strftime('%H:%M'),
                 'log_type': log.log_type,
                 'time_spent': get_log_today_active_time(session, log),
                 'comment': log.comment,
                 'complete': any(child.log_type == 'complete' for child in get_children(session, log)),
                 'parent_id': log.parent_id} for log in logs]
    if reversed:
        data.reverse()
    return data


def get_activities_object(time_span: TimeSpan=None) -> List[dict]:
    with Session() as session:
        activities = query_activities(session, time_span=time_span)
        data = [{'id': activity.id, 
                 'timestamp': activity.timestamp.strftime('%H:%M'), 
                 'duration': get_activity_duration(session, activity),
                 'active_log_id': activity.active_log_id} 
                 for activity in activities]
        return data


def get_log_tree_object(time_span: TimeSpan=None) -> List[dict]:
    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        log_ids = [log.id for log in logs]
        root_logs = [log for log in logs if log.parent_id not in log_ids]
        # if the orphan is an import, bring in the parent instead and put it in the back
        imports = []
        for log in root_logs:
            if log.log_type == 'import':
                parent = log.parent
                if parent:
                    imports.append(parent)
                    root_logs.remove(log)
        tree = [assemble_tree(session, root) for root in root_logs + imports]
    return tree


def get_log_dict(log_id: int) -> dict:
    with Session() as session:
        log = get_log(session, log_id)
        return {'id': log.id,
                'timestamp': log.timestamp.strftime('%H:%M'),
                'log_type': log.log_type,
                'comment': log.comment,
                'parent_id': log.parent_id}


def get_current_activity_log_dict() -> dict:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return get_log_dict(current_activity.active_log_id)

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


def get_log(session, log_id: int) -> Log:
    return session.query(Log).filter(Log.id == log_id).first()


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


def get_log_today_active_time(session, log: Log) -> int:
    """gets the total duration of activities linked to this log, today"""
    activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
    return sum([get_activity_duration(session, activity) for activity in activities if activity.timestamp.date() == datetime.now().date()])


def get_log_active_time(session, log: Log) -> int:
    """gets the total duration of activities linked to this log"""
    activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
    return sum([get_activity_duration(session, activity) for activity in activities])

def has_children(session, log: Log) -> bool:
    """returns True if the log has children, False otherwise"""
    return bool(session.query(Log).filter(Log.parent_id == log.id).first())


def assemble_tree(session, log: Log, propagate_up: bool=False, manual_children: List[dict]=None) -> dict:
    children = manual_children or [assemble_tree(session, child) for child in log.children]
    direct_duration = get_log_today_active_time(session, log)
    if children:
        total_duration = sum([child['total_duration'] for child in children]) + direct_duration
    else:
        total_duration = direct_duration
    dict_out = {'id': log.id,
                'timestamp': log.timestamp,
                'log_type': log.log_type if log.log_type else None,
                'comment': log.comment,
                'parent_id': log.parent_id if log.parent_id else None,
                'complete': log.has_complete_child,
                'direct_duration': direct_duration,
                'total_duration': total_duration,
                'direct_duration_string': get_duration_string(direct_duration),
                'total_duration_string': get_duration_string(total_duration),
                'is_from_today': log.is_from_today,
                'children': children}
    # propagate up means to nest the dict in parents until the root is reached
    if propagate_up:
        while log.parent_id:
            ic(log.parent_id)
            dict_out = assemble_tree(session, log.parent, manual_children=[dict_out])
            log = log.parent

    return dict_out
