import datetime

from flask.ext.mongoengine import MongoEngine
from mongoengine import *

from angular_flask import app
from angular_flask.models.User import User
from angular_flask.models.Category import Category

db = MongoEngine(app)

class Product(db.Document):

    name = StringField(max_length=100, required=True)
    description = StringField(max_length=1000, required=False)
    price = FloatField(required=True)    
    image = StringField(max_length=256, required=True)
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    category = ReferenceField(Category)

    def __unicode__(self):
    	return self.name    


    