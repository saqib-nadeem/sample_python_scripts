import datetime

from flask.ext.mongoengine import MongoEngine
from mongoengine import *

from angular_flask import app
from angular_flask.models.Store import Store

db = MongoEngine(app)

class Category(db.Document):

    name = StringField(max_length=200, required=True)
    description = StringField(max_length=1000, required=True)
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    store = ReferenceField(Store)

    def __unicode__(self):
    	return self.name 


    