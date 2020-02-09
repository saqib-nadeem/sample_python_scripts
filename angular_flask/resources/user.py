import os
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.httpauth import HTTPBasicAuth

from angular_flask import app
from angular_flask.common.util import error_response

from angular_flask.models.User import User


auth = HTTPBasicAuth()

@app.route('/api/register', methods = ['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments

    user = User(username = username)
    user.hash_password(password)
    user.save()

    return jsonify({ 
        'username': user.username,
        'id': str(user.id) }), 201


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User().verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.objects(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/login')
@auth.login_required
def login():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username,
        'id': str(g.user.id) })


def error_response(code, message):
    return jsonify({'status': False, 'error': {
            'code': code,
            'message': message
        }})




# User Story example!
#
# Creating New User
# curl i -X POST -H "Content-Type: application/json" -d '{"username":"reham","password":"khan"}' http://127.0.0.1:5000/api/register
#
# Login via new user OR generating token
# curl u reham:khan -i -X GET http://127.0.0.1:5000/api/login
#
# Access API using token (in my example I am accessing sample resource)
# curl u INSERT_YOUR_TOKEN_HERE:unused -i -X GET http://127.0.0.1:5000/api/resource