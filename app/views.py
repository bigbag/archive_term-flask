from flask import Flask, jsonify, abort, make_response
from flask.ext.httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username in users:
        return users[username]
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
