from app import db

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


