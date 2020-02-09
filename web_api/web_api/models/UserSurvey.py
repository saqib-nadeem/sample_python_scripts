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


class UserSurvey(db.Model):
    __tablename__ = 'user_survey'

    id = db.Column(BIGINT, primary_key = True)
    user = db.Column(BIGINT, db.ForeignKey('user.id'), nullable = False)
    dob = db.Column(VARCHAR(128), nullable = False)
    city_and_country = db.Column(VARCHAR(128), nullable = False)
    gender = db.Column(VARCHAR(128), nullable = False)
    race = db.Column(VARCHAR(128), nullable = False)
    allow_data_comparison = db.Column(BOOLEAN, default = False)
    term_of_service = db.Column(BOOLEAN, default = False)
    privacy_policy = db.Column(BOOLEAN, default = False)
    induction_completed = db.Column(BOOLEAN, default = False)
    service_consent = db.Column(BOOLEAN, default = False)
    consent_on_file = db.Column(BOOLEAN, default = False) 
    record_created = db.Column(TIMESTAMP, default = func.current_timestamp(), nullable = False)   

    def __init__(self, user, dob, city_and_country, gender, race, allow_data_comparison, term_of_service,
                 privacy_policy, induction_completed, service_consent):        
        self.user = user
        self.dob = dob
        self.city_and_country = city_and_country
        self.gender = gender
        self.race = race
        self.allow_data_comparison = allow_data_comparison
        self.privacy_policy = privacy_policy
        self.induction_completed = induction_completed 
        self.service_consent = service_consent

    def __repr__(self):
        return '<id {}>'.format(self.id)    
