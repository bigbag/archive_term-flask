from functools import wraps
from flask import Flask, make_response
from api.helpers.hash_helper import *


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def xml_headers(f):
    @wraps(f)
    @add_response_headers({'Content-Type': 'application/xml; charset=windows-1251'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def md5_content_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        h = resp.headers
        h['Content-MD5'] = get_content_md5(resp.response[0])
        return resp
    return decorated_function
