# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask import current_app

from datetime import datetime, date
from icecream import ic
from typing import List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

class LogType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50))
    color = db.Column(db.String(50))

    def __repr__(self):
        return f'<LogTypes {self.id} - {self.log_type}>'
    
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    log_type_id = db.Column(db.Integer, db.ForeignKey('log_type.id'))
    log_type = db.relationship('LogType', backref='logs', lazy=True)
    comment = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    parent = db.relationship('Log', remote_side=[id], backref='children', lazy=True)

    def __repr__(self):
        return f'<Log {self.id} - {self.timestamp} - parent: {self.parent_id} - {self.comment}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    active_log_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    active_log = db.relationship('Log', backref='activity', lazy=True)

    def __repr__(self):
        return f'<Activity {self.timestamp}, {self.active_log_id}>'

def get_log_type(log_type: str) -> LogType|None:
    """returns the LogType object with the given log_type, or None if it doesn't exist"""
    with Session() as session:
        result =  session.query(LogType).filter(LogType.log_type == log_type).first()
    return result

with app.app_context():
    Session = sessionmaker(bind=db.engine)
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

class CommentParser:
    """takes in a comment, and makes available the following properties:
    - comment_type (if specified)
    - parent_id (if specified)
    - comment (the comment itself, stripped of special commands)"""
    def __init__(self, comment: str):
        self.comment = comment
        self.log_type_id = None
        self.parent_id = None
        self.state_command = False
        self.parse_comment()
    
    def parse_comment(self):
        """strips the comment of any special commands"""
        comment = self.comment
        commands = []
        while '[' in comment and ']' in comment:
            # get the text between the brackets
            bracket_text = comment[comment.find('[')+1:comment.find(']')]
            commands.append(bracket_text)
            # remove the text between the brackets
            comment = comment.replace(f'[{bracket_text}]', '')
        # verify the commands are valid
        if len(commands) > 2:
            raise ValueError('Too many commands in comment')
        for command in commands:
            if command.isnumeric():
                if self.parent_id:
                    raise ValueError('Too many parent ids in comment')
                self.parent_id = int(command)
            elif not command:
                self.state_command = True
            else:
                log_type = get_log_type(command)
                if log_type:
                    if self.log_type_id:
                        raise ValueError('Too many log types in comment')
                    self.log_type_id = log_type.id
                else:
                    raise ValueError(f'Invalid command in comment: {command}')
        self.comment = comment.strip()
        if not self.state_command:
            self.state_command = not self.comment and\
                                 not self.log_type_id and\
                                 self.parent_id

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
    parser = CommentParser(data['log-comment'])
    if parser.state_command:
        set_activity(parser.parent_id)
    else:
        # if the parser picks up a comment type, use that
        log_type = parser.log_type_id or data['log-type-id']
        activity = get_activity()
        parent_id = parser.parent_id or (None if not activity else activity.id)
        add_log(log_type, parser.comment, parent_id)
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
    table = '<table><tr><th>ID</th><th>Timestamp</th><th>Log Type</th><th>Comment</th></tr>'
    for log in logs:
        table += f'<tr><td>{log.id}</td><td>{log.timestamp}</td><td>{log.log_type}</td><td>{log.comment}</td></tr>'
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

@app.route('/current_activity', methods=['GET'])
def get_current_activity():
    current_activity = get_activity()
    return jsonify(current_activity.comment if current_activity else 'no current task')

@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    start_time = datetime.fromtimestamp(int(start_time)/1000.0)
    end_time = datetime.fromtimestamp(int(end_time)/1000.0)

    with Session() as session:
        if start_time and end_time:
            activities = session.query(Activity).filter(Activity.timestamp.between(start_time, end_time)).all()
        else:
            activities = session.query(Activity).all()
    return jsonify([{'id': activity.id, 
                     'timestamp': activity.timestamp, 
                     'active_log_id': activity.active_log_id} 
                     for activity in activities])

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
    dict_out = {'id': log.id,
            'timestamp': log.timestamp,
            'log_type': log.log_type.log_type if log.log_type else None,
            'comment': log.comment,
            'parent_id': log.parent_id if log.parent_id else None,
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

if __name__ == '__main__':
    app.run(debug=True)
