from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal
from flask.ext.security import login_required, auth_token_required, roles_accepted, roles_required

from web_api.resources import auth
from web_api.models import User, db
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 

user_fields = {
    'email': fields.String,
    'password': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'admin': fields.String,
    'uri': fields.Url('user', absolute=True, scheme='http')
}

# UserListAPI
# shows a list of all users, and lets you POST to add new user
class UserListAPI(Resource):
    #decorators = [auth_token_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type = str)
        self.reqparse.add_argument('password', type = str)
        self.reqparse.add_argument('first_name', type = str)
        self.reqparse.add_argument('last_name', type = str)
        self.reqparse.add_argument('admin', type = str)
        super(UserListAPI, self).__init__()

    def get(self):
    	output = get_all_records(User, "user")
        return {'data' : marshal(output, user_fields)}

    def post(self):
        args = parser.parse_args()
        email = args['email']
        password = args['password']
        first_name = args['first_name']
        last_name = args['last_name']

        user = User(email, password, first_name, last_name)

        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return args, 201
        
# UserAPI
# show a single user info and lets you updte/delete them
class UserAPI(Resource):
    #decorators = [auth_token_required]
        
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type = str)
        self.reqparse.add_argument('password', type = str)
        self.reqparse.add_argument('first_name', type = str)
        self.reqparse.add_argument('last_name', type = str)
        self.reqparse.add_argument('admin', type = str)
        
        super(UserAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(User, id, "user")
        return {'data' : marshal(output, user_fields)}

    def delete(self, id):
    	delete_record(User, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(User, id, args, "user")
        return output, 201



# AdminAPI
# Check if user is an admin
class AdminAPI(Resource):
    #decorators = [auth_token_required]

    def get(self, id):
        row = get_record_by_ID(User, id, "user")

        if row[0]["admin"] == True:
            return { 'status': True}

        return {'status': False}

'''user_fields = {
    'facebook_id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'induction_completed': fields.Integer,
    'adminlevel': fields.Integer,
    'outbound_last_identify': fields.DateTime,
    'serviceConsent': fields.Integer,
    'sitever': fields.Integer,
    'firstrunwarning': fields.Integer,
    'displayname': fields.String,
    'consentonfile': fields.Integer,
    'mailinglist_invite': fields.DateTime,
    'uri': fields.Url('user', absolute=True, scheme='http')
}

# UserListAPI
# shows a list of all users, and lets you POST to add new user
class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('facebook_id', type = int)
        self.reqparse.add_argument('username', type = str)
        self.reqparse.add_argument('email', type = str)
        self.reqparse.add_argument('password', type = str)
        self.reqparse.add_argument('first_name', type = str)
        self.reqparse.add_argument('last_name', type = str)
        self.reqparse.add_argument('induction_completed', type = int)
        self.reqparse.add_argument('adminlevel', type = int)
        self.reqparse.add_argument('outbound_last_identify', type = str)
        self.reqparse.add_argument('serviceConsent', type = int)
        self.reqparse.add_argument('sitever', type = int)
        self.reqparse.add_argument('firstrunwarning', type = int)
        self.reqparse.add_argument('displayname', type = str)
        self.reqparse.add_argument('consentonfile', type = int)
        self.reqparse.add_argument('mailinglist_invite', type = str)
        super(UserListAPI, self).__init__()

    def get(self):
        output = get_all_records(Users, "users")
        return {'data' : marshal(output, user_fields)}

    def post(self):
        args = parser.parse_args()
        facebook_id = args['facebook_id']
        username = args['username']
        email = args['email']
        password = args['password']
        first_name = args['first_name']
        last_name = args['last_name']
        induction_completed = args['induction_completed']
        adminlevel = args['adminlevel']
        outbound_last_identify = args['outbound_last_identify']
        serviceConsent = args['serviceConsent']
        sitever = args['sitever']
        firstrunwarning = args['firstrunwarning']
        displayname = args['displayname']
        consentonfile = args['consentonfile']
        mailinglist_invite = args['mailinglist_invite']

        user = Users(facebook_id, username, email, password, first_name, last_name,
                     induction_completed, adminlevel, outbound_last_identify,
                     serviceConsent, sitever, firstrunwarning, displayname,
                     consentonfile, mailinglist_invite)

        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return args, 201
        
# UserAPI
# show a single user info and lets you updte/delete them
class UserAPI(Resource):
    decorators = [auth.login_required]
        
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('facebook_id', type = int)
        self.reqparse.add_argument('username', type = str)
        self.reqparse.add_argument('email', type = str)
        self.reqparse.add_argument('password', type = str)
        self.reqparse.add_argument('first_name', type = str)
        self.reqparse.add_argument('last_name', type = str)
        self.reqparse.add_argument('induction_completed', type = int)
        self.reqparse.add_argument('adminlevel', type = int)
        self.reqparse.add_argument('outbound_last_identify', type = str)
        self.reqparse.add_argument('serviceConsent', type = int)
        self.reqparse.add_argument('sitever', type = int)
        self.reqparse.add_argument('firstrunwarning', type = int)
        self.reqparse.add_argument('displayname', type = str)
        self.reqparse.add_argument('consentonfile', type = int)
        self.reqparse.add_argument('mailinglist_invite', type = str)
        
        super(UserAPI, self).__init__()

    def get(self, id):
        output = get_record_by_ID(Users, id, "users")
        return {'data' : marshal(output, user_fields)}

    def delete(self, id):
        delete_record(Users, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(Users, id, args, "users")
        return output, 201'''       