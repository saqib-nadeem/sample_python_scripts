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


class KitTypesQuestionsAnswers(db.Model):
    __tablename__ = 'kit_types_questions_answers'

    id = db.Column(BIGINT, primary_key = True)
    kit = db.Column(BIGINT, db.ForeignKey('kits.id'), nullable = False)
    kit_types_questions_answer_option = db.Column(BIGINT, db.ForeignKey('kit_types_questions_answer_options.id'), nullable = False)
    answer_int = db.Column(BIGINT, default = True, nullable = True)
    answer_decimal = db.Column(BIGINT, default = True, nullable = True)
    answer_text = db.Column(TEXT)

    def __init__(self, kit_types_questions_answer_option, kit, answer_int,
                 answer_decimal, answer_text):
        self.kit_types_questions_answer_option = kit_types_questions_answer_option
        self.kit = kit
        self.answer_int = answer_int
        self.answer_decimal = answer_decimal
        self.answer_text = answer_text

    def __repr__(self):
        return '<id {}>'.format(self.id)