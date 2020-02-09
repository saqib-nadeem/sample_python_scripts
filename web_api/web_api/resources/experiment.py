from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.models import Experiments, db
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 

experiment_fields = {
    'name': fields.String,
    'color': fields.String,
    'description': fields.String,
    'instructions': fields.String,
    'spare_answer_id': fields.Integer,
    'tag': fields.String,
    'deliver_data': fields.Integer,    
    'uri': fields.Url('experiment', absolute=True, scheme='http')
    }

# ExperimentListAPI
# shows a list of all experiments, and lets you POST to add new experiment
class ExperimentListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str)
        self.reqparse.add_argument('color', type = str)
        self.reqparse.add_argument('description', type = str)
        self.reqparse.add_argument('instructions', type = str)
        self.reqparse.add_argument('spare_answer_id', type = int)
        self.reqparse.add_argument('tag', type = str)
        self.reqparse.add_argument('deliver_data', type = int)
        super(ExperimentListAPI, self).__init__()

    def get(self):
    	output = get_all_records(Experiments, "experiments")
        return {'data' : marshal(output, experiment_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        name = args['name']
        color = args['color']
        description = args['description']
        instructions = args['instructions']
        spare_answer_id = args['spare_answer_id']
        tag = args['tag']
        deliver_data = args['deliver_data']

        experiment = Experiments(name, color, description, instructions, spare_answer_id, tag, deliver_data)
        db.session.add(experiment)
        db.session.commit()
        experiment_id = experiment.id
        return args, 201
        
# ExperimentAPI
# show a single experiment info and lets you update/delete them
class ExperimentAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str)
        self.reqparse.add_argument('color', type = str)
        self.reqparse.add_argument('description', type = str)
        self.reqparse.add_argument('instructions', type = str)
        self.reqparse.add_argument('spare_answer_id', type = int)
        self.reqparse.add_argument('tag', type = str)
        self.reqparse.add_argument('deliver_data', type = int)
        
        super(ExperimentAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(Experiments, id, "experiments")
        return {'data' : marshal(output, experiment_fields)}

    def delete(self, id):
    	delete_record(Experiments, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(Experiments, id, args, "experiments")
        return output, 201
