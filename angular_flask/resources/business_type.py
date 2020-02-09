from flask_restful import reqparse, abort, Api, Resource, fields, marshal

from angular_flask import app
from angular_flask.common.util import *
from angular_flask.models.BusinessType import BusinessType

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)

# shows a list of all BusinessType, and lets you POST to add new BusinessType
class BusinessTypeListAPI(Resource):

    #decorators = [auth.login_required]

    def get(self):

        output = []

        for business_type in BusinessType.objects:
            row = {}
            row['id'] = str(business_type.id)
            row['name'] = business_type.name
            row['created_at'] = business_type.created_at.isoformat()
            output.append(row)

        return {'business_types': output}       
        
    def post(self):

        args = parser.parse_args()
        business_type = BusinessType(name=args['name'])

        business_type.save()
        return business_type.name, 201     

# shows a single business_type record and lets you delete a business_type record
class BusinessTypeAPI(Resource):
   
    def get(self, business_type_id):

        business_type = get_business_type_by_id(business_type_id)
        #TODO: proper error handling for => mongoengine.errors.ValidationError 
        abort_if_record_doesnt_exist(business_type_id, business_type)

        result = {}
        result['id'] = str(business_type.id)
        result['name'] = business_type.name
        result['created_at'] = business_type.created_at.isoformat()

        return result
          
    def delete(self, business_type_id):

        business_type = get_business_type_by_id(business_type_id)
        abort_if_record_doesnt_exist(business_type_id, business_type)
        business_type.delete()
        return '', 204

    def put(self, business_type_id):

        business_type = get_business_type_by_id(business_type_id)
        abort_if_record_doesnt_exist(business_type_id, business_type)

        args = parser.parse_args()
        for field, value in args.iteritems():
            if value is not None:
                setattr(business_type, field, value)

        business_type.save()
        return business_type.name, 201


"""
Complete CURD opterations example using curl utility 

Get All business_types:
curl -X GET http://127.0.0.1:5000/api/v1/business_types

Creating a business_type
curl -X POST -d "name=business_type_name_here"  http://127.0.0.1:5000/api/v1/business_types

Delete a business_type
curl -X DELETE -v http://127.0.0.1:5000/api/v1/business_types/business_type_id

Update a business_type
curl -X PUT -v -d "name=business_type_name_here" http://127.0.0.1:5000/api/v1/business_types/business_type_id

"""

