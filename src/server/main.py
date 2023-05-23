# src/server/main.py

# Server code that hosts the main RL API

from src.server.auth.auth import token_required

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import app, bcrypt, db
from src.server.auth.models import Client, BlacklistToken

rlservice_blueprint = Blueprint('rlservice', __name__)

@token_required
def get_actions_for_user(current_user):
    """
    Get the actions for a user
    """
    # get the post data
    post_data = request.get_json()
    # check if user already exists
    user = Client.query.filter_by(username=post_data.get('username')).first()
    if not user:
        responseObject = {
            'status': 'fail',
            'message': 'No user found.',
        }
        return make_response(jsonify(responseObject)), 404
    else:
        # generate the auth token
        auth_token = user.encode_auth_token(user.id)
        responseObject = {
            'status': 'success',
            'message': 'Successfully retrieved actions.',
            'auth_token': auth_token.decode()
        }
        return make_response(jsonify(responseObject)), 200