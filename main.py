# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask import current_app

from datetime import datetime, date
from typing import List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    log_type = db.Column(db.String(50))
    comment = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    parent = db.relationship('Log', remote_side=[id], backref='children', lazy=True)

    def __repr__(self):
        return f'<Log {self.timestamp}, {self.comment}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    active_log_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    active_log = db.relationship('Log', backref='activity', lazy=True)

    def __repr__(self):
        return f'<Activity {self.timestamp}, {self.active_log_id}>'
    

with app.app_context():
    Session = sessionmaker(bind=db.engine)
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

def add_log(log_type, comment):
    new_log = Log(timestamp=datetime.now(),
                  log_type=log_type, 
                  comment=comment)
    with Session() as session:
        session.add(new_log)
        session.commit()

class CommentParser:
    """takes in a comment, and makes available the following properties:
    - comment_type (if specified)
    - parent_id (if specified)
    - comment (the comment itself, stripped of special commands)"""
    def __init__(self, comment: str):
        self.comment = comment
        self.comment_type = None
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
            elif command in ['thought', 'action', 'task', 'error', 'success', 
                             'completion', 'learning', 'break', 'distraction', 
                             'issue']:
                if self.comment_type:
                    raise ValueError('Too many comment types in comment')
                self.comment_type = command
            elif not command:
                self.state_command = True
            else:
                raise ValueError(f'Invalid command in comment: {command}')
        self.comment = comment.strip()
        if not self.state_command:
            self.state_command = not self.comment and\
                                 not self.comment_type and\
                                 self.parent_id

def add_log(log_type, comment, parent_id):
    new_log = Log(timestamp=datetime.now(),
                  log_type=log_type, 
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
    data = request.form
    parser = CommentParser(data['log-comment'])
    if parser.state_command:
        set_activity(parser.parent_id)
    else:
        # if the parser picks up a comment type, use that
        log_type = parser.comment_type or data['log-type']
        activity = get_activity()
        parent_id = parser.parent_id or None if not activity else get_activity().id
        add_log(log_type, parser.comment, parent_id)
    return redirect('/')

@app.route('/get_logs', methods=['GET'])
def get_logs():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    start_time = datetime.fromtimestamp(int(start_time)/1000.0)
    end_time = datetime.fromtimestamp(int(end_time)/1000.0)

    with Session() as session:
        if start_time and end_time:
            logs = session.query(Log).filter(Log.timestamp.between(start_time, end_time)).all()
            print(logs)
        else:
            logs = session.query(Log).all()
    return jsonify([{'id': log.id, 
                     'timestamp': log.timestamp, 
                     'log_type': log.log_type, 
                     'comment': log.comment,
                     'parent_id': log.parent_id} 
                     for log in logs])

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
    start_time = datetime.fromtimestamp(int(start_time)/1000.0)
    end_time = datetime.fromtimestamp(int(end_time)/1000.0)
    with Session() as session: 
        activities = get_activity_history(session, start_time=start_time, end_time=end_time)
    return jsonify([{'id': activity.id, 
                     'timestamp': activity.timestamp, 
                     'active_log_id': activity.active_log_id} 
                     for activity in activities])

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
