from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import ResultsTaxoncount, db

results_taxoncount_fields = {
    'sample': fields.Integer,
    'ssr': fields.Integer,
    'taxon': fields.Integer,
    'count': fields.Integer,
    'avg': fields.Integer,
    'count_norm': fields.Integer,
    'disabled_sample': fields.Integer,
    'terminal_count': fields.Integer,
    'uri': fields.Url('result_taxoncount', absolute=True, scheme='http')
}

class ResultsTaxoncountListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sample', type = int)
        self.reqparse.add_argument('ssr', type = int)
        self.reqparse.add_argument('taxon', type = int)
        self.reqparse.add_argument('count', type = int)
        self.reqparse.add_argument('avg', type = int)
        self.reqparse.add_argument('count_norm', type = int)
        self.reqparse.add_argument('disabled_sample', type = int)
        self.reqparse.add_argument('terminal_count', type = int)
        super(ResultsTaxoncountListAPI, self).__init__()

    def get(self):
        output = get_all_records(ResultsTaxoncount, "results_taxoncount")
        return {'data' : marshal(output, results_taxoncount_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        
        sample = args['sample']
        ssr = args['ssr']
        taxon = args['taxon']
        count = args['count']
        avg = args['avg']
        count_norm = args['count_norm']
        disabled_sample = args['disabled_sample']
        terminal_count = args['terminal_count']

        new_row = ResultsTaxoncount(sample, ssr, taxon, count, avg, count_norm, disabled_sample, terminal_count)
        db.session.add(new_row)
        db.session.commit()
        new_row_id = new_row.id
        return new_row_id, 201

# TaxaAPI
# show a single taxa type info and lets you update/delete them
class ResultsTaxoncountAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sample', type = int)
        self.reqparse.add_argument('ssr', type = int)
        self.reqparse.add_argument('taxon', type = int)
        self.reqparse.add_argument('count', type = int)
        self.reqparse.add_argument('avg', type = int)
        self.reqparse.add_argument('count_norm', type = int)
        self.reqparse.add_argument('disabled_sample', type = int)
        self.reqparse.add_argument('terminal_count', type = int)
        
        super(ResultsTaxoncountAPI, self).__init__()    

    def get(self, id):
        output = get_record_by_ID(ResultsTaxoncount, id, "results_taxoncount")
        return {'data' : marshal(output, results_taxoncount_fields)}

    def delete(self, id):
        delete_record(ResultsTaxoncount, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(ResultsTaxoncount, id, args, "results_taxoncount")
        return output, 201
