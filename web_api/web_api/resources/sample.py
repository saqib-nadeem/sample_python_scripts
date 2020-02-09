from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import Samples, db

sample_fields = {
    'vial_barcode': fields.Integer,
    'experiment': fields.Integer,
    'assigned_kit': fields.DateTime,
    'kit': fields.Integer,
    'assigned_vial': fields.DateTime,
    'processed': fields.DateTime,
    'received': fields.DateTime,
    'analyzed': fields.DateTime,
    'query_exclude': fields.Integer,
    'collected': fields.DateTime,
    'sequencing_revision': fields.Integer,
    'uri': fields.Url('sample', absolute=True, scheme='http')
}

# SampleListAPI
# shows a list of all samples, and lets you POST to add new sample
class SampleListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('vial_barcode', type = str)
        self.reqparse.add_argument('experiment', type = int)
        self.reqparse.add_argument('assigned_kit', type = str)
        self.reqparse.add_argument('kit', type = int)
        self.reqparse.add_argument('assigned_vial', type = str)
        self.reqparse.add_argument('processed', type = str)
        self.reqparse.add_argument('received', type = str)
        self.reqparse.add_argument('analyzed', type = str)
        self.reqparse.add_argument('query_exclude', type = int)
        self.reqparse.add_argument('collected', type = str)
        self.reqparse.add_argument('sequencing_revision', type = int)
        
        super(SampleListAPI, self).__init__()    

    def get(self):
        output = get_all_records(Samples, "samples")
        return {'data' : marshal(output, sample_fields)}

    def post(self):
        args = self.reqparse .parse_args()
        vial_barcode = args['vial_barcode']
        experiment = args['experiment']
        assigned_kit = args['assigned_kit']
        kit = args['kit']
        assigned_vial = args['assigned_vial']
        processed = args['processed']
        received = args['received']
        analyzed = args['analyzed']
        query_exclude = args['query_exclude']
        collected = args['collected']
        sequencing_revision = args['sequencing_revision']

        sample = Samples(vial_barcode, experiment, assigned_kit, kit, assigned_vial, processed,
                         received, analyzed, query_exclude, collected, sequencing_revision)
        db.session.add(sample)
        db.session.commit()
        sample_id = sample.id
        return args, 201
        
# SampleAPI
# show a single sample info and lets you delete them
class SampleAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('vial_barcode', type = str)
        self.reqparse.add_argument('experiment', type = int)
        self.reqparse.add_argument('assigned_kit', type = str)
        self.reqparse.add_argument('kit', type = int)
        self.reqparse.add_argument('assigned_vial', type = str)
        self.reqparse.add_argument('processed', type = str)
        self.reqparse.add_argument('received', type = str)
        self.reqparse.add_argument('analyzed', type = str)
        self.reqparse.add_argument('query_exclude', type = int)
        self.reqparse.add_argument('collected', type = str)
        self.reqparse.add_argument('sequencing_revision', type = int)
        super(SampleAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(Samples, id, "samples")
        return {'data' : marshal(output, sample_fields)}

    def delete(self, id):
    	delete_record(Samples, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(Samples, id, args, "samples")
        return output, 201 