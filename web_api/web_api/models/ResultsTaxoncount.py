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


class ResultsTaxoncount(db.Model):
    __tablename__ = 'results_taxoncount'

    id = db.Column(BIGINT, primary_key = True)
    sample = db.Column(BIGINT, db.ForeignKey('samples.id'), nullable = False)
    ssr = db.Column(BIGINT, default = True, nullable = True)
    taxon = db.Column(BIGINT, db.ForeignKey('taxa.id'), nullable = False)
    count = db.Column(BIGINT, default = True, nullable = True)
    avg = db.Column(BIGINT, default = True, nullable = True)
    created = db.Column(TIMESTAMP, default = func.current_timestamp())
    count_norm = db.Column(BIGINT, default = True, nullable = True)
    disabled_sample = db.Column(BIGINT, default = True, nullable = True)
    terminal_count = db.Column(BIGINT, nullable = False)

    def __init__(self, sample, ssr, taxon, count, avg, count_norm,
                 disabled_sample, terminal_count):
        self.sample = sample
        self.ssr = ssr
        self.taxon = taxon
        self.count = count
        self.avg = avg
        self.count_norm = count_norm
        self.disabled_sample = disabled_sample
        self.terminal_count = terminal_count

    def __repr__(self):
        return '<id {}>'.format(self.id)