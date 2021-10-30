from markupsafe import escape
from flask import Flask

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)
    
    @app.route('/<name>')
    def hello(name):
        return f"Hello, {escape(name)}."

    @app.route('/')
    def default():
        return f"Hello, world."

    return app