# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask import current_app

from datetime import datetime, date
from icecream import ic
from typing import List

from app.comment_parser import parse_comment
from app import app, db, Session

from app.models import Log, LogType, Activity


with app.app_context():
    db.create_all()
    default_log_types = [
        LogType(log_type='thought', color='lightblue'),
        LogType(log_type='task', color='orange'),
        LogType(log_type='error', color='red'),
        LogType(log_type='complete', color='green'),
        LogType(log_type='distraction', color='purple')
    ]
    with Session() as session:
        # Check if LogType table is empty
        if not session.query(LogType).first():
            session.add_all(default_log_types)
            session.commit()

@app.route('/')
def index():
    return render_template('index.html')

def add_log(log_type_id, comment, parent_id):
    new_log = Log(timestamp=datetime.now(),
                  log_type_id=log_type_id, 
                  comment=comment,
                  parent_id=parent_id)
    with Session() as session:
        session.add(new_log)
        session.commit()

def set_activity(log_id: int=None):
    new_activity = Activity(timestamp=datetime.now(),
                            active_log_id=log_id)
    with Session() as session:
        session.add(new_activity)
        session.commit()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    comment = parse_comment(data['log-comment'])
    ic(comment)
    # state commands have no comment string, so they only change the state
    if comment.state_command:
        set_activity(comment.parent_id)
    else:
        # if the parser picks up a comment type, that overrides whats in the dropdown
        log_type = comment.log_type_id or data['log-type-id']
        current_activity = get_activity()
        # if the parser picks up a parent id, that overrides the current activity
        if comment.parent_id == 0:  # 0 means the user wants an orphan comment
            parent_id = None
        elif comment.parent_id is None and current_activity:  # none means the user did not specify parent
            parent_id = current_activity.id # (so use the current activity)
        else:  # otherwise use the parent id from the comment
            parent_id = comment.parent_id  # this will be None if the user does not specify, which is what we want. 
        add_log(log_type, comment.comment, parent_id)
    return redirect('/')

@app.route('/configure_log_types', methods=['GET', 'POST'])
def configure_log_types():
    if request.method == 'GET':
        return render_template('configure_log_types.html')
    elif request.method == 'POST':
        data = request.form
        log_type = LogType(log_type=data['log-type'], color=data['color'])
        with Session() as session:
            session.add(log_type)
            session.commit()
        return redirect('/configure_log_types')

@app.route('/delete_log_type', methods=['POST'])
def delete_log_type():
    data = request.args
    with Session() as session:
        log_type = session.query(LogType).filter(LogType.id == data['id']).first()
        session.delete(log_type)
        session.commit()
    return redirect('/configure_log_types')

@app.route('/get_logs', methods=['GET'])
def get_logs():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    start_time = datetime.fromtimestamp(int(start_time)/1000.0)
    end_time = datetime.fromtimestamp(int(end_time)/1000.0)

    with Session() as session:
        if start_time and end_time:
            logs = session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
        else:
            logs = session.query(Log).all()
        data = [{'id': log.id,
                    'timestamp': log.timestamp.strftime('%H:%M'),
                    'log_type': log.log_type.log_type if log.log_type else None,
                    'comment': log.comment,
                    'parent_id': log.parent_id} for log in logs]
    return jsonify(data)

@app.route('/get_log_types', methods=['GET'])
def get_log_types():
    with Session() as session:
        log_types = session.query(LogType).all()
    return jsonify([{'id': log_type.id, 
                     'log_type': log_type.log_type,
                     'color': log_type.color} 
                     for log_type in log_types])

@app.route('/get_log_table', methods=['GET'])
def get_log_table(): 
    current_date = date.today()

    # Set the start_time to the beginning of the current day
    start_time = datetime.combine(current_date, datetime.min.time())

    # Set the end_time to the end of the current day
    end_time = datetime.combine(current_date, datetime.max.time())

    with Session() as session:
        if start_time and end_time:
            logs = session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
        else:
            logs = session.query(Log).all()

    # Create an HTML table from the data
    table = '<table><tr><th>ID</th><th>Timestamp</th><th>Log Type</th><th>Comment</th><th>Parent ID</th></tr>'
    for log in logs:
        table += f'<tr><td>{log.id}</td><td>{log.timestamp}</td><td>{log.log_type}</td><td>{log.comment}</td><td>{log.parent_id}</td></tr>'
    table += '</table>'

    # Return the HTML table as a response
    return table

