# this module contains functions that interact with the database
# this includes returning objects from the models database, adding to the database
# and returning other data structures from the database

from .. import Session, default_log_types, log_runtime

from .models import (Log,
                     Activity,
                     Comment, 
                     TimeSpan)
from .util import get_duration_string

from icecream import ic
from datetime import datetime
from typing import List

db_runtime_logger = log_runtime('db_runtime.log')


#############################################################
## setters
#############################################################

@db_runtime_logger
def set_activity(log_id: int) -> None:
    with Session() as session:
        activity = Activity(timestamp=datetime.now(), 
                            active_log_id=log_id)
        session.add(activity)
        session.commit()


@db_runtime_logger
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


@db_runtime_logger
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


@db_runtime_logger
def get_current_tree_data() -> List[dict]|None:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return [assemble_tree(session, current_activity.active_log, propagate_up=True)]


@db_runtime_logger
def get_logs_object(time_span: TimeSpan=None, reversed: bool=True) -> List[dict]:
    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        data = [{'id': log.id,
                 'timestamp': log.timestamp.strftime('%H:%M'),
                 'log_type': log.log_type,
                 'time_spent': get_log_active_time(session, log),
                 'comment': log.comment,
                 'complete': log.has_complete_child,
                 'parent_id': log.parent_id} for log in logs]
    if reversed:
        data.reverse()
    return data


@db_runtime_logger
def get_activities_object(time_span: TimeSpan=None) -> List[dict]:
    with Session() as session:
        activities = query_activities(session, time_span=time_span)
        data = [{'id': activity.id, 
                 'timestamp': activity.timestamp.strftime('%H:%M'), 
                 'duration': get_activity_duration(session, activity),
                 'active_log_id': activity.active_log_id} 
                 for activity in activities]
        return data


@db_runtime_logger
def get_log_tree_object(time_span: TimeSpan=None) -> List[dict]:
    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        log_ids = [log.id for log in logs]
        root_logs = [log for log in logs if log.parent_id not in log_ids]
        # if the orphan is an import, bring in the parent instead and put it in the back
        imported_logs, imported_log_ids = [], []
        for log in root_logs:
            if log.log_type == 'import':
                parent = log.parent
                if parent:
                    imported_logs.append(parent)
                    imported_log_ids.append(log.parent_id)
        # remove root logs that are children of imports so they aren't double-rendered. 
        imported_log_descendents = []
        for imported_log in imported_logs:
            imported_log_descendents += get_descendants(session, imported_log)
        imported_log_ids += [log.id for log in imported_log_descendents]
        root_logs = [log for log in root_logs if log.parent_id not in imported_log_ids]
        tree = [assemble_tree(session, root, time_span) for root in root_logs + imported_logs]
    return tree


@db_runtime_logger
def get_promoted_logs_object() -> List[dict]:
    with Session() as session:
        promotions = session.query(Log).filter(Log.log_type == 'promote').all()
        promoted = [promotion.parent for promotion in promotions]
        promoted_descendants = []
        for promotion in promoted:
            promoted_descendants += get_descendants(session, promotion)
        promoted = [promotion for promotion in promoted if promotion not in promoted_descendants]
        tree = [assemble_tree(session, promotion, promotion_mode=True) for promotion in promoted]
    return tree


@db_runtime_logger
def get_log_dict(log_id: int) -> dict:
    with Session() as session:
        log = get_log(session, log_id)
        return {'id': log.id,
                'timestamp': log.timestamp.strftime('%H:%M'),
                'log_type': log.log_type,
                'comment': log.comment,
                'parent_id': log.parent_id}


@db_runtime_logger
def get_current_activity_log_dict() -> dict:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            return get_log_dict(current_activity.active_log_id)

#############################################################
## models getters
#############################################################
# these all take a session as an argument, so they can be used in a session context

@db_runtime_logger
def query_logs(session, time_span: TimeSpan=None) -> List[Log]:
    if time_span:
        logs = session.query(Log).filter(Log.timestamp >= time_span.start, Log.timestamp <= time_span.end).all()
    else:
        logs = session.query(Log).all()
    return logs


