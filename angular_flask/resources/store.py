from flask_restful import reqparse, abort, Api, Resource, fields, marshal

from angular_flask import app
from angular_flask.common.util import *
from angular_flask.models.Store import Store
from angular_flask.models.User import User
from angular_flask.models.BusinessType import BusinessType

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('business_name', type=str)
parser.add_argument('about', type=str)
parser.add_argument('title', type=str)
parser.add_argument('activated', type=str)
parser.add_argument('published', type=str)
parser.add_argument('address', type=str)
parser.add_argument('city', type=str)
parser.add_argument('email', type=str)
parser.add_argument('contact', type=str)
parser.add_argument('url', type=str)
parser.add_argument('business_type_id', type=str)
parser.add_argument('user_id', type=str)

# StoreListAPI
# shows a list of all stores, and lets you POST to add new stores
class StoreListAPI(Resource):

    #decorators = [auth.login_required]

    def get(self):

        output = []

        for store in Store.objects:
            row = {}
            row['id'] = str(store.id)
            row['business_name'] = store.business_name
            row['about'] = store.about
            row['title'] = store.title
            row['activated'] = store.activated
            row['published'] = store.published
            row['address'] = store.address
            row['city'] = store.city
            row['email'] = store.email
            row['contact'] = store.contact
            row['url'] = store.url
            row['created_at'] = store.created_at.isoformat()
            output.append(row)

        return {'stores': output}    

    def post(self):

        args = parser.parse_args()
        store = Store(business_name=args['business_name'], about=args['about'], title=args['title'], 
                      activated=args['activated'], published=args['published'], address=args['address'],
                      city=args['city'], email=args['email'], contact=args['contact'],
                      url=args['url'])
        user = User.objects(id=args['user_id']).first() 
        store.user = user
        business_type = get_business_type_by_id(args['business_type_id'])
        store.business_type
        store.save()
        return {'business_name': store.business_name, 'id': str(store.id)}, 201                 
        
        
# StoreAPI
# shows a single store record and lets you delete a store record
class StoreAPI(Resource):
    def get(self, business_name):
        store = Store.objects(business_name=business_name).first() 
        abort_if_record_doesnt_exist(business_name, store)
        result = {}
        result['id'] = str(store.id)
        result['business_name'] = store.business_name
        result['about'] = store.about
        result['title'] = store.title
        result['activated'] = store.activated
        result['published'] = store.published
        result['address'] = store.address
        result['city'] = store.city
        result['email'] = store.email
        result['contact'] = store.contact
        result['url'] = store.url
        result['created_at'] = store.created_at.isoformat()

        return result, 200 

    def delete(self, business_name):
        store = Store.objects(business_name=business_name).first() 
        abort_if_record_doesnt_exist(business_name, store)
        store.delete()
        return '', 204

    def put(self, business_name):
        args = parser.parse_args()
        store = Store.objects(business_name=business_name).first() 
        abort_if_record_doesnt_exist(business_name, store)        
        for field, value in args.iteritems():
            if value is not None:
                setattr(store, field, value)

        store.save()        
        return store.business_name, 201


# Complete CURD opterations example using curl utility 

# Creating A Store
# curl http://localhost:5000/api/v1/stores -d "business_name=unique-business-name-here&about=about-desc-here&title=title-here&user_id=ref-user-id-here" -X POST -v

# Get All Stores List
# curl http://localhost:5000/api/v1/stores

# Get A Single Store 
# curl http://localhost:5000/api/v1/stores/store_business_name_here

# Delete A Single Store
# curl http://localhost:5000/api/v1/stores/store_business_name_here -X DELETE -v

# Update A single Store
# curl http://localhost:5000/api/v1/stores/store_business_name_here -d "about=about-desc-here&title=some-title-here" -X PUT -v

# Or from python if you have the requests library installed
# from requests import put, get
# get('http://localhost:5000/api/v1/stores').json()
# put('http://localhost:5000/api/v1/stores/store_business_name_here', data={'title': 'some title here'}).json()