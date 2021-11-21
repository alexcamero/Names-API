from sqlalchemy import create_engine
from sqlalchemy.orm import registry, Session
import click
from flask import current_app, g
from flask.cli import with_appcontext

from application.models import mapper_registry

def get_engine(remote = False):
    if 'engine' not in g:
        if remote:
            g.engine = create_engine(current_app.config['REMOTE_ENGINE'])
        else:
            g.engine = create_engine(current_app.config['ENGINE'])
    return g.engine

def get_session(remote = False):
    if 'session' not in g:
        engine = get_engine(remote)
        g.session = Session(engine)
    return g.session

def close_session(e = None):
    session = g.pop('session', None)
    if session is not None:
        session.close()

@click.command('init-db')
@click.option('--remote', default = False)
@with_appcontext
def init_db_command(remote):
    engine = get_engine(remote)
    mapper_registry.metadata.create_all(engine)
    click.echo('Database initialized.')

@click.command('kill-db')
@click.option('--remote', default = False)
@with_appcontext
def kill_db_command(remote):
    engine = get_engine(remote)
    mr = registry()
    mr.metadata.reflect(engine)
    mr.metadata.drop_all(engine)
    click.echo('Database emptied of tables and data.')

@click.command('reset-db')
@click.option('--remote', default = False)
@with_appcontext
def reset_db_command(remote):
    engine = get_engine(remote)
    mr = registry()
    mr.metadata.reflect(engine)
    mr.metadata.drop_all(engine)
    mapper_registry.metadata.create_all(engine)
    click.echo('Database has been reset.')