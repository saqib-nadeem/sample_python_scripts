from flask import Flask

app = Flask(__name__)
app.config.from_object('angular_flask.settings')

# TODO: Remove view file and move user API to resources folder
from angular_flask import views

from angular_flask.models import User, Store, BusinessType
from angular_flask.resources import store, user, business_type
from angular_flask import routes
import angular_flask.common