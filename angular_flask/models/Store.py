import datetime

from flask.ext.mongoengine import MongoEngine
from mongoengine import *

from angular_flask import app
from angular_flask.models.User import User
from angular_flask.models.BusinessType import BusinessType


db = MongoEngine(app)

class Store(db.Document):

    business_name = StringField(max_length=100, unique=True, required=True)
    about = StringField(max_length=1000, required=True)
    title = StringField(max_length=100)
    activated = BooleanField(required=True, default=False)
    published = BooleanField(required=True, default=False)
    address =  StringField(max_length=100)
    city =  StringField(max_length=100)
    email = EmailField(max_length=100)
    contact = StringField(max_length=100)
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    user = ReferenceField(User)
    url = URLField() 
    business_type = ReferenceField(BusinessType)

    def __unicode__(self):
    	return self.business_name    


    