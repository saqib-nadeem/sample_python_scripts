from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal
from flask.ext.security import login_required, auth_token_required, roles_accepted, roles_required

from web_api.resources import auth
from web_api.models import KitTypes, db
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api import app


kit_type_fields = {
    'name': fields.String,
    'description': fields.String,	
    'welcome_screen': fields.String,
    'finish_screen': fields.String,
    'uri': fields.Url('kit_type', absolute=True, scheme='http')
}

# KitTypeListAPI
# shows a list of all kit types, and lets you POST to add new kit type
class KitTypeListAPI(Resource):
	decorators = [auth_token_required]

	def __init__(self):
	    self.reqparse = reqparse.RequestParser()
	    self.reqparse.add_argument('name', type = str)
	    self.reqparse.add_argument('description', type = str)
	    self.reqparse.add_argument('welcome_screen', type = str)
	    self.reqparse.add_argument('finish_screen', type = str)
	    super(KitTypeListAPI, self).__init__()

	def get(self):
		output = get_all_records(KitTypes, "kit_types")
		return {'data' : marshal(output, kit_type_fields)}

	def post(self):
	    args = self.reqparse.parse_args()
	    name = args['name']
	    description = args['description']
	    welcome_screen = args['welcome_screen']
	    finish_screen = args['finish_screen']
	    kit_type = KitTypes(name, description, welcome_screen, finish_screen)
	    db.session.add(kit_type)
	    db.session.commit()
	    kit_type_id = kit_type.id
	    return args, 201

# KitAPI
# show a single kit type info and lets you update/delete them
class KitTypeAPI(Resource):
	decorators = [auth_token_required]
	
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('name', type = str)
		self.reqparse.add_argument('description', type = str)
		self.reqparse.add_argument('welcome_screen', type = str)
		self.reqparse.add_argument('finish_screen', type = str)
		super(KitTypeAPI, self).__init__()

	def get(self, id):
		output = get_record_by_ID(KitTypes, id, "kit_types")
		return { 'data' : marshal(output, kit_type_fields) }

	def delete(self, id):
		delete_record(KitTypes, id)     
		return '', 204

	def put(self, id):
	    args = self.reqparse.parse_args()
	    output = update_record(KitTypes, id, args, "kit_types")
	    return output, 201


#POST
#curl -u user:uBiome http://localhost:5000/kit_types -d "name=Bowel Condition&description=This is the kit for the bowel condition uBiome.&welcome_screen=welcome screen styling text&finish_screen=finish screen styling text." -X POST -v
#PUT
#curl -u user:uBiome http://localhost:5000/kit_types/id -d "name=Bowel Condition&description=This is the kit for the bowel condition uBiome.&welcome_screen=welcome screen styling text&finish_screen=finish screen styling text." -X PUT -v
#curl -u user:uBiome http://localhost:5000/kit_types -d "name=Bowel Condition&description=This is the kit for the bowel condition uBiome.&welcome_screen=welcome screen styling text&finish_screen=finish screen styling text." -X POST -v
#curl -H "Authentication-Token: WyIxIiwiOGViNTEyZmJjYzVkM2I5ZDdiYWQ2NWM0NTBjNjVjYzQiXQ.Bzl7nA.SERdG_5T1lIs9ignG9MY6RmyKhw" http://localhost:5000/api/v0/kit_types (GET ALL)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types/2 (GET ONE)
#curl -u admin:uBiome http://localhost:5000/api/v0/kit_types/2 -X DELETE -v 