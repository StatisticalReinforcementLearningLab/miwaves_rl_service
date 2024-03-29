# src/server/auth/views.py


from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import app, bcrypt, db
from src.server.auth.models import Client, BlacklistToken

auth_blueprint = Blueprint('auth', __name__)


class AuthRegisterAPI(MethodView):
    """
    Client Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = Client.query.filter_by(username=post_data.get('api_user')).first()
        number_of_users = Client.query.count()
        if not user:
            # Do not want to allow more than one registered user
            if number_of_users != 0:
                responseObject = {
                    'status': 'fail',
                    'message': 'No more clients allowed to register.',
                    'error_code': 4,
                }
                return make_response(jsonify(responseObject)), 202
            else:
                try:
                    user = Client(
                        username=post_data.get('api_user'),
                        password=post_data.get('api_pass')
                    )
                    # Print the user if DEBUG is set to True
                    if app.config.get('DEBUG'):
                        print("User: ", user)

                    # insert the user
                    db.session.add(user)
                    db.session.commit()

                    # Print the commit if DEBUG is set to True
                    if app.config.get('DEBUG'):
                        print("DB Committed new user")

                    # generate the auth token
                    auth_token = user.encode_auth_token(user.id)

                    # Print the auth_token if DEBUG is set to True
                    if app.config.get('DEBUG'):
                        print("Auth Token: ", auth_token)

                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully registered.',
                        'auth_token': auth_token
                    }
                    return make_response(jsonify(responseObject)), 201
                except Exception as e:
                    print("Exception: ", e)
                    # import pdb; pdb.set_trace()
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again.',
                        'error_code': 5
                    }
                    return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Client already exists. Please Log in.',
                'error_code': 6,
            }
            return make_response(jsonify(responseObject)), 202


class AuthLoginAPI(MethodView):
    """
    Client Login Resource
    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = Client.query.filter_by(
                username=post_data.get('api_user')
            ).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get('api_pass')
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Invalid client credentials.',
                    'error_code': 7
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again',
                'error_code': 8
            }
            return make_response(jsonify(responseObject)), 500

class AuthLogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = Client.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e,
                        'error_code': 9
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                # import pdb; pdb.set_trace()
                responseObject = {
                    'status': 'fail',
                    'message': resp,
                    'error_code': 10
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.',
                'error_code': 11
            }
            return make_response(jsonify(responseObject)), 403

# define the API resources
registration_view = AuthRegisterAPI.as_view('register_api')
login_view = AuthLoginAPI.as_view('login_api')
logout_view = AuthLogoutAPI.as_view('logout_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)