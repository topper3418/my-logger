# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask import current_app

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    log_type = db.Column(db.String(50))
    comment = db.Column(db.String(255))

    def __repr__(self):
        return f'<Log {self.timestamp}, {self.comment}>'

with app.app_context():
    Session = sessionmaker(bind=db.engine)
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_log', methods=['POST'])
def add_log():
    data = request.form
    new_log = Log(timestamp=datetime.now(),
                  log_type=data['log-type'], 
                  comment=data['log-comment'])
    with Session() as session:
        session.add(new_log)
        session.commit()
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
    return jsonify([{'id': log.id, 'timestamp': log.timestamp, 'log_type': log.log_type, 'comment': log.comment} for log in logs])

if __name__ == '__main__':
    app.run(debug=True)
