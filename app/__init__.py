from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

import logging
from functools import wraps
import time

from icecream import ic
import logging
import time
from functools import wraps

import os


def log_runtime(filename):
    log_path = os.path.join('logs', filename)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename=log_path, level=logging.INFO)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = (time.time() - start) * 1000
            logging.info(f'{func.__name__} took {end:.2f} milliseconds')
            return result
        return wrapper

    return decorator


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

