from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import LabPipelineTracing, db

lab_pipeline_tracking_fields = {
    'PRID': fields.String,
    'StartTime': fields.String,
    'primerPlateId': fields.String,
    'PCRSetupStartTime': fields.String,
    'PCRPlateBarcode': fields.String,
    'PCRPlateBarcode': fields.String,
    'ExtractStorageTime': fields.String,
    'ThermocycleStartTime': fields.String,
    'PCRProductTubeId': fields.String,
    'PCRProductScanTime': fields.String,
    'qBitData': fields.String,
    'DCCPlateStorageTime': fields.String,
    'labChippedTubeId': fields.String,
    'labChippedProductScanTime': fields.String,
    'PCRProductTubeStorageTime': fields.Integer,
    'FinalLibraryAliquatTime': fields.String,
    'labChippedTubeStorageTime': fields.String,
    'seqRunName': fields.String,
    'seqRunId': fields.Integer,
    'active_at_robot': fields.Integer,
                
    'uri': fields.Url('lab_pipeline_tracking', absolute=True, scheme='http')
}


# LabPipelineTracingListAPI
# shows a list of all lab_pipeline_tracking, and lets you POST to add new lab_pipeline_tracking
class LabPipelineTracingListAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('PRID', type = str)
        self.reqparse.add_argument('StartTime', type = str)
        self.reqparse.add_argument('primerPlateId', type = str)
        self.reqparse.add_argument('PCRSetupStartTime', type = str)
        self.reqparse.add_argument('PCRPlateBarcode', type = str)
        self.reqparse.add_argument('ExtractStorageTime', type = str)
        self.reqparse.add_argument('ThermocycleStartTime', type = str)
        self.reqparse.add_argument('PCRProductTubeId', type = str)        
        self.reqparse.add_argument('PCRProductScanTime', type = str)
        self.reqparse.add_argument('qBitData', type = str)
        self.reqparse.add_argument('DCCPlateStorageTime', type = str)
        self.reqparse.add_argument('labChippedTubeId', type = str)
        self.reqparse.add_argument('labChippedProductScanTime', type = str)
        self.reqparse.add_argument('PCRProductTubeStorageTime', type = int)        
        self.reqparse.add_argument('FinalLibraryAliquatTime', type = str)
        self.reqparse.add_argument('labChippedTubeStorageTime', type = str)
        self.reqparse.add_argument('seqRunName', type = str)
        self.reqparse.add_argument('seqRunId', type = int)
        self.reqparse.add_argument('active_at_robot', type = int)                     
        super(LabPipelineTracingListAPI, self).__init__()

    def get(self):
    	output = get_all_records(LabPipelineTracing, "lab_pipeline_tracking")
        return {'data' : marshal(output, lab_pipeline_tracking_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        PRID = args['PRID']
        StartTime = args['StartTime']
        primerPlateId = args['primerPlateId']
        PCRSetupStartTime = args['PCRSetupStartTime']
        PCRPlateBarcode = args['PCRPlateBarcode']
        ExtractStorageTime = args['ExtractStorageTime']
        ThermocycleStartTime = args['ThermocycleStartTime']
        PCRProductTubeId = args['PCRProductTubeId']
        PCRProductScanTime = args['PCRProductScanTime']
        qBitData = args['qBitData']
        DCCPlateStorageTime = args['DCCPlateStorageTime']
        labChippedTubeId = args['labChippedTubeId']
        labChippedProductScanTime = args['labChippedProductScanTime']
        PCRProductTubeStorageTime = args['PCRProductTubeStorageTime']
        FinalLibraryAliquatTime = args['FinalLibraryAliquatTime']
        labChippedTubeStorageTime = args['labChippedTubeStorageTime']
        seqRunName = args['seqRunName']
        seqRunId = args['seqRunId']
        active_at_robot = args['active_at_robot']       

        lab_pipeline_tracking = LabPipelineTracing(PRID, StartTime, primerPlateId, PCRSetupStartTime, PCRPlateBarcode, 
					                               ExtractStorageTime, ThermocycleStartTime, PCRProductTubeId, PCRProductScanTime,
					                               qBitData, DCCPlateStorageTime, labChippedTubeId, labChippedProductScanTime, 
					                               PCRProductTubeStorageTime, FinalLibraryAliquatTime, labChippedTubeStorageTime, 
					                               seqRunName, seqRunId, active_at_robot)
        db.session.add(lab_pipeline_tracking)
        db.session.commit()
        lab_pipeline_tracking_id = lab_pipeline_tracking.id
        return args, 201
        
# LabPipelineTracingAPI
# show a single lab_pipeline_tracking info and lets you update/delete them
class LabPipelineTracingAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('PRID', type = str)
        self.reqparse.add_argument('StartTime', type = str)
        self.reqparse.add_argument('primerPlateId', type = str)
        self.reqparse.add_argument('PCRSetupStartTime', type = str)
        self.reqparse.add_argument('PCRPlateBarcode', type = str)
        self.reqparse.add_argument('ExtractStorageTime', type = str)
        self.reqparse.add_argument('ThermocycleStartTime', type = str)
        self.reqparse.add_argument('PCRProductTubeId', type = str)        
        self.reqparse.add_argument('PCRProductScanTime', type = str)
        self.reqparse.add_argument('qBitData', type = str)
        self.reqparse.add_argument('DCCPlateStorageTime', type = str)
        self.reqparse.add_argument('labChippedTubeId', type = str)
        self.reqparse.add_argument('labChippedProductScanTime', type = str)
        self.reqparse.add_argument('PCRProductTubeStorageTime', type = int)        
        self.reqparse.add_argument('FinalLibraryAliquatTime', type = str)
        self.reqparse.add_argument('labChippedTubeStorageTime', type = str)
        self.reqparse.add_argument('seqRunName', type = str)
        self.reqparse.add_argument('seqRunId', type = int)
        self.reqparse.add_argument('active_at_robot', type = int)                     
        super(LabPipelineTracingAPI, self).__init__()	

    def get(self, id):
    	output = get_record_by_ID(LabPipelineTracing, id, "lab_pipeline_tracking")
        return {'data' : marshal(output, lab_pipeline_tracking_fields)}

    def delete(self, id):
    	delete_record(LabPipelineTracing, id)     
    	return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(LabPipelineTracing, id, args, "lab_pipeline_tracking")
        return output, 201
