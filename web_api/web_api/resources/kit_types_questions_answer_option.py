from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import KitTypesQuestionsAnswerOptions, db

kit_types_questions_answer_options_fields = {
    'kit_type_question': fields.Integer,
    'answer_text': fields.String,
    'answer_tooltip': fields.String,
    'answer_order': fields.Integer,
    'answer_validation': fields.String, 
    'uri': fields.Url('kit_types_questions_answer_option', absolute=True, scheme='http')
}

# KitTypesQuestionsAnswerOptionsListAPI
# shows a list of all options, and lets you POST to add new option for a particular kit type question
class KitTypesQuestionsAnswerOptionsListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type_question', type = int)
        self.reqparse.add_argument('answer_text', type = str)
        self.reqparse.add_argument('answer_tooltip', type = str)
        self.reqparse.add_argument('answer_order', type = int)
        self.reqparse.add_argument('answer_validation', type = str)
        super(KitTypesQuestionsAnswerOptionsListAPI, self).__init__()

    def get(self):
        output = get_all_records(KitTypesQuestionsAnswerOptions, "kit_types_questions_answer_options")
        return {'data' : marshal(output, kit_types_questions_answer_options_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        
        kit_type_question = args['kit_type_question']
        answer_text = args['answer_text']
        answer_tooltip = args['answer_tooltip']
        answer_order = args['answer_order']
        answer_validation = args['answer_validation']
        new_row = KitTypesQuestionsAnswerOptions(kit_type_question, answer_text, answer_tooltip, answer_order,
                 answer_validation)
        db.session.add(new_row)
        db.session.commit()
        new_row_id = new_row.id
        return args, 201

# KitTypesQuestionsAnswerOptionsAPI
# shows a single option and lets you delete/update them
class KitTypesQuestionsAnswerOptionsAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type_question', type = int)
        self.reqparse.add_argument('answer_text', type = str)
        self.reqparse.add_argument('answer_tooltip', type = str)
        self.reqparse.add_argument('answer_order', type = int)
        self.reqparse.add_argument('answer_validation', type = str)
        
        super(KitTypesQuestionsAnswerOptionsAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(KitTypesQuestionsAnswerOptions, id, "kit_types_questions_answer_options")
        return {'data' : marshal(output, kit_types_questions_answer_options_fields)}

    def delete(self, id):
        delete_record(KitTypesQuestionsAnswerOptions, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(KitTypesQuestionsAnswerOptions, id, args, "kit_types_questions_answer_options")
        return output, 201

#POST
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answer_options -d "kit_type_question=2&answer_text=5.44&answer_tooltip=Check this box if you have been diagnosed with this condition.&answer_order=1&answer_validation" -X POST -v
#PUT
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answer_options/2 -d "kit_type_question=2&answer_text=5&answer_tooltip=Check this box&answer_order=4&answer_validation=true" -X PUT -v
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answer_options (GET ALL)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answer_options/2 (GET ONE)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answer_options/2 -X DELETE -v
