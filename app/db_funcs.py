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
                 'time_spent': get_log_active_time(session, log),
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
        orig_root_logs = root_logs
        ic(orig_root_logs)
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


def get_activity_duration(session, activity: Activity) -> int:
    """returns the amount of time between the given activity and the next one"""
    next_activity = session.query(Activity).filter(Activity.id == activity.id + 1).first()
    if next_activity:
        return (next_activity.timestamp - activity.timestamp).total_seconds()
    else:
        return (datetime.now() - activity.timestamp).total_seconds()


def get_log_active_time(session, log: Log, time_span: TimeSpan=None) -> int:
    """gets the total duration of activities linked to this log, today"""
    if not time_span:
        activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
        return sum([get_activity_duration(session, activity) for activity in activities if activity.timestamp.date() == datetime.now().date()])
    else:
        activities = session.query(Activity).filter(Activity.active_log_id == log.id).all()
        return sum([get_activity_duration(session, activity) for activity in activities if activity.timestamp in time_span])


def has_children(session, log: Log) -> bool:
    """returns True if the log has children, False otherwise"""
    return bool(session.query(Log).filter(Log.parent_id == log.id).first())


def has_promoted_descendant(session, log: Log) -> bool:
    """returns True if the log has a descendant that has been promoted, False otherwise"""
    descendants = get_descendants(session, log)
    return any(descendant.log_type == 'promote' for descendant in descendants)


def has_promote(session, log: Log) -> bool:
    """returns True if the log has been promoted, False otherwise"""
    return any(child.log_type == 'promote' for child in log.children)


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
                    if has_promoted_descendant(session, child) or has_promote(session, child)]
    
    direct_duration = get_log_active_time(session, log, time_span=time_span)
    if children:
        total_duration = children_duration + direct_duration
    else:
        total_duration = direct_duration
    days_ago = log.days_ago
    word = ['',
            'one',
            'two',
            'three',
            'four',
            'many'][days_ago if days_ago <= 4 else 5]
    if not promotion_mode:
        days_ago_class = f'{word}-days-ago' if days_ago <= 4 else 'many'
    # if promotion mode, the days_ago_class (needs to be renamed) is dependent on whether the log has been promoted
    if promotion_mode:
        days_ago_class = 'promoted' if has_promote(session, log) else ''

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
                'is_from_today': log.days_ago == 0,
                'days_ago_class': days_ago_class,
                'days_ago': log.days_ago,
                'children': children}
    # propagate up means to nest the dict in parents until the root is reached
    if propagate_up:
        while log.parent_id:
            dict_out = assemble_tree(session, log.parent, manual_children=[dict_out])
            log = log.parent

    return dict_out
