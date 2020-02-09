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


class Samples(db.Model):
    __tablename__ = 'samples'

    id = db.Column(BIGINT, primary_key = True)
    vial_barcode = db.Column(VARCHAR(32), default = True, nullable = True)
    experiment = db.Column(BIGINT, db.ForeignKey('experiments.id'), nullable = False)
    assigned_kit = db.Column(TIMESTAMP)
    kit = db.Column(BIGINT, db.ForeignKey('kits.id'), nullable = False)
    assigned_vial = db.Column(TIMESTAMP)
    created = db.Column(TIMESTAMP, default = func.current_timestamp())
    processed = db.Column(TIMESTAMP)
    received = db.Column(TIMESTAMP)
    analyzed = db.Column(TIMESTAMP)
    query_exclude = db.Column(INTEGER, default = 0, nullable = False)
    collected = db.Column(TIMESTAMP)
    sequencing_revision = db.Column(BIGINT, nullable = False)
    lab_sample_loading = db.relationship('LabSampleLoading', backref='samples')
    results_taxoncount = db.relationship('ResultsTaxoncount', uselist=False, backref='samples')

    def __init__(self, vial_barcode, experiment, assigned_kit, kit, assigned_vial,
                 processed, received, analyzed, query_exclude, collected,
                 sequencing_revision):
        self.vial_barcode = vial_barcode
        self.experiment = experiment
        self.assigned_kit = assigned_kit
        self.kit = kit
        self.assigned_vial = assigned_vial
        self.processed = processed
        self.received = received
        self.analyzed = analyzed
        self.query_exclude = query_exclude
        self.collected = collected
        self.sequencing_revision = sequencing_revision

    def __repr__(self):
        return '<id {}>'.format(self.id)