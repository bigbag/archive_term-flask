from functools import wraps

from flask import Flask, make_response


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
    return add_response_headers({'Content-Type': 'application/xml; charset=windows-1251'})(f)
