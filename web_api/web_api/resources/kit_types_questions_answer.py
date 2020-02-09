from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import KitTypesQuestionsAnswers, db

kit_types_questions_answers_fields = {
    'kit': fields.Integer,
    'kit_types_questions_answer_option': fields.Integer,
    'answer_int': fields.Integer,
    'answer_decimal': fields.Integer,    
    'answer_text': fields.String,
    'uri': fields.Url('kit_types_questions_answer', absolute=True, scheme='http')
}

 #KitTypesQuestionsAnswers
# shows a list of all Answers, and lets you POST to add new answers of a kit type questions
class KitTypesQuestionsAnswersListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit', type = int)
        self.reqparse.add_argument('kit_types_questions_answer_option', type = int)
        self.reqparse.add_argument('answer_int', type = int)
        self.reqparse.add_argument('answer_decimal', type = int)
        self.reqparse.add_argument('answer_text', type = str, required = True, help = "Name cannot be blank!")
        super(KitTypesQuestionsAnswersListAPI, self).__init__()

    def get(self):
        output = get_all_records(KitTypesQuestionsAnswers, "kit_types_questions_answers")
        return {'data' : marshal(output, kit_types_questions_answers_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        kit = args['kit']
        kit_types_questions_answer_option = args['kit_types_questions_answer_option']
        answer_int = args['answer_int']
        answer_decimal = args['answer_decimal']
        answer_text = args['answer_text']

        new_row = KitTypesQuestionsAnswers(kit_types_questions_answer_option, kit, answer_int,
                 answer_decimal, answer_text)
        db.session.add(new_row)
        db.session.commit()
        new_row_id = new_row.id
        return args, 201


# KitTypesQuestionsAnswersAPI
# show a single answer of kit type info and lets you update/delete them
class KitTypesQuestionsAnswersAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit', type = int)
        self.reqparse.add_argument('kit_types_questions_answer_option', type = int)
        self.reqparse.add_argument('answer_int', type = int)
        self.reqparse.add_argument('answer_decimal', type = int)
        self.reqparse.add_argument('answer_text', type = str)
        super(KitTypesQuestionsAnswersAPI, self).__init__()
    

    def get(self, id):
        output = get_record_by_ID(KitTypesQuestionsAnswers, id, "kit_types_questions_answers")
        return {'data' : marshal(output, kit_types_questions_answers_fields)}

    def delete(self, id):
        delete_record(KitTypesQuestionsAnswers, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(KitTypesQuestionsAnswers, id, args, "kit_types_questions_answers")
        return output, 201

#POST
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answers -d "kit_types_questions_answer_option=1&kit=5&answer_int=0&answer_decimal=0&answer_text=5 ft, 8in" -X POST -v
#PUT
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answers/2 -d "kit_types_questions_answer_option=1&kit=5&answer_int=2&answer_decimal=2&answer_text=5 ft" -X PUT -v
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answers (GET ALL)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answers/2 (GET ONE)
#curl -u user:uBiome http://localhost:5000/api/v0/kit_types_questions_answers/5 -X DELETE -v