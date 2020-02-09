
from flask.ext import restful

from web_api import app

from web_api.resources.user import UserListAPI, UserAPI, AdminAPI
from web_api.resources.kit import KitListAPI, KitAPI
from web_api.resources.kit_type import KitTypeListAPI, KitTypeAPI
from web_api.resources.sample import SampleListAPI, SampleAPI
from web_api.resources.experiment import ExperimentListAPI, ExperimentAPI
from web_api.resources.kit_types_question import KitTypesQuestionsListAPI, KitTypesQuestionsAPI
from web_api.resources.kit_types_questions_answer_option import KitTypesQuestionsAnswerOptionsListAPI, KitTypesQuestionsAnswerOptionsAPI
from web_api.resources.kit_types_questions_answer import KitTypesQuestionsAnswersListAPI, KitTypesQuestionsAnswersAPI
from web_api.resources.experiment_types_question import ExperimentTypesQuestionsListAPI, ExperimentTypesQuestionsAPI
from web_api.resources.lab_sample_loading import LabSampleLoadingListAPI, LabSampleLoadingAPI
from web_api.resources.lab_pipeline_tracking import LabPipelineTracingListAPI, LabPipelineTracingAPI
from web_api.resources.taxa import TaxaListAPI, TaxaAPI
from web_api.resources.taxon_info import TaxonInfoListAPI, TaxonInfoAPI
from web_api.resources.results_taxoncount import ResultsTaxoncountListAPI, ResultsTaxoncountAPI
from web_api.resources.user_survey import UserSurveyListAPI, UserSurveyAPI, UserSurveyCompletedAPI

from flask import jsonify, url_for, request, make_response, send_from_directory

@app.route("/")
def test(**kwargs):
	#return send_from_directory("web_api/ubiome/ubiome/","index.html")
	return make_response(open('web_api/static/index.html').read())

api = restful.Api(app)

##
## Actually setup the Api resource routing here
##

api.add_resource(UserListAPI, '/api/v0/users', endpoint = 'users')
api.add_resource(UserAPI, '/api/v0/users/<int:id>', endpoint = 'user')
api.add_resource(AdminAPI, '/api/v0/admin/<int:id>', endpoint = 'admin')

api.add_resource(UserSurveyListAPI, '/api/v0/user_survey', endpoint = 'user_surveys')
api.add_resource(UserSurveyAPI, '/api/v0/user_survey/<int:id>', endpoint = 'user_survey')
api.add_resource(UserSurveyCompletedAPI, '/api/v0/user_survey_completed/<int:id>', endpoint = 'user_survey_completed')

api.add_resource(KitListAPI, '/api/v0/kits', endpoint = 'kits')
api.add_resource(KitAPI, '/api/v0/kits/<int:id>', endpoint = 'kit')

api.add_resource(KitTypeListAPI, '/api/v0/kit_types', endpoint = 'kit_types')
api.add_resource(KitTypeAPI, '/api/v0/kit_types/<int:id>', endpoint = 'kit_type')

api.add_resource(SampleListAPI, '/api/v0/samples', endpoint = 'samples')
api.add_resource(SampleAPI, '/api/v0/samples/<int:id>', endpoint = 'sample')

api.add_resource(ExperimentListAPI, '/api/v0/experiments', endpoint = 'experiments')
api.add_resource(ExperimentAPI, '/api/v0/experiments/<int:id>', endpoint = 'experiment')

api.add_resource(KitTypesQuestionsListAPI, '/api/v0/kit_types_questions', endpoint = 'kit_types_questions')
api.add_resource(KitTypesQuestionsAPI, '/api/v0/kit_types_questions/<int:id>', endpoint = 'kit_types_question')

api.add_resource(KitTypesQuestionsAnswerOptionsListAPI, '/api/v0/kit_types_questions_answer_options', endpoint = 'kit_types_questions_answer_options')
api.add_resource(KitTypesQuestionsAnswerOptionsAPI, '/api/v0/kit_types_questions_answer_options/<int:id>', endpoint = 'kit_types_questions_answer_option')

api.add_resource(KitTypesQuestionsAnswersListAPI, '/api/v0/kit_types_questions_answers', endpoint = 'kit_types_questions_answers')
api.add_resource(KitTypesQuestionsAnswersAPI, '/api/v0/kit_types_questions_answers/<int:id>', endpoint = 'kit_types_questions_answer')

api.add_resource(ExperimentTypesQuestionsListAPI, '/api/v0/experiment/<int:experiment_id>/kit_type_question', endpoint = 'experiment_types_questions')
api.add_resource(ExperimentTypesQuestionsAPI, '/api/v0/experiment/<int:experiment_id>/kit_type_question/<int:id>', endpoint = 'experiment_types_question')

api.add_resource(LabSampleLoadingListAPI, '/api/v0/lab_sample_loading', endpoint = 'lab_samples_loading')
api.add_resource(LabSampleLoadingAPI, '/api/v0/lab_sample_loading/<int:id>', endpoint = 'lab_sample_loading')

api.add_resource(LabPipelineTracingListAPI, '/api/v0/lab_pipeline_tracking', endpoint = 'lab_pipelines_tracking')
api.add_resource(LabPipelineTracingAPI, '/api/v0/lab_pipeline_tracking/<int:id>', endpoint = 'lab_pipeline_tracking')

api.add_resource(TaxaListAPI, '/api/v0/taxa', endpoint = 'taxa')
api.add_resource(TaxaAPI, '/api/v0/taxa/<int:id>', endpoint = 'taxon')

api.add_resource(TaxonInfoListAPI, '/api/v0/taxon_info', endpoint = 'taxa_info')
api.add_resource(TaxonInfoAPI, '/api/v0/taxon_info/<int:id>', endpoint = 'taxon_info')

api.add_resource(ResultsTaxoncountListAPI, '/api/v0/results_taxoncount', endpoint = 'results_taxoncount')
api.add_resource(ResultsTaxoncountAPI, '/api/v0/results_taxoncount/<int:id>', endpoint = 'result_taxoncount')