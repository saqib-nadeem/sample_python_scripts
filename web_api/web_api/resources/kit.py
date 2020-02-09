from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.models import Kits, db
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 

kit_fields = {
    'user': fields.Integer,
    'mailinglabel': fields.Integer,
    'assembled': fields.DateTime(default=None),
    'registered': fields.DateTime(default=None),
    'barcode': fields.String,
    'order_id': fields.Integer,
    'kit_type': fields.Integer,
    'survey_page': fields.Integer,
    'survey_completed': fields.DateTime(default=None),
    'registration_override': fields.Integer,
    'tubesReceived': fields.DateTime(default=None),
    'processed': fields.DateTime(default=None),
    'analyzed': fields.DateTime(default=None),
    'last_reminder': fields.DateTime(default=None),
    'uri': fields.Url('kit', absolute=True, scheme='http')
}

# KitListAPI
# shows a list of all kits, and lets you POST to add new kit
class KitListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type = int)
        self.reqparse.add_argument('mailinglabel', type = int)
        self.reqparse.add_argument('assembled', type = str)
        self.reqparse.add_argument('registered', type = str)
        self.reqparse.add_argument('barcode', type = str)
        self.reqparse.add_argument('order_id', type = int)
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('survey_page', type = str)
        self.reqparse.add_argument('survey_completed', type = str)
        self.reqparse.add_argument('registration_override', type = int)
        self.reqparse.add_argument('tubesReceived', type = str)
        self.reqparse.add_argument('processed', type = str)
        self.reqparse.add_argument('analyzed', type = str)
        self.reqparse.add_argument('last_reminder', type = str)
        super(KitListAPI, self).__init__()

    def get(self):
    	output = get_all_records(Kits, "kits")
        return {'data' : marshal(output, kit_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        user = args['user']
        mailinglabel = args['mailinglabel']
        assembled = args['assembled']
        registered = args['registered']
        barcode = args['barcode']
        order_id = args['order_id']
        kit_type = args['kit_type']
        survey_page = args['survey_page']
        survey_completed = args['survey_completed']
        registration_override = args['registration_override']
        tubesReceived = args['tubesReceived']
        processed = args['processed']
        analyzed = args['analyzed']
        last_reminder = args['last_reminder']

        kit = Kits(user, mailinglabel, assembled, registered, barcode, order_id, kit_type,
                   survey_page, survey_completed, registration_override, tubesReceived,
                   processed, analyzed, last_reminder)

        db.session.add(kit)
        db.session.commit()
        kit_id = kit.id
        return args, 201

# KitAPI
# show a single kit info and lets you update/delete them
class KitAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type = int)
        self.reqparse.add_argument('mailinglabel', type = int)
        self.reqparse.add_argument('assembled', type = str)
        self.reqparse.add_argument('registered', type = str)
        self.reqparse.add_argument('barcode', type = str)
        self.reqparse.add_argument('order_id', type = int)
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('survey_completed', type = str)
        self.reqparse.add_argument('registration_override', type = int)
        self.reqparse.add_argument('tubesReceived', type = str)
        self.reqparse.add_argument('processed', type = str)
        self.reqparse.add_argument('analyzed', type = str)
        self.reqparse.add_argument('last_reminder', type = str)
        super(KitAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(Kits, id, "kits")
        return {'data' : marshal(output, kit_fields)}

    def delete(self, id):
    	delete_record(Kits, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(Kits, id, args, "kits")
        return output, 201
