from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from icecream import ic


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

default_log_types = [
    {'log_type': 'thought', 'color': 'lightblue'},
    {'log_type': 'task', 'color': 'orange'},
    {'log_type': 'error', 'color': 'red'},
    {'log_type': 'complete', 'color': 'green'},
    {'log_type': 'distraction', 'color': 'purple'}
]


with app.app_context():
    Session = sessionmaker(bind=db.engine)