def get_activity() -> Log:
    with Session() as session:
        current_activity = session.query(Activity).order_by(Activity.timestamp.desc()).first()
        if current_activity:
            current_activity = current_activity.active_log
        else:
            current_activity = None
    return current_activity

def get_span(session, activity: Activity) -> int:
    """returns the amount of time between the given activity and the next one"""
    next_activity = session.query(Activity).filter(Activity.id == activity.id + 1).first()
    if next_activity:
        return (next_activity.timestamp - activity.timestamp).total_seconds()
    else:
        return (datetime.now() - activity.timestamp).total_seconds()

def get_active_duration(session, log_id: int) -> int:
    """returns the amount of time between the given log and the next activity"""
    active_spans = session.query(Activity).filter(Activity.active_log_id == log_id).all()
    return sum([get_span(session, activity) for activity in active_spans])

@app.route('/current_activity', methods=['GET'])
def get_current_activity():
    current_activity = get_activity()
    return jsonify(current_activity.comment if current_activity else 'no current task')

def get_activity_history(session, start_time: datetime=None, end_time: datetime=None) -> List[Activity]:
    if start_time and end_time:
        activities = session.query(Activity).filter(Activity.timestamp.between(start_time, end_time)).all()
    else:
        activities = session.query(Activity).all()
    return activities

@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    if start_time and end_time:
        start_time = datetime.fromtimestamp(int(start_time)/1000.0)
        end_time = datetime.fromtimestamp(int(end_time)/1000.0)

    with Session() as session:
        if start_time and end_time:
            activities = session.query(Activity).filter(Activity.timestamp.between(start_time, end_time)).all()
        else:
            activities = session.query(Activity).all()
        data = [{'id': activity.id, 
                 'timestamp': activity.timestamp, 
                 'duration': get_span(session, activity).total_seconds(),
                 'active_log_id': activity.active_log_id} 
                 for activity in activities]
    return jsonify(data)

def get_logs_helper(session, start_time: datetime=None, end_time: datetime=None) -> List[Log]:
    """returns a list of logs between the given start and end times"""
    if start_time and end_time:
        return session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
    else:
        return session.query(Log).all()

def has_children(session, log: Log) -> bool:
    """returns True if the log has children, False otherwise"""
    return bool(session.query(Log).filter(Log.parent_id == log.id).first())

def get_children(session, log: Log) -> List[Log]:
    """returns a list of the children of the given log"""
    return session.query(Log).filter(Log.parent_id == log.id).all()

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

@app.route('/get_log_tree', methods=['GET'])
def get_log_tree():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    if start_time and end_time:
        start_time = datetime.fromtimestamp(int(start_time)/1000.0)
        end_time = datetime.fromtimestamp(int(end_time)/1000.0)
    with Session() as session:
        logs = get_logs_helper(session, start_time, end_time)
        log_ids = [log.id for log in logs]
        orphans = [log for log in logs if log.parent_id not in log_ids]
        tree = [assemble_tree(session, orphan) for orphan in orphans]
    return jsonify(tree)

@app.route('/get_logs_v2', methods=['GET'])
def get_logs_v2():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    start_time = datetime.fromtimestamp(int(start_time)/1000.0)
    end_time = datetime.fromtimestamp(int(end_time)/1000.0)

    with Session() as session:
        if start_time and end_time:
            logs = session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
        else:
            logs = session.query(Log).all()
        data = [{'id': log.id,
                 'timestamp': log.timestamp.strftime('%H:%M'),
                 'log_type': log.log_type.log_type if log.log_type else None,
                 'time_spent': get_active_duration(session, log.id),
                 'comment': log.comment,
                 'complete': any(child.log_type.log_type == 'complete' for child in get_children(session, log)),
                 'parent_id': log.parent_id} for log in logs]
    return jsonify(data)

@app.route('/get_activity_history_table', methods=['GET'])
def get_state_history_table():
    start_time = datetime.now().date()
    end_time = datetime.now()
    # Create an HTML table from the data
    table = '<table><tr><th>ID</th><th>Timestamp</th><th>Log Id</th><th>Comment</th></tr>'
    with Session() as session:
        activities = get_activity_history(session, start_time=start_time, end_time=end_time)
        for activity in activities:
            comment = None if not activity.active_log_id else activity.active_log.comment
            table += f'<tr><td>{activity.id}</td><td>{activity.timestamp}</td><td>{activity.active_log_id}</td><td>{comment}</td></tr>'
    table += '</table>'
    return table


if __name__ == '__main__':
    app.run(debug=True)
