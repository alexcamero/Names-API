import json

from flask import (
    Blueprint, request
)

from application.models import Name, Location, Data
from application.db import get_engine

bp = Blueprint('legacy', __name__, url_prefix = '/legacy')

def return_totals(min_year, max_year):
    engine = get_engine()
    with engine.connect() as cnx:
        us_totals = cnx.execute(f"SELECT d.year - {min_year} AS first_index, d.value AS total FROM data d INNER JOIN location l ON d.location_id = l.id WHERE l.name = 'United States' AND d.year BETWEEN {min_year} AND {max_year} ORDER BY d.year")
        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Washington DC', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana','Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        states = ', '.join([f"'{s}'" for s in states])
        state_totals = cnx.execute(f"SELECT d.year - {min_year} AS first_index, l.name AS location, SUM(d.value) AS total FROM data d INNER JOIN location l ON d.location_id = l.id WHERE l.name IN ({states}) AND d.year BETWEEN {min_year} AND {max_year} GROUP BY d.year, l.name")
    totals = []
    for row in us_totals:
        totals.append([row.total])
    for state in states:
        for row in state_totals:
            if row.location == state:
                totals[row.first_index].append(row.total)
    return totals


@bp.route('/graph', methods=('POST'))
def graph_data():
    min_year = request.form['min_year']
    max_year = request.form['max_year']
    if request.form['totals'] == 1:
        totals = return_totals(min_year, max_year)
        return json.dumps(totals)