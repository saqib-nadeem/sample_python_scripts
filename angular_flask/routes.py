from flask.ext import restful

from angular_flask import app
from angular_flask.resources.store import StoreListAPI, StoreAPI
from angular_flask.resources.category import CategoryListAPI, CategoryAPI
from angular_flask.resources.product import ProductListAPI, ProductAPI
from angular_flask.resources.business_type import BusinessTypeListAPI, BusinessTypeAPI

api = restful.Api(app)

## Actually setup the Api resource routing here

#Store
api.add_resource(StoreListAPI, '/api/v1/stores')
api.add_resource(StoreAPI, '/api/v1/stores/<business_name>')

#Business Type
api.add_resource(BusinessTypeListAPI, '/api/v1/business_types')
api.add_resource(BusinessTypeAPI, '/api/v1/business_types/<business_type_id>')

#Category
api.add_resource(CategoryListAPI, '/api/v1/stores/<business_name>/categories/')
api.add_resource(CategoryAPI, '/api/v1/stores/<business_name>/categories/<category_id>')

#Product
api.add_resource(ProductListAPI, '/api/v1/categories/<category_name>/products/')
api.add_resource(ProductAPI, '/api/v1/categories/<category_name>/products/<product_id>')
