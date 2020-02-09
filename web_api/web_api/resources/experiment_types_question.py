from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import KitTypesQuestions, Experiments, db

experiment_types_questions_fields = {
    'kit_type': fields.Integer,
    'question_text': fields.String,
    'question_type': fields.Integer,
    'question_order': fields.Integer,
    'page': fields.Integer,
    'show_number': fields.Integer,
    'requiredFilterPermission': fields.Integer,
    #'uri': fields.Url('experiment_types_question', absolute=True, scheme='http')
}

class ExperimentTypesQuestionsListAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('question_text', type = str)
        self.reqparse.add_argument('question_type', type = int)
        self.reqparse.add_argument('question_order', type = int)
        self.reqparse.add_argument('page', type = int)
        self.reqparse.add_argument('show_number', type = int)
        self.reqparse.add_argument('requiredFilterPermission', type = int)
        
        super(ExperimentTypesQuestionsListAPI, self).__init__()

    def get(self, experiment_id):
        exp = Experiments.query.filter_by(id=experiment_id).first()
        output = []
    
        for row in exp.kit_types_questions:
            obj = {}
            for field in KitTypesQuestions.__table__.c:
                field = str(field).replace("kit_types_questions.","")
                obj[field] = getattr(row, field, None)
            output.append(obj)
        return {'data' : marshal(output, experiment_types_questions_fields)}

    def post(self, experiment_id):
        args = self.reqparse.parse_args()
        kit_type = args['kit_type']
        question_text = args['question_text']
        question_type = args['question_type']
        question_order = args['question_order']
        page = args['page']
        show_number = args['show_number']
        requiredFilterPermission = args['requiredFilterPermission']
        experiment_type_question = KitTypesQuestions(kit_type, question_text, question_type, question_order,
                                                     page, show_number, requiredFilterPermission)
        db.session.add(experiment_type_question)
        db.session.commit()
        experiment_type_question_id = experiment_type_question.id

        experiment_row = Experiments.query.filter_by(id=experiment_id).first()
        experiment_row.kit_types_questions.append(experiment_type_question)
        db.session.add(experiment_row)
        db.session.commit()
        return args, 201


class ExperimentTypesQuestionsAPI(Resource):
    #decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('kit_type', type = int)
        self.reqparse.add_argument('question_text', type = str)
        self.reqparse.add_argument('question_type', type = int)
        self.reqparse.add_argument('question_order', type = int)
        self.reqparse.add_argument('page', type = int)
        self.reqparse.add_argument('show_number', type = int)
        self.reqparse.add_argument('requiredFilterPermission', type = int)
        
        super(ExperimentTypesQuestionsAPI, self).__init__()

    def get(self, experiment_id, id):

        exp = Experiments.query.filter_by(id=experiment_id).first()
        question = KitTypesQuestions.query.filter_by(id=id).first()
        output = []
        obj = {}
        for row in exp.kit_types_questions:
            if row.id == id:
                for field in KitTypesQuestions.__table__.c:
                    field = str(field).replace("kit_types_questions.","")
                    obj[field] = getattr(row, field, None)

                output.append(obj)
                return jsonify(data=output)
        return {"message":"Data not found"},404

    def delete(self, experiment_id, id):
        experiment_row = Experiments.query.filter_by(id=experiment_id).first()
        experiment_type_question = KitTypesQuestions.query.filter_by(id=id).first()
        experiment_row.kit_types_questions.remove(experiment_type_question)
        db.session.delete(experiment_type_question)
        db.session.commit()
        return '',204    

#POST Command
#curl http://localhost:5000/api/v0/experiment/1/kit_type_question -d "kit_type=12&question_text=Do you wear glasses&question_type=2&question_order=4&page=7&show_number=1&requiredFilterPermission=15" -X POST -v
#curl -u admin:uBiome http://localhost:5000/api/v0/experiment/1/kit_type_question (GET ALL)
#curl -u admin:uBiome http://localhost:5000/api/v0/kexperiment/1/kit_type_question/8 (GET ONE)
#curl -u admin:uBiome http://localhost:5000/api/v0/experiment/1/kit_type_question/9 -X DELETE -v
