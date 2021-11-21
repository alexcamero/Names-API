from flask import Flask
from sqlalchemy import select

def init_app(app):
    from . import data, db
    app.cli.add_command(db.init_db_command)
    app.cli.add_command(db.kill_db_command)
    app.cli.add_command(db.reset_db_command)
    app.cli.add_command(data.process_year)
    app.cli.add_command(data.process_state)
    app.cli.add_command(data.load_all_data)
    app.cli.add_command(data.load_new_year)
    app.cli.add_command(data.quick_migrate)
    app.teardown_appcontext(db.close_session)

def create_app(test_config = None):
    app = Flask(__name__)
    if test_config == None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)

    init_app(app)
    
    @app.route('/api/<name>')
    def hello(name):
        from .db import get_session
        from .models import Name
        sesh = get_session()
        stmt = select(Name).where(Name.name == name)
        result = sesh.execute(stmt)
        name = result.scalars().first() or Name(name = name)
        return "<br>".join([f"{d!r}" for d in name.data])

    @app.route('/')
    def default():
        return "<h1>Names API</h1><h2>Example Usage:</h2><p><a href='./api/Alexander'>/api/Alexander</a></p>"

    return app