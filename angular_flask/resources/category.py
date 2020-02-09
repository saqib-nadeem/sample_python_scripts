from flask_restful import reqparse, abort, Api, Resource, fields, marshal

from angular_flask import app
from angular_flask.common.util import *
from angular_flask.models.Category import Category

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('description', type=str)

# shows a list of all categories in a given store, and lets you POST to add new categories
class CategoryListAPI(Resource):

    #decorators = [auth.login_required]

    def get(self, business_name):

        output = []
        store = get_store_by_business_name(business_name)
        abort_if_record_doesnt_exist(business_name, store)

        for category in Category.objects(store=store.id):
            row = {}
            row['id'] = str(category.id)
            row['name'] = category.name
            row['description'] = category.description
            row['created_at'] = category.created_at.isoformat()
            output.append(row)

        return {'categories': output}       
        
    def post(self, business_name):

        store = get_store_by_business_name(business_name)
        abort_if_record_doesnt_exist(business_name, store)

        args = parser.parse_args()
        category = Category(name=args['name'], description=args['description'])
        category.store = store

        category.save()
        return category.name, 201     

# shows a single category record and lets you delete a category record
class CategoryAPI(Resource):
   
    def get(self, business_name, category_id):

        store = get_store_by_business_name(business_name)
        abort_if_record_doesnt_exist(business_name, store)

        category = Category.objects(store=store.id, id = category_id).first()
        #TODO: check if category_id is invalid

        result = {}
        result['id'] = str(category.id)
        result['name'] = category.name
        result['description'] = category.description
        result['created_at'] = category.created_at.isoformat()

        return result
          
    def delete(self, business_name, category_id):

        store = get_store_by_business_name(business_name)
        abort_if_record_doesnt_exist(business_name, store)

        category = Category.objects(store=store.id, id = category_id).first()
        #TODO: check if category_id is invalid

        category.delete()
        return category.name, 204

    def put(self, business_name, category_id):

        store = get_store_by_business_name(business_name)
        abort_if_record_doesnt_exist(business_name, store)

        category = Category.objects(store=store.id, id = category_id).first()
        #TODO: check if category_id is invalid

        args = parser.parse_args()
        for field, value in args.iteritems():
            if value is not None:
                setattr(category, field, value)

        category.save()
        return category.name, 201


############

"""

Get All categories in a store given a business_name:
curl -X GET http://127.0.0.1:5000/api/v1/stores/namco2good/categories/

Add a Category: Send a POST request to /stores/<business_name/categories
curl -X POST -d "name=Action Games&description=All about action games"  http://127.0.0.1:5000/api/v1/stores/namco2good/categories/

Delete a category:Send a DELETE request to /stores/<business_name/categories/<category_id>
curl -X DELETE http://127.0.0.1:5000/api/v1/stores/namco2good/categories/55ae369e9469d844b08009e8

Update a category: Send a PUT request to /stores/<business_name/categories/<category_id>
curl -X PUT -d "name=Action Games" http://127.0.0.1:5000/api/v1/stores/namco2good/categories/55ac137d9469d83cdef9427acurl -X PUT -d "name=Action Games" http://127.0.0.1:5000/api/v1/stores/namco2good/categories/55ac137d9469d83cdef9427a

"""

