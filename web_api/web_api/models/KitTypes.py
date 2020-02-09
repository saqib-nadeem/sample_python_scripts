import datetime
from web_api import app, db
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import \
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
    DOUBLE_PRECISION, ENUM, FLOAT, HSTORE, INET, INTEGER, \
    INTERVAL, JSON, JSONB, MACADDR, NUMERIC, OID, REAL, SMALLINT, TEXT, \
    TIME, TIMESTAMP, UUID, VARCHAR, INT4RANGE, INT8RANGE, NUMRANGE, \
    DATERANGE, TSRANGE, TSTZRANGE, TSVECTOR


class KitTypes(db.Model):
    __tablename__ = 'kit_types'
    
    id = db.Column(BIGINT, primary_key = True)
    name = db.Column(VARCHAR(128), nullable = False)
    description = db.Column(TEXT, nullable = False)
    welcome_screen = db.Column(TEXT, nullable = False)
    finish_screen = db.Column(TEXT)
    
    def __init__(self, name, description, welcome_screen, finish_screen):
        self.name = name
        self.description = description
        self.welcome_screen = welcome_screen
        self.finish_screen = finish_screen

    def __repr__(self):
        return '<id {}>'.format(self.id)