@db_runtime_logger
def query_activities(session, time_span: TimeSpan=None) -> List[Activity]:
    if time_span:
        activities = session.query(Activity).filter(Activity.timestamp >= time_span.start, Activity.timestamp <= time_span.end).all()
    else:
        activities = session.query(Activity).all()
    return activities


@db_runtime_logger
def get_current_activity(session) -> Activity|None:
    return session.query(Activity).order_by(Activity.timestamp.desc()).first()


@db_runtime_logger
def get_log(session, log_id: int) -> Log:
    return session.query(Log).filter(Log.id == log_id).first()


@db_runtime_logger
def get_descendants(session, log: Log) -> List[Log]:
    """returns a list of the descendants of the given log"""
    descendants = []
    if log.children:
        descendants += log.children
        for child in log.children:
            descendants += get_descendants(session, child)
    return descendants
    

#############################################################
## other getters
#############################################################
# these return native objects but still maintain the context of a session


@db_runtime_logger
def get_activity_duration(session, activity: Activity) -> int:
    """returns the amount of time between the given activity and the next one"""
    next_activity = session.query(Activity).filter(Activity.id == activity.id + 1).first()
    if next_activity:
        return (next_activity.timestamp - activity.timestamp).total_seconds()
    else:
        return (datetime.now() - activity.timestamp).total_seconds()


@db_runtime_logger
def get_log_active_time(session, log: Log, time_span: TimeSpan=None) -> int:
    """gets the total duration of activities linked to this log, today"""
    if not time_span:
        activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
        return sum([get_activity_duration(session, activity) for activity in activities if activity.timestamp.date() == datetime.now().date()])
    else:
        activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
        return sum([get_activity_duration(session, activity) for activity in activities if activity.timestamp in time_span])


@db_runtime_logger
def has_promoted_descendant(session, log: Log) -> bool:
    """returns True if the log has a descendant that has been promoted, False otherwise"""
    descendants = get_descendants(session, log)
    return any(descendant.log_type == 'promote' for descendant in descendants)


@db_runtime_logger
def assemble_tree(session, log: Log, 
                           time_span: TimeSpan=None, 
                           propagate_up: bool=False, 
                           manual_children: List[dict]=None,
                           promotion_mode: bool=False) -> dict:
    # if not promotion mode, get all children (get them anyway to get the duration)
    children = manual_children or [assemble_tree(session, child) for child in log.children]
    children_duration = sum([child['total_duration'] for child in children])
    # if promotion mode, only get children that have been promoted or have promoted descendants
    if promotion_mode and not manual_children:
        children = [assemble_tree(session, child, promotion_mode=True) for child in log.children 
                    if has_promoted_descendant(session, child) or child.has_promote_child]
    
    direct_duration = get_log_active_time(session, log, time_span=time_span)
    if children:
        total_duration = children_duration + direct_duration
    else:
         total_duration = direct_duration
    mods = log.mods
    has_complete = mods['has_complete']
    has_promote = mods['has_promote']
    has_error = mods['has_error']
    has_edit = mods['has_edit']
    render = log.log_type not in ['promote', 'import', 'edit']
    dict_out = {'id': log.id,
                'timestamp': log.timestamp,
                'log_type': log.log_type if log.log_type else None,
                'comment': log.comment,
                'parent_id': log.parent_id if log.parent_id else None,
                'complete': has_complete,
                'promote': has_promote,
                'error': has_error,
                'edit': has_edit,
                'direct_duration': direct_duration,
                'total_duration': total_duration,
                'direct_duration_string': get_duration_string(direct_duration),
                'total_duration_string': get_duration_string(total_duration),
                'days_ago': log.days_ago,
                'children': children}
    # propagate up means to nest the dict in parents until the root is reached
    if propagate_up:
        while log.parent_id:
            dict_out = assemble_tree(session, log.parent, manual_children=[dict_out])
            log = log.parent

    return dict_out
