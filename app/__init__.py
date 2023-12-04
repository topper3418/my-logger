from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from .lib.logging import log_runtime
from .lib.log_types import default_log_types, get_log_type

from icecream import ic


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)



with app.app_context():
    Session = sessionmaker(bind=db.engine)

