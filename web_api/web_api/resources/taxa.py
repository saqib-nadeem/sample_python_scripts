from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import Taxa, db

taxa_fields = {
    'tax_rank': fields.String,
    'tax_name': fields.String,
    'tax_color': fields.String,
    'parent': fields.Integer,
    'superkingdom': fields.Integer,
    'reads': fields.Integer,
    'uri': fields.Url('taxon', absolute=True, scheme='http')
}

class TaxaListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tax_rank', type = str)
        self.reqparse.add_argument('tax_name', type = str)
        self.reqparse.add_argument('tax_color', type = str)
        self.reqparse.add_argument('parent', type = int)
        self.reqparse.add_argument('superkingdom', type = int)
        self.reqparse.add_argument('reads', type = int)

        super(TaxaListAPI, self).__init__()

    def get(self):
        output = get_all_records(Taxa, "taxa")
        return {'data' : marshal(output, taxa_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        
        tax_rank = args['tax_rank']
        tax_name = args['tax_name']
        tax_color = args['tax_color']
        parent = args['parent']
        superkingdom = args['superkingdom']
        reads = args['reads']
        
        new_row = Taxa(tax_rank, tax_name, tax_color, parent, superkingdom, reads)
        db.session.add(new_row)
        db.session.commit()
        new_row_id = new_row.id
        return args, 201


class TaxaAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('tax_rank', type = str)
        self.reqparse.add_argument('tax_name', type = str)
        self.reqparse.add_argument('tax_color', type = str)
        self.reqparse.add_argument('parent', type = int)
        self.reqparse.add_argument('superkingdom', type = int)
        self.reqparse.add_argument('reads', type = int)

        super(TaxaAPI, self).__init__()    

    def get(self, id):
        output = get_record_by_ID(Taxa, id, "taxa")
        return {'data' : marshal(output, taxa_fields)}

    def delete(self, id):
        delete_record(Taxa, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(Taxa, id, args, "taxa")
        return output, 201
