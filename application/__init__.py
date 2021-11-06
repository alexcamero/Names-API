from markupsafe import escape
from flask import Flask
from sqlalchemy import create_engine, MetaData, Table, select

def create_app(test_config = None):
    app = Flask(__name__)
    if test_config == None:
        app.config.from_pyfile('config.py')
    
    @app.route('/<name>')
    def hello(name):
        reply = [f"Hello, {escape(name)}."]
        engine = create_engine(f"mysql+pymysql://{app.config['DATABASE_USER']}:{app.config['DATABASE_PASSWORD']}@{app.config['DATABASE_HOST']}/{app.config['DATABASE_NAME']}?charset=utf8mb4")
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
        return f"Hello, world."

    return app