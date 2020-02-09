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


class KitTypesQuestionsAnswerOptions(db.Model):
    __tablename__ = 'kit_types_questions_answer_options'

    id = db.Column(BIGINT, primary_key = True)
    kit_type_question = db.Column(BIGINT, db.ForeignKey('kit_types_questions.id'), nullable = False)
    answer_text = db.Column(VARCHAR(256), nullable = False)
    answer_tooltip = db.Column(VARCHAR(256), nullable = False)
    answer_order = db.Column(INTEGER, default = True, nullable = True)
    answer_validation = db.Column(TEXT)
    kit_types_questions_answers = db.relationship('KitTypesQuestionsAnswers', backref='kit_types_questions_answer_options')

    def __init__(self, kit_type_question, answer_text, answer_tooltip, answer_order,
                 answer_validation):
        self.kit_type_question = kit_type_question
        self.answer_text = answer_text
        self.answer_tooltip = answer_tooltip
        self.answer_order = answer_order
        self.answer_validation = answer_validation

    def __repr__(self):
        return '<id {}>'.format(self.id)