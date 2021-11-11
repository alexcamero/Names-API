from os import path

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, Enum
from sqlalchemy.orm import registry, relationship, Session
import click
from flask import current_app, g
from flask.cli import with_appcontext

mapper_registry = registry()
Base = mapper_registry.generate_base()

class Name(Base):
    __tablename__ = 'name'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), unique = True)

    data = relationship("Data", back_populates = "name")

    def __repr__(self):
        return self.name

class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique = True)

    data = relationship("Data", back_populates = "location")

    def __repr__(self):
        return self.name

class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key = True)
    name_id = Column(Integer, ForeignKey('name.id'))
    location_id = Column(Integer, ForeignKey('location.id'))
    year = Column(Integer)
    value = Column(Integer)
    sex = Column(Enum('F','M'))

    name = relationship("Name", back_populates = "data")
    location = relationship("Location", back_populates = "data")

    def __repr__(self):
        return f"Data(year = {self.year}, location = {self.location!r}, name = {self.name!r}, sex = {self.sex!r}, count = {self.value})"


def get_engine(remote = False):
    if 'engine' not in g:
        if remote:
            g.engine = create_engine(current_app.config['REMOTE_ENGINE'])
        else:
            g.engine = create_engine(current_app.config['ENGINE'])
    return g.engine

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


@click.command('process-year')
@click.option('--remote', default = False)
@click.option('--year', prompt = True)
@with_appcontext
def process_year(year, remote):
    file_path = path.join(current_app.config['DATA_DIR'], 'year', f"yob{year}.txt")
    with open(file_path, 'r') as file:
        rows = [line[0:-1].split(',') for line in file]
    engine = get_engine(remote)
    sesh = Session(engine)
    stmt = select(Location).where(Location.name == 'United States')
    result = sesh.execute(stmt)
    usa = result.scalars().first() or Location(name = 'United States')
    for row in rows:
        stmt = select(Name).where(Name.name == row[0])
        result = sesh.execute(stmt)
        name = result.scalars().first() or Name(name = row[0])
        data = Data(name = name, location = usa, value = int(row[2]), sex = row[1], year = year)
        sesh.add(data)
    sesh.commit()
    sesh.close()



    
    

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(kill_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(process_year)