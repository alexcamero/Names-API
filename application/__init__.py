from flask import Flask
from sqlalchemy import select

from .models import Name
from .db import init_db_command, kill_db_command, reset_db_command, get_session
from .data import process_year, process_state, load_all_data, load_new_year, quick_migrate, close_session

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(kill_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(process_year)
    app.cli.add_command(process_state)
    app.cli.add_command(load_all_data)
    app.cli.add_command(load_new_year)
    app.cli.add_command(quick_migrate)
    app.teardown_appcontext(close_session)

def create_app(test_config = None):
    app = Flask(__name__)
    if test_config == None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)

    init_app(app)
    
    @app.route('/api/<name>')
    def hello(name):
        sesh = get_session()
        stmt = select(Name).where(Name.name == name)
        result = sesh.execute(stmt)
        name = result.scalars().first() or Name(name = name)
        return "<br>".join([f"{d!r}" for d in name.data])

    @app.route('/')
    def default():
        return "<h1>Names API</h1><h2>Example Usage:</h2><p><a href='./api/Alexander'>/api/Alexander</a></p>"

    return app