import datetime
from passlib.apps import custom_app_context as pwd_context

from flask.ext.mongoengine import MongoEngine
from mongoengine import *

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from angular_flask import app

db = MongoEngine(app)

class User(db.Document):

    username = StringField(max_length=50, required=True)
    password_hash = StringField(max_length=128)


    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 6000):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': str(self.id) })

    def get_id(self):
    	return str(self.id)

    @staticmethod
    def verify_auth_token(token):

    	s = Serializer(app.config['SECRET_KEY'])
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		return None
    	except BadSignature:
    		return None

    	user = User.objects(id=data['id']).first()
        return user