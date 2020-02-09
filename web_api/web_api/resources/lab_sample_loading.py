from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import LabSampleLoading, db

lab_sample_loading_fields = {
    'tubeId': fields.String,
    'PRID': fields.String,
    'Extraction_Rack_Number': fields.String,
    'Extraction_Rack_Loaction': fields.String,
    'Extraction_Rack_Scan_Time': fields.String,
    'pipeline_tracking_record': fields.Integer,
    'originFileName': fields.String,
    'sample': fields.Integer,
    'taxondata_loaded': fields.DateTime,
    'pipeline_rev': fields.Integer,
    'latestRev2': fields.Integer,

    'uri': fields.Url('lab_sample_loading', absolute=True, scheme='http')
}

# LabSampleLoadingListAPI
# shows a list of all lab_sample_loading, and lets you POST to add new lab_sample_loading
class LabSampleLoadingListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tubeId', type = str)
        self.reqparse.add_argument('PRID', type = str)
        self.reqparse.add_argument('Extraction_Rack_Number', type = str)
        self.reqparse.add_argument('Extraction_Rack_Loaction', type = str)
        self.reqparse.add_argument('Extraction_Rack_Scan_Time', type = str)
        self.reqparse.add_argument('pipeline_tracking_record', type = int)
        self.reqparse.add_argument('originFileName', type = str)
        self.reqparse.add_argument('sample', type = int)        
        self.reqparse.add_argument('taxondata_loaded', type = str)
        self.reqparse.add_argument('pipeline_rev', type = int)
        self.reqparse.add_argument('latestRev2', type = int)       
        super(LabSampleLoadingListAPI, self).__init__()

    def get(self):
    	output = get_all_records(LabSampleLoading, "lab_sample_loading")
        return {'data' : marshal(output, lab_sample_loading_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        tubeId = args['tubeId']
        PRID = args['PRID']
        Extraction_Rack_Number = args['Extraction_Rack_Number']
        Extraction_Rack_Loaction = args['Extraction_Rack_Loaction']
        Extraction_Rack_Scan_Time = args['Extraction_Rack_Scan_Time']
        pipeline_tracking_record = args['pipeline_tracking_record']
        originFileName = args['originFileName']
        sample = args['sample']
        taxondata_loaded = args['taxondata_loaded']
        pipeline_rev = args['pipeline_rev']
        latestRev2 = args['latestRev2']

        lab_sample_loading = LabSampleLoading(tubeId, PRID, Extraction_Rack_Number, Extraction_Rack_Loaction,
                         Extraction_Rack_Scan_Time, pipeline_tracking_record, originFileName,
                         sample, taxondata_loaded, pipeline_rev, latestRev2)
        db.session.add(lab_sample_loading)
        db.session.commit()
        lab_sample_loading_id = lab_sample_loading.id
        return args, 201
        
# LabSampleLoadingAPI
# show a single lab_sample_loading info and lets you update/delete them
class LabSampleLoadingAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tubeId', type = str)
        self.reqparse.add_argument('PRID', type = str)
        self.reqparse.add_argument('Extraction_Rack_Number', type = str)
        self.reqparse.add_argument('Extraction_Rack_Loaction', type = str)
        self.reqparse.add_argument('Extraction_Rack_Scan_Time', type = str)
        self.reqparse.add_argument('pipeline_tracking_record', type = int)
        self.reqparse.add_argument('originFileName', type = str)
        self.reqparse.add_argument('sample', type = int)        
        self.reqparse.add_argument('taxondata_loaded', type = str)
        self.reqparse.add_argument('pipeline_rev', type = int)
        self.reqparse.add_argument('latestRev2', type = int)       
        super(LabSampleLoadingAPI, self).__init__()

    def get(self, id):
    	output = get_record_by_ID(LabSampleLoading, id, "lab_sample_loading")
        return {'data' : marshal(output, lab_sample_loading_fields)}

    def delete(self, id):
    	delete_record(LabSampleLoading, id)     
    	return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(LabSampleLoading, id, args, "lab_sample_loading")
        return output, 201