from flask import Blueprint

api = Blueprint('api',__name__, static_folder="../static", static_url_path='/static')

from . import auth
from . import current_state
from . import hist_state
from . import index
