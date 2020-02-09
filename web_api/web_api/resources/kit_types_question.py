from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import KitTypesQuestions, db

kit_types_questions_fields = {
    'kit_type': fields.Integer,
    'question_text': fields.String,
    'question_type': fields.Integer,
    'question_order': fields.Integer,
    'page': fields.Integer,
    'show_number': fields.Integer,
    'requiredFilterPermission': fields.Integer,
    'uri': fields.Url('kit_types_question', absolute=True, scheme='http')
}

# KitTypeQuestionsListAPI
# shows a list of all kit types, and lets you POST to add new kit type
class KitTypesQuestionsListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('question_text', type = str, required = True, help = "Name cannot be blank!")
        self.reqparse.add_argument('question_type', type = int)
        self.reqparse.add_argument('question_order', type = int)
        self.reqparse.add_argument('page', type = int)
        self.reqparse.add_argument('show_number', type = int)
        self.reqparse.add_argument('requiredFilterPermission', type = int)
        
        super(KitTypesQuestionsListAPI, self).__init__()

    def get(self):
        output = get_all_records(KitTypesQuestions, "kit_types_questions")
        return {'data' : marshal(output, kit_types_questions_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        kit_type = args['kit_type']
        question_text = args['question_text']
        question_type = args['question_type']
        question_order = args['question_order']
        page = args['page']
        show_number = args['show_number']
        requiredFilterPermission = args['requiredFilterPermission']
        kit_type_question = KitTypesQuestions(kit_type, question_text, question_type, question_order,
                                              page, show_number, requiredFilterPermission)
        db.session.add(kit_type_question)
        db.session.commit()
        kit_type_question_id = kit_type_question.id
        return args, 201

# KitTypesQuestionsAPI
# shows a single Question and lets you delete/update them
class KitTypesQuestionsAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('question_text', type = str, required = True, help = "Name cannot be blank!")
        self.reqparse.add_argument('question_type', type = int)
        self.reqparse.add_argument('question_order', type = int)
        self.reqparse.add_argument('page', type = int)
        self.reqparse.add_argument('show_number', type = int)
        self.reqparse.add_argument('requiredFilterPermission', type = int)
        super(KitTypesQuestionsAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(KitTypesQuestions, id, "kit_types_questions")
        return {'data' : marshal(output, kit_types_questions_fields)}

    def delete(self, id):
        delete_record(KitTypesQuestions, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(KitTypesQuestions, id, args, "kit_types_questions")
        return output, 201

#POST
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions -d "kit_type=12&question_text=Has your weight changed by more than 5 lbs (2kg) in the last 6 months?&question_type=3&question_order=3&page=7&show_number=1&requiredFilterPermission=15" -X POST -v
#PUT 
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions/6 -d "kit_type=12&question_text=Has your weight changed by more than 5 lbs (2kg) in the last 6 months test?&question_type=3&question_order=3&page=7&show_number=1&requiredFilterPermission=18" -X PUT -v
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions (GET ALL)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions/2 (GET ONE)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions/5 -X DELETE -v
