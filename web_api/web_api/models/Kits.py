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


class Kits(db.Model):
    __tablename__ = 'kits'

    id = db.Column(BIGINT, primary_key = True)
    user = db.Column(BIGINT, db.ForeignKey('users.id'), nullable = False )
    mailinglabel = db.Column(BIGINT, default = 0, nullable = True)
    record_created = db.Column(TIMESTAMP, default = func.current_timestamp(), nullable = False)
    assembled = db.Column(TIMESTAMP)
    registered = db.Column(TIMESTAMP)
    barcode = db.Column(VARCHAR(9), default = True, nullable = True)
    order_id = db.Column(BIGINT, default = 0, nullable = True)
    kit_type = db.Column(BIGINT, db.ForeignKey('kit_types.id'), nullable = False)
    survey_page = db.Column(INTEGER, default = 0, nullable = False)
    survey_completed = db.Column(TIMESTAMP)
    registration_override = db.Column(INTEGER, default = 0, nullable = False)
    tubesReceived = db.Column(TIMESTAMP)
    processed = db.Column(TIMESTAMP)
    analyzed = db.Column(TIMESTAMP)
    last_reminder = db.Column(TIMESTAMP)
    samples = db.relationship('Samples', backref = 'kits')
    kit_types_questions_answers = db.relationship('KitTypesQuestionsAnswers', backref = 'kits')

    def __init__(self, user, mailinglabel, assembled, registered,
                 barcode, order_id, kit_type, survey_page, survey_completed,
                 registration_override, tubesReceived, processed, analyzed,
                 last_reminder):
        self.user = user
        self.mailinglabel = mailinglabel
        self.assembled = assembled
        self.registered = registered
        self.barcode = barcode
        self.order_id = order_id
        self.kit_type = kit_type
        self.survey_page = survey_page
        self.survey_completed = survey_completed
        self.registration_override = registration_override
        self.tubesReceived = tubesReceived
        self.processed = processed
        self.analyzed = analyzed
        self.last_reminder = last_reminder

    def __repr__(self):
        return '<id {}>'.format(self.id)