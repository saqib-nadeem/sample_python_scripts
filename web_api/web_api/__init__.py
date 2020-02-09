import os
import json
from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for

app = Flask(__name__)
app.config.from_object('web_api.settings')
db = SQLAlchemy(app)

import web_api.models
import web_api.routes
import web_api.common
import web_api.resources

