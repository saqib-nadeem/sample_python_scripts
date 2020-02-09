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


class LabPipelineTracing(db.Model):
    __tablename__ = 'lab_pipeline_tracking'

    id = db.Column(BIGINT, primary_key = True)
    PRID = db.Column(VARCHAR(255), nullable = False)
    StartTime = db.Column(VARCHAR(255), nullable = False)
    primerPlateId = db.Column(VARCHAR(255), nullable = False)
    PCRSetupStartTime = db.Column(VARCHAR(255), nullable = False)
    PCRPlateBarcode = db.Column(VARCHAR(255), nullable = False)
    ExtractStorageTime = db.Column(VARCHAR(255), nullable = False)
    ThermocycleStartTime = db.Column(VARCHAR(255), nullable = False)
    PCRProductTubeId = db.Column(VARCHAR(255), nullable = False)
    PCRProductScanTime = db.Column(VARCHAR(255), nullable = False)
    qBitData = db.Column(TEXT, nullable = False)
    DCCPlateStorageTime = db.Column(VARCHAR(255), nullable = False)
    labChippedTubeId = db.Column(VARCHAR(255), nullable = False)
    labChippedProductScanTime = db.Column(VARCHAR(255), nullable = False)
    PCRProductTubeStorageTime = db.Column(VARCHAR(255), nullable = False)
    FinalLibraryAliquatTime = db.Column(VARCHAR(255), nullable = False)
    labChippedTubeStorageTime = db.Column(VARCHAR(255), nullable = False)
    seqRunName = db.Column(VARCHAR(255), nullable = False)
    seqRunId = db.Column(BIGINT, nullable = False)
    active_at_robot = db.Column(INTEGER, default = True, nullable = True)
    lab_sample_loading = db.relationship('LabSampleLoading', backref='lab_pipeline_tracking')

    def __init__(self, PRID, StartTime, primerPlateId, PCRSetupStartTime, PCRPlateBarcode, 
                 ExtractStorageTime, ThermocycleStartTime, PCRProductTubeId, PCRProductScanTime,
                 qBitData, DCCPlateStorageTime, labChippedTubeId, labChippedProductScanTime, 
                 PCRProductTubeStorageTime, FinalLibraryAliquatTime, labChippedTubeStorageTime, 
                 seqRunName, seqRunId, active_at_robot):
        self.PRID = PRID
        self.StartTime = StartTime
        self.primerPlateId = primerPlateId
        self.PCRSetupStartTime = PCRSetupStartTime
        self.PCRPlateBarcode = PCRPlateBarcode
        self.ExtractStorageTime = ExtractStorageTime
        self.ThermocycleStartTime = ThermocycleStartTime
        self.PCRProductTubeId = PCRProductTubeId
        self.PCRProductScanTime = PCRProductScanTime
        self.qBitData = qBitData
        self.DCCPlateStorageTime = DCCPlateStorageTime
        self.labChippedTubeId = labChippedTubeId
        self.labChippedProductScanTime = labChippedProductScanTime
        self.PCRProductTubeStorageTime = PCRProductTubeStorageTime
        self.FinalLibraryAliquatTime = FinalLibraryAliquatTime
        self.labChippedTubeStorageTime = labChippedTubeStorageTime
        self.seqRunName = seqRunName
        self.seqRunId = seqRunId
        self.active_at_robot = active_at_robot

    def __repr__(self):
        return '<id {}>'.format(self.id)