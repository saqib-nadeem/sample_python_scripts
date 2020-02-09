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


class LabSampleLoading(db.Model):
    __tablename__ = 'lab_sample_loading'

    id = db.Column(BIGINT, primary_key = True)
    tubeId = db.Column(VARCHAR(255), nullable = False)
    PRID = db.Column(VARCHAR(255), nullable = False)
    Extraction_Rack_Number = db.Column(VARCHAR(255), nullable = False)
    Extraction_Rack_Loaction = db.Column(VARCHAR(255), nullable = False)
    Extraction_Rack_Scan_Time = db.Column(VARCHAR(255), nullable = False)
    pipeline_tracking_record = db.Column(BIGINT, db.ForeignKey('lab_pipeline_tracking.id'), nullable = False)
    originFileName = db.Column(VARCHAR(128), nullable = False)
    sample = db.Column(BIGINT, db.ForeignKey('samples.id'), nullable = False)
    taxondata_loaded = db.Column(TIMESTAMP)
    created = db.Column(TIMESTAMP, default = func.current_timestamp())
    pipeline_rev = db.Column(INTEGER, default = 1, nullable = False)
    latestRev2 = db.Column(INTEGER, default = 0, nullable = False)

    def __init__(self, tubeId, PRID, Extraction_Rack_Number, Extraction_Rack_Loaction,
                 Extraction_Rack_Scan_Time, pipeline_tracking_record, originFileName,
                 sample, taxondata_loaded, pipeline_rev, latestRev2):
        self.tubeId = tubeId
        self.PRID = PRID
        self.Extraction_Rack_Number = Extraction_Rack_Number
        self.Extraction_Rack_Loaction = Extraction_Rack_Loaction
        self.Extraction_Rack_Scan_Time = Extraction_Rack_Scan_Time
        self.pipeline_tracking_record = pipeline_tracking_record
        self.originFileName = originFileName
        self.sample = sample
        self.taxondata_loaded = taxondata_loaded
        self.pipeline_rev = pipeline_rev
        self.latestRev2 = latestRev2

    def __repr__(self):
        return '<id {}>'.format(self.id)