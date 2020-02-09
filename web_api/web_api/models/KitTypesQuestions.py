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


kit_types_questions_X_experiments = db.Table('kit_types_questions_X_experiments',
    db.Column('kit_types_question', BIGINT, db.ForeignKey('kit_types_questions.id')),
    db.Column('experiment', BIGINT, db.ForeignKey('experiments.id')))


class KitTypesQuestions(db.Model):
    __tablename__ = 'kit_types_questions'

    id = db.Column(BIGINT, primary_key = True)
    kit_type = db.Column(BIGINT, db.ForeignKey('kit_types.id'), nullable = False)
    question_text = db.Column(TEXT, nullable = False)
    question_type = db.Column(INTEGER, default = True, nullable = True)
    question_order = db.Column(INTEGER, nullable = False)
    page = db.Column(INTEGER, default = True, nullable = True)
    show_number = db.Column(SMALLINT, default = 1, nullable = False)
    requiredFilterPermission = db.Column(INTEGER, default = 15, nullable = False)
    kit_types_questions_answer_options = db.relationship('KitTypesQuestionsAnswerOptions', backref='kit_types_questions')

    def __init__(self, kit_type, question_text, question_type, question_order,
                 page, show_number, requiredFilterPermission):
        self.kit_type = kit_type
        self.question_text = question_text
        self.question_type = question_type
        self.question_order = question_order
        self.page = page
        self.show_number = show_number
        self.requiredFilterPermission = requiredFilterPermission

    def __repr__(self):
        return '<id {}>'.format(self.id)


