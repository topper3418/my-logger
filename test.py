from flask import render_template, current_app
from flask import render_template, current_app

from app import app



with app.app_context():
    print(render_template('index.html'))

