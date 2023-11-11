from app import db, app

from dataclasses import dataclass
from datetime import datetime

    
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    #log_type_id = db.Column(db.Integer, db.ForeignKey('log_type.id'))
    log_type = db.Column(db.String(55))  # db.relationship('LogType', backref='logs', lazy=True)
    comment = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    parent = db.relationship('Log', remote_side=[id], backref='children', lazy=True)

    @property
    def has_complete_child(self):
        return any(child.log_type == 'complete' for child in self.children)
    
    @property
    def is_from_today(self):
        return self.timestamp.date() == datetime.now().date()
    
    @property 
    def days_ago(self):
        return (datetime.now().date() - self.timestamp.date()).days

    def __repr__(self):
        return f'<Log {self.id} - {self.timestamp} - parent: {self.parent_id} - type: {self.log_type} - {self.comment}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    active_log_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    active_log = db.relationship('Log', backref='activity', lazy=True)

    def __repr__(self):
        return f'<Activity {self.timestamp}, {self.active_log_id}>'


with app.app_context():
    db.create_all()

@dataclass
class Comment:
    comment: str
    log_type: str = None
    parent_id: int = None
    state_command: bool = False


@dataclass
class TimeSpan:
    start: datetime
    end: datetime

    @property
    def duration(self):
        if self.start and self.end:
            return int((self.end - self.start).total_seconds())
        else:
            return None
    
    
    def __contains__(self, timestamp):
        return self.start <= timestamp <= self.end