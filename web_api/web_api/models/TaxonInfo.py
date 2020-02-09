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


class TaxonInfo(db.Model):
    __tablename__ = 'taxon_info'

    id = db.Column(BIGINT, primary_key = True)
    taxon = db.Column(BIGINT, db.ForeignKey('taxa.id'), nullable = False)
    description_1 = db.Column(VARCHAR(256), default = True, nullable = True)
    description_2 = db.Column(VARCHAR(4096), default = True, nullable = True)
    description_3 = db.Column(TEXT)

    def __init__(self, taxon, description_1, description_2, description_3):
        self.taxon = taxon
        self.description_1 = description_1
        self.description_2 = description_2
        self.description_3 = description_3

    def __repr__(self):
        return '<id {}>'.format(self.id)