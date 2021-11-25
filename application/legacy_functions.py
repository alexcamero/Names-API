from application.db import get_engine



def totals_legacy_graph(min_year, max_year):
    states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Washington DC', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana','Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
    engine = get_engine()
    with engine.connect() as cnx:
        us_totals = cnx.execute(f"SELECT SUM(d.value) AS total FROM data d INNER JOIN location l ON d.location_id = l.id WHERE l.name = 'United States' AND d.year BETWEEN {min_year} AND {max_year} AND d.name_id IS NULL GROUP BY d.year ORDER BY d.year")
        states_string = ', '.join([f"'{s}'" for s in states])
        state_totals = cnx.execute(f"SELECT d.year - {min_year} AS first_index, l.name AS location, SUM(d.value) AS total FROM data d INNER JOIN location l ON d.location_id = l.id WHERE l.name IN ({states_string}) AND d.year BETWEEN {min_year} AND {max_year} GROUP BY d.year, l.name")
    totals = []
    for row in us_totals:
        totals.append([int(row.total)] + [0 for _ in range(len(states))])
    for row in state_totals:
        totals[int(row.first_index)][states.index(row.location) + 1] = int(row.total)
    return totals