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


class Taxa(db.Model):
    __tablename__ = 'taxa'
    
    id = db.Column(BIGINT, primary_key = True)
    tax_rank = db.Column(VARCHAR(128), default = True, nullable = True)
    tax_name = db.Column(VARCHAR(128), default = True, nullable = True)
    tax_color = db.Column(VARCHAR(12), default = True, nullable = True)
    parent = db.Column(BIGINT, default = True, nullable = True)
    superkingdom = db.Column(BIGINT, default = True, nullable = True)
    reads = db.Column(BIGINT, default = 0, nullable = False)
    results_taxoncount = db.relationship('ResultsTaxoncount', backref='taxa')
    taxon_infos = db.relationship('TaxonInfo', uselist=False, backref='taxa')

    def __init__(self, tax_rank, tax_name, tax_color, parent,
                 superkingdom, reads):
        self.tax_rank = tax_rank
        self.tax_name = tax_name
        self.tax_color = tax_color
        self.parent = parent
        self.superkingdom = superkingdom
        self.reads = reads

    def __repr__(self):

        return '<id {}>'.format(self.id)