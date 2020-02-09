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


class Experiments(db.Model):
    __tablename__ = 'experiments'

    id = db.Column(BIGINT, primary_key = True)
    name = db.Column(VARCHAR(64), default = True, nullable = False)
    color = db.Column(VARCHAR(6), default = True, nullable = False)
    description = db.Column(TEXT, default = True, nullable = False)
    instructions = db.Column(TEXT)
    spare_answer_id = db.Column(BIGINT, default = True, nullable = True)
    tag = db.Column(VARCHAR(10), default = True, nullable = True)
    deliver_data = db.Column(SMALLINT, default = 0, nullable = False)
    samples = db.relationship('Samples', backref='experiments')
    kit_types_questions = db.relationship('KitTypesQuestions', secondary=kit_types_questions_X_experiments,
                                          backref=db.backref('experiments', lazy='dynamic'))

    def __init__(self, name, color, description, instructions, spare_answer_id, tag, deliver_data):
        self.name = name
        self.color = color
        self.description = description
        self.instructions = instructions
        self.spare_answer_id = spare_answer_id
        self.tag = tag
        self.deliver_data = deliver_data

    def __repr__(self):
        return '<id {}>'.format(self.id)