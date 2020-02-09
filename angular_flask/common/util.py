from flask import jsonify, url_for, request, make_response
from flask.ext.restful import reqparse, abort
from angular_flask.models.Store import Store
from angular_flask.models.Category import Category
from angular_flask.models.BusinessType import BusinessType


#### Helper Functions ####


def abort_if_record_doesnt_exist(id, entity):
    if entity is None:
        abort(404, message="ID {} doesn't exist".format(id)) 

def error_response(code, message):
    return jsonify({'status': False, 'error': {
		            'code': code,
		            'message': message
		    }})        

def get_store_by_business_name(business_name):
	return Store.objects(business_name=business_name).first()


def get_category_by_name(category_name):
	return Category.objects(name=category_name).first()

def get_business_type_by_id(id):
	return BusinessType.objects(id=id).first()	

