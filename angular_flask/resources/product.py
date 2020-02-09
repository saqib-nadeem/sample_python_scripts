from flask_restful import reqparse, abort, Api, Resource, fields, marshal

from angular_flask import app
from angular_flask.common.util import abort_if_record_doesnt_exist, get_category_by_name
from angular_flask.models.Category import Category
from angular_flask.models.User import User
from angular_flask.models.Product import Product

api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('description', type=str)
parser.add_argument('price', type=float)
parser.add_argument('image', type=str)


class ProductListAPI(Resource):

    def get(self, category_name):
        
        output = []
        category = get_category_by_name(category_name)
        abort_if_record_doesnt_exist(category_name, category)

        for product in Product.objects(category=category.id):
            row = {}
            row['id'] = str(category.id)
            row['name'] = product.name
            row['description'] = product.description
            row['price'] = product.price
            row['image'] = product.image
            output.append(row)

        return { 'Products': output }, 200


    def post(self, category_name):

        category = get_category_by_name(category_name)
        abort_if_record_doesnt_exist(category_name, category)

        args = parser.parse_args()
        product = Product(name=args['name'], description=args['description'], price=args['price'], image=args['image'])
        product.category = category

        product.save()
        return product.name, 201



class ProductAPI(Resource):

    def get(self, category_name, product_id):

        category = get_category_by_name(category_name)
        abort_if_record_doesnt_exist(category_name, category)

        product = Product.objects(category=category.id, id = product_id).first()
        #TODO: check if category_id is invalid

        result = {}
        result['id'] = str(product.id)
        result['name'] = product.name
        result['description'] = product.description
        result['price'] = product.price
        result['image'] = product.image
        result['created_at'] = product.created_at.isoformat()

        return result, 200


    def delete(self, category_name, product_id):

        category = get_category_by_name(category_name)
        abort_if_record_doesnt_exist(category_name, category)

        product = Product.objects(category=category.id, id = product_id).first()
        
        product.delete()
        return category.name, 204


    def put(self, category_name, product_id):

    	category = get_category_by_name(category_name)
        abort_if_record_doesnt_exist(category_name, category)

        product = Product.objects(category=category.id, id = product_id).first()
        args = parser.parse_args()
        for field, value in args.iteritems():
            if value is not None:
                setattr(product, field, value)

        product.save()
        return product.name, 201






# Sample Data

# GET
# curl -X GET http://127.0.0.1:5000/api/v1/categories/Action%20Games/products/

# GET single object
# curl -X GET http://127.0.0.1:5000/api/v1/categories/Action%20Games/products/55be3ff7036bc1118df9bb59

# POST
# curl -X POST -d "name=Project IGI&description=First Person shooter game&price=100&image=image01.jpg"  http://127.0.0.1:5000/api/v1/categories/Action%20Games/products/

# PUT
# curl -X PUT -d "price=120"  http://127.0.0.1:5000/api/v1/categories/Action%20Games/products/55be3ff7036bc1118df9bb59

# DELETE
# curl -X DELETE http://127.0.0.1:5000/api/v1/categories/Action%20Games/products/55be3ff7036bc1118df9bb59

