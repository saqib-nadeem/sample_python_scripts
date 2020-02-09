import datetime

from flask.ext.mongoengine import MongoEngine
from mongoengine import *

from angular_flask import app

db = MongoEngine(app)

class BusinessType(db.Document):

    name = StringField(max_length=200, required=True)
    created_at = DateTimeField(default=datetime.datetime.now, required=True)

    def __unicode__(self):
    	return self.name 


    