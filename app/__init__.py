from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from icecream import ic


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# default_log_types = [
#     {'log_type': 'thought', 'color': 'lightblue'},
#     {'log_type': 'task', 'color': 'orange'},
#     {'log_type': 'error', 'color': 'red'},
#     {'log_type': 'complete', 'color': 'green'},
#     {'log_type': 'distraction', 'color': 'purple'}
# ]

default_log_types = [
    'thought',
    'task',
    'error',
    'complete',
    'distraction'
]

# def get_color(log_type: str) -> str:
#     for log_type_dict in default_log_types:
#         if log_type_dict['log_type'] == log_type:
#             return log_type_dict['color']
#     return 'black'


with app.app_context():
    Session = sessionmaker(bind=db.engine)

