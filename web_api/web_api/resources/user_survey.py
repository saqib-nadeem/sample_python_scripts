from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal
from flask.ext.security import login_required, auth_token_required, roles_accepted, roles_required

from web_api.resources import auth
from web_api.models import UserSurvey, db
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 

user_fields = {
    'user': fields.Integer,
    'dob': fields.String,
    'city_and_country': fields.String,
    'gender': fields.String,
    'race': fields.String,
    'allow_data_comparison': fields.String,
    'term_of_service': fields.String,
    'privacy_policy': fields.String,
    'induction_completed': fields.String,
    'service_consent': fields.String,
    'uri': fields.Url('user_survey', absolute=True, scheme='http')
}

# UserSurveyListAPI
# shows a list of all user surveys, and lets you POST to add new user user survey
class UserSurveyListAPI(Resource):
    #decorators = [auth_token_required]

    def __init__(self):  
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type = int)
        self.reqparse.add_argument('dob', type = str)
        self.reqparse.add_argument('city_and_country', type = str)
        self.reqparse.add_argument('gender', type = str)
        self.reqparse.add_argument('race', type = str)
        self.reqparse.add_argument('allow_data_comparison', type = str)
        self.reqparse.add_argument('term_of_service', type = str)
        self.reqparse.add_argument('privacy_policy', type = str)
        self.reqparse.add_argument('induction_completed', type = str)
        self.reqparse.add_argument('service_consent', type = str)                 
        super(UserSurveyListAPI, self).__init__()

    def get(self):
    	output = get_all_records(UserSurvey, "user_survey")
        return {'data' : marshal(output, user_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        user = args['user']
        dob = args['dob']
        city_and_country = args['city_and_country']
        gender = args['gender']
        race = args['race']
        allow_data_comparison = args['allow_data_comparison']
        term_of_service = args['term_of_service']
        privacy_policy = args['privacy_policy']
        induction_completed = args['induction_completed']
        service_consent = args['service_consent']

        user_survey = UserSurvey(user, dob, city_and_country, gender, race, allow_data_comparison, term_of_service,
                                 privacy_policy, induction_completed, service_consent)

        db.session.add(user_survey)
        db.session.commit()
        user_survey = user_survey.id
        return args, 201
        
# UserSurveyAPI
# show a single user survey info and lets you updte/delete them
class UserSurveyAPI(Resource):
    #decorators = [auth_token_required]
        
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type = int)
        self.reqparse.add_argument('dob', type = str)
        self.reqparse.add_argument('city_and_country', type = str)
        self.reqparse.add_argument('gender', type = str)
        self.reqparse.add_argument('race', type = str)
        self.reqparse.add_argument('allow_data_comparison', type = str)
        self.reqparse.add_argument('privacy_policy', type = str)
        self.reqparse.add_argument('induction_completed', type = str)
        self.reqparse.add_argument('service_consent', type = str)                 
        super(UserSurveyAPI, self).__init__()

    def get(self, id):        
        output = get_record_by_ID(UserSurvey, id, "user_survey")
        return {'data' : marshal(output, user_fields)}

    def delete(self, id):
    	delete_record(UserSurvey, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(UserSurvey, id, args, "user_survey")
        return output, 201

# UserSurveyCompletedAPI
# Check id user comoleted the survey
class UserSurveyCompletedAPI(Resource):
    #decorators = [auth_token_required]
    def get(self, id): 
        record = UserSurvey.query.filter_by(user=id).first()
        abort_if_record_doesnt_exist(id,record)
        output = []
        row = {}

        for field in UserSurvey.__table__.c:
            field = str(field).replace("user_survey.","")

            if field == "induction_completed" and record.induction_completed == True:
                return {"status": True}

            row[field] = getattr(record, field, None)
        
        output.append(row)
        return {'data' : marshal(output, user_fields) }
      