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
        reply = [f"Hello, {escape(name)}."]
        engine = models.get_engine()
        metadata_obj = MetaData()
        best_names = Table("best_names", metadata_obj, autoload_with = engine)
        stmt = select(best_names).where(best_names.c.name == name)
        with engine.connect() as conn:
            additional_replies = [r.special_greeting for r in conn.execute(stmt)]
        reply += additional_replies
        reply = " ".join(reply)
        return reply
        

    @app.route('/')
    def default():
        x = environ.get('FLASK_APP')
        return f"Hello, world. Check out this cool {x}."

    return app