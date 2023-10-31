# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import jsonify, request, render_template, redirect

from datetime import datetime
from icecream import ic
from typing import List

from app.comment_parser import parse_comment
from app.db_funcs import (get_current_activity_comment, 
                          set_activity, 
                          add_log, 
                          add_log_type,
                          delete_log_type,
                          query_logs,
                          get_children,
                          get_log_types as db_get_log_types,
                          assemble_tree,
                          query_activities,
                          get_activity_duration,
                          get_log_active_time)
from app import app, db, Session

from app.models import Log, LogType, Activity, Comment, TimeSpan


# this script ought to be in a different __init__.py file
# however to reduce coupling it is best here for now. 
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


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    comment = parse_comment(data['log-comment'])
    # state commands have no comment string, so they only change the state
    if comment.state_command:
        set_activity(comment.parent_id)
    else:
        add_log(comment, data.get('log-type-id'))
    return redirect('/')


@app.route('/configure_log_types', methods=['GET', 'POST'])
def configure_log_types():
    if request.method == 'GET':
        return render_template('configure_log_types.html')
    elif request.method == 'POST':
        data = request.form
        add_log_type(data.get('log_type'), data.get('color'))
        return redirect('/configure_log_types')


@app.route('/delete_log_type', methods=['POST'])
def delete_log_type():
    log_type_id = request.args.get('id')
    delete_log_type(log_type_id)
    return redirect('/configure_log_types')


@app.route('/get_logs', methods=['GET'])
def get_logs():
    time_span = get_time_span(request.args)

    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        data = [{'id': log.id,
                 'timestamp': log.timestamp.strftime('%H:%M'),
                 'log_type': log.log_type.log_type if log.log_type else None,
                 'comment': log.comment,
                 'parent_id': log.parent_id} for log in logs]
    return jsonify(data)


@app.route('/get_log_types', methods=['GET'])
def get_log_types():
    log_types = db_get_log_types(as_dict=True)
    return jsonify(log_types)


# def get_activity_duration(session, log_id: int) -> int:
#     """returns the amount of time between the given log and the next activity"""
#     active_spans = session.query(Activity).filter(Activity.active_log_id == log_id).all()
#     return sum([get_activity_duration(session, activity) for activity in active_spans])


@app.route('/current_activity', methods=['GET'])
def get_current_activity():
    comment = get_current_activity_comment()
    return jsonify(comment or 'no current task')


@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    time_span = get_time_span(request.args)

    with Session() as session:
        activities = query_activities(session, time_span=time_span)
        data = [{'id': activity.id, 
                 'timestamp': activity.timestamp, 
                 'duration': get_activity_duration(session, activity),
                 'active_log_id': activity.active_log_id} 
                 for activity in activities]
    return jsonify(data)

def get_logs_helper(session, start_time: datetime=None, end_time: datetime=None) -> List[Log]:
    """returns a list of logs between the given start and end times"""
    if start_time and end_time:
        return session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
    else:
        return session.query(Log).all()


def get_time_span(request_args) -> TimeSpan|None:
    start_time = request_args.get('start_time')
    end_time = request_args.get('end_time')
    if start_time and end_time:
        start_time = datetime.fromtimestamp(int(start_time)/1000.0)
        end_time = datetime.fromtimestamp(int(end_time)/1000.0)
        return TimeSpan(start_time, end_time)


@app.route('/get_log_tree', methods=['GET'])
def get_log_tree():
    time_span = get_time_span(request.args)
    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        log_ids = [log.id for log in logs]
        orphans = [log for log in logs if log.parent_id not in log_ids]
        tree = [assemble_tree(session, orphan) for orphan in orphans]
    return jsonify(tree)

@app.route('/get_logs_v2', methods=['GET'])
def get_logs_v2():
    time_span = get_time_span(request.args)

    with Session() as session:
        logs = query_logs(session, time_span=time_span)
        data = [{'id': log.id,
                 'timestamp': log.timestamp.strftime('%H:%M'),
                 'log_type': log.log_type.log_type if log.log_type else None,
                 'time_spent': get_log_active_time(session, log),
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
        activities = query_activities(session, start_time=start_time, end_time=end_time)
        for activity in activities:
            comment = None if not activity.active_log_id else activity.active_log.comment
            table += f'<tr><td>{activity.id}</td><td>{activity.timestamp}</td><td>{activity.active_log_id}</td><td>{comment}</td></tr>'
    table += '</table>'
    return table


if __name__ == '__main__':
    app.run(debug=True)
