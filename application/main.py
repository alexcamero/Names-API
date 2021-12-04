import json

from flask import (
    Blueprint, request
)

bp = Blueprint('main', __name__, url_prefix = '/api')


@bp.route('/', methods=['POST'])
def get_data():
    names = json.loads(request.form['names'])
    print(names)
    print(type(names))
    return "all done, thanks"