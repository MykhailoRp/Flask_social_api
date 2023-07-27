from flask import Flask, jsonify, request
from app.models import Token, User
from app import db
from time import time
from functools import wraps


def requires_token(func):
    @wraps(func)
    def inner(*args, **kwargs):
        auth_token = request.headers.get("Authentication", None)

        if auth_token is None:
            return jsonify("Token is required"), 401

        token_data = Token.query.get(auth_token)

        if token_data is None:
            return jsonify("Invalid token provided"), 401

        if token_data.user is None:
            return jsonify("Invalid token provided"), 401

        if token_data.expires < time():
            return jsonify("Token has expired"), 401

        return func(user=token_data.user, token = token_data, *args, **kwargs)

    return inner

def optional_token(func):
    @wraps(func)
    def inner(*args, **kwargs):
        auth_token = request.headers.get("Authentication", None)

        if auth_token is None:
            return func(user=None, *args, **kwargs)

        token_data = Token.query.get(auth_token)

        if token_data is None:
            return func(user=None, *args, **kwargs)

        if token_data.user is None:
            return func(user=None, *args, **kwargs)

        if token_data.expires < time():
            return func(user=None, *args, **kwargs)

        return func(user=token_data.user, token = token_data, *args, **kwargs)

    return inner

def log_request(func):
    @wraps(func)
    def inner(user: User = None, *args, **kwargs):
        if user is not None:
            user.log_request()

        return func(user=user, *args, **kwargs)

    return inner