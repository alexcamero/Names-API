from os import path, listdir

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, Enum
from sqlalchemy.orm import registry, relationship, Session
import click
from flask import current_app, g
from flask.cli import with_appcontext
from bs4 import BeautifulSoup as bs
import requests

state_dict = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 
'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'Washington DC', 'FL': 'Florida',
'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 
'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 
'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 
'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 
'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 
'RI': 'Rhode ISland', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 
'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
'PR': 'Puerto Rico', 'TR': 'American Samoa, Guam, Northern Mariana Islands, and US Virgin Islands'}

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

def load_year_file(year, remote):
    file_path = path.join(current_app.config['DATA_DIR'], 'year', f"yob{year}.txt")
    with open(file_path, 'r') as file:
        rows = [line[0:-1].split(',') for line in file]
    sesh = get_session(remote)
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
    print(f"Data for the United States {year} added successfully.")
    return True

def load_state_file(state, remote, year = False):
    state = state.upper()
    file_path = path.join(current_app.config['DATA_DIR'], 'state', f"{state}.TXT")
    state_name = state_dict[state]
    sesh = get_session(remote)
    stmt = select(Location).where(Location.name == state_name)
    result = sesh.execute(stmt)
    state = result.scalars().first() or Location(name = state_name)
    with open(file_path, 'r') as file:
        if year:
            rows = filter(lambda x: x[2] == year, [line[0:-1].split(',') for line in file])
        else:
            rows = [line[0:-1].split(',') for line in file]
            year = int(rows[0][2])
    for row in rows:
        if year != int(row[2]):
            sesh.commit()
            print(f"Completed {state_name} {sex or 'F'} {year}.")
            year = int(row[2])
        sex = row[1]
        name = row[3]
        value = int(row[4])
        stmt = select(Name).where(Name.name == name)
        result = sesh.execute(stmt)
        name = result.scalars().first() or Name(name = name)
        data = Data(name = name, location = state, value = value, sex = sex, year = year)
        sesh.add(data)
    sesh.commit()
    print(f"Completed {state_name} {sex or 'F'} {year}.")
    return True

@click.command('process-year')
@click.option('--remote', default = False)
@click.option('--year', prompt = True)
@with_appcontext
def process_year(year, remote):
    load_year_file(year, remote)
    

@click.command('process-state')
@click.option('--remote', default = False)
@click.option('--state', prompt = True)
@with_appcontext
def process_state(state, remote):
    load_state_file(state, remote)
    print(f"Data for {state_dict[state]} added successfully.")
 

@click.command('load-all-data')
@click.option('--remote', default = False)
@with_appcontext
def load_all_data(remote):
    get_usa_totals(remote)
    state_dir = path.join(current_app.config['DATA_DIR'], 'state')
    for file_path in listdir(state_dir):
        state = file_path[0:2]
        load_state_file(state, remote)
    year_dir = path.join(current_app.config['DATA_DIR'], 'year')
    for file_path in listdir(year_dir):
        year = file_path[3:7]
        load_year_file(year, remote)
    print('All data added successfully!')
    return True

@click.command('load-new-year')
@click.option('--remote', default = False)
@click.option('--year', prompt = True)
@with_appcontext
def load_new_year(year, remote):
    state_dir = path.join(current_app.config['DATA_DIR'], 'state')
    for file_path in listdir(state_dir):
        state = file_path[0:2]
        load_state_file(state, remote, year)
        print(f"Data for {state_dict[state]} added successfully.")
    get_usa_totals(remote, year = year)
    load_year_file(year, remote)
    print(f"Data for the United States {year} added successfully.")
    print(f"Happy New Year {year}!")

def get_usa_totals(remote, year = False):
    sesh = get_session(remote)
    stmt = select(Location).where(Location.name == 'United States')
    result = sesh.execute(stmt)
    usa = result.scalars().first() or Location(name = 'United States')
    url = "https://www.ssa.gov/OACT/babynames/numberUSbirths.html"
    headers = {'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            + 'AppleWebKit/537.36 (KHTML, like Gecko) '
            + 'Chrome/88.0.4324.150 Safari/537.36'}
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        soup = bs(response.text, 'html.parser')
        data_rows = soup.find_all('tr')
        data_rows.pop(0)
        for row in data_rows:
            cell_list = row.find_all('td')
            data_year = cell_list[0].get_text()
            if not year or data_year == year:
                data_year = int(data_year)
                male = int(cell_list[1].get_text().replace(',',''))
                female = int(cell_list[2].get_text().replace(',',''))
                data = Data(location = usa, value = female, sex = 'F', year = data_year)
                sesh.add(data)
                data = Data(location = usa, value = male, sex = 'M', year = data_year)
                sesh.add(data)
        sesh.commit()
        return True     
    else:
        print(f"There was an issue: Status Code {response.status_code}")
        return False

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(kill_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(process_year)
    app.cli.add_command(process_state)
    app.cli.add_command(load_all_data)
    app.cli.add_command(load_new_year)
    app.teardown_appcontext(close_session)