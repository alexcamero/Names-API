from os import environ

from markupsafe import escape
from flask import Flask
from sqlalchemy import MetaData, Table, select

def create_app(test_config = None):
    app = Flask(__name__)
    if test_config == None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)

    from . import models
    models.init_app(app)
    
    @app.route('/<name>')
    def hello(name):
        sesh = models.get_session(remote = False)
        result = sesh.select(models.Data)
        

    @app.route('/')
    def default():
        x = environ.get('FLASK_APP')
        return f"Hello, world. Check out this cool {x}."

    return app