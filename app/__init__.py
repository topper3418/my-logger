from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from icecream import ic


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

default_log_types = [
    'thought',
    'question',
    'task',
    'error',
    'complete',
    'distraction',
    'promote',
    'import'
]


with app.app_context():
    Session = sessionmaker(bind=db.engine)

