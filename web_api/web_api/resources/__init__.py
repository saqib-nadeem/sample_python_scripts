from flask import jsonify, url_for, request, make_response

from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import (Users, Kits, KitTypes, Samples, Experiments, KitTypesQuestions, KitTypesQuestionsAnswerOptions,
 KitTypesQuestionsAnswers, kit_types_questions_X_experiments, Taxa, TaxonInfo, ResultsTaxoncount ,LabSampleLoading, LabPipelineTracing, db)


auth = HTTPBasicAuth()

users = {
    "admin": "uBiome",
    "user": "uBiome",
    "ubiome": "welovebacteria"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None 

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)