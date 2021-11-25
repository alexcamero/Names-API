import json

from flask import (
    Blueprint, request
)

from application.legacy_functions import totals_legacy_graph

bp = Blueprint('legacy', __name__, url_prefix = '/legacy')


@bp.route('/graph', methods=['POST'])
def graph_data():
    min_year = int(request.form['min_year'])
    max_year = int(request.form['max_year'])
    if request.form['totals']:
        totals = totals_legacy_graph(min_year, max_year)
        return json.dumps(totals)