from os import path, listdir

from sqlalchemy import create_engine, select
import click
from flask import current_app
from flask.cli import with_appcontext
from bs4 import BeautifulSoup as bs
import requests
from progress.bar import Bar

from application.db import get_session
from application.models import Data, Name, Location

state_dict = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 
'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'Washington DC', 'FL': 'Florida',
'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 
'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 
'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 
'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 
'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 
'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 
'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
'PR': 'Puerto Rico', 'TR': 'American Samoa, Guam, Northern Mariana Islands, and US Virgin Islands'}

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

@click.command('quick-migrate')
@with_appcontext
def quick_migrate():
    local_e = create_engine(current_app.config['ENGINE'])
    remote_e = create_engine(current_app.config['REMOTE_ENGINE'])
    with local_e.connect() as cnx:
        with remote_e.connect() as r_cnx:
            locations = cnx.execute("SELECT * FROM location order by id")
            locations = ", ".join([f"({l.id}, '{l.name}')" for l in locations])
            query = f"INSERT INTO location (id, name) VALUES {locations}"
            r_cnx.execute(query)
            print("Locations migrated")
            max_id = int(cnx.execute("SELECT MAX(id) FROM name").scalar())
            print(f"{max_id} names to migrate")
            num_iterations = (max_id // 100) + 1
            with Bar('Names...') as bar:
                for i in range(num_iterations):
                    lower = 100 * i
                    upper = 100 * (i+1)
                    names = cnx.execute(f"SELECT * FROM name WHERE id > {lower} AND id <= {upper}")
                    names = ", ".join([f"({n.id}, '{n.name}')" for n in names])
                    query = f"INSERT INTO name (id, name) VALUES {names}"
                    r_cnx.execute(query)
                    bar.next()
            max_id = int(cnx.execute("SELECT MAX(id) FROM data WHERE name_id IS NULL").scalar())
            print(f"{max_id} US totals to migrate")
            num_iterations = (max_id // 100) + 1
            with Bar('US Totals...') as bar:
                for i in range(num_iterations):
                    lower = 100 * i
                    upper = 100 * (i+1)
                    data = cnx.execute(f"SELECT * FROM data WHERE id > {lower} AND id <= {upper} AND name_id IS NULL")
                    data = ", ".join([f"({d.id}, {d.location_id}, {d.year}, {d.value}, '{d.sex}')" for d in data])
                    if data:
                        query = f"INSERT INTO data (id, location_id, year, value, sex) VALUES {data}"
                        r_cnx.execute(query)
                    bar.next()
            max_id = int(cnx.execute("SELECT MAX(id) FROM data").scalar())
            print(f"{max_id} data rows to migrate")
            num_iterations = (max_id // 100) + 1
            with Bar('Data...') as bar:
                for i in range(num_iterations):
                    lower = 100 * i
                    upper = 100 * (i+1)
                    data = cnx.execute(f"SELECT * FROM data WHERE id > {lower} AND id <= {upper} AND name_id IS NOT NULL")
                    data = ", ".join([f"({d.id}, {d.location_id}, {d.name_id}, {d.year}, {d.value}, '{d.sex}')" for d in data])
                    if data:
                        query = f"INSERT INTO data (id, location_id, name_id, year, value, sex) VALUES {data}"
                        r_cnx.execute(query)
                    bar.next()
    print("Migration complete.")