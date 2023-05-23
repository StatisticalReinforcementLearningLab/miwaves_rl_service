# Sets up authentication token based API

from functools import wraps

import jwt
from flask import request, abort
from flask import current_app
from models import Client


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers.get("Authorization")
            try:
                token = token.split(" ")[1]
            except IndexError:
                return {
                    "message": "Bearer token malformed.",
                    "data": None,
                    "status": "Unauthorized",
                }, 401
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "status": "Unauthorized",
            }, 401
        try:
            data = Client.decode_auth_token(token)
            current_client = None
            if not isinstance(data, str):
                current_client = Client.query.filter_by(id = data).first()
            if current_client is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "status": "Unauthorized",
                }, 401
            if not current_client["active"]:
                abort(403)
        except Exception as e:
            print(e)
            return {
                "message": "Something went wrong",
                "data": None,
                "status": "Internal Server Error",
            }, 500

        return f(current_client, *args, **kwargs)

    return decorated