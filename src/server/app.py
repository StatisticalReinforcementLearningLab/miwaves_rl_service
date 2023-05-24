# src/server/app.py

# Server code that hosts the main RL API

from src.server.auth.auth import token_required

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import app, bcrypt, db
from src.server.auth.models import Client
from src.server.tables import (
    User,
    UserStatus,
    AlgorithmStatus,
    RLWeights,
    RLActionSelection,
    UserStudyPhaseEnum,
)

rlservice_blueprint = Blueprint("rlservice", __name__)


class RegisterAPI(MethodView):
    """
    Register users (API called by the client to send info about users)
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user already exists
        user = User.query.filter_by(id=post_data.get("id")).first()

        # if user does not exist, add the user
        if not user:
            user = User(
                id=int(post_data.get("id")),
                age=post_data.get("age"),
                gender=post_data.get("gender"),
                start_date=post_data.get("start_date"),
                end_date=post_data.get("end_date"),
                study_level_start_index=post_data.get("study_level_start_index"),
                study_level_end_index=post_data.get("study_level_end_index"),
            )

            user_status = UserStatus(
                user_id=int(post_data.get("id")),
                study_phase=UserStudyPhaseEnum.REGISTERED,
                study_day=0,
                morning_notification_time_start=post_data.get(
                    "morning_notification_time_start"
                ),
                evening_notification_time_start=post_data.get(
                    "evening_notification_time_start"
                ),
            )

            # insert the user and userstatus
            db.session.add(user)
            db.session.commit()
            db.session.add(user_status)
            db.session.commit()

            responseObject = {
                "status": "success",
                "message": "Successfully registered.",
            }
            return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                "status": "fail",
                "message": "User already exists.",
            }
            return make_response(jsonify(responseObject)), 202


class ActionsAPI(MethodView):
    """
    Get actions for the specified user
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user already exists
        user = User.query.filter_by(id=post_data.get("id")).first()

        # if user does not exist, return fail
        if not user:
            responseObject = {
                "status": "fail",
                "message": "User does not exist.",
            }
            return make_response(jsonify(responseObject)), 202
        else:
            pass


# define the API resources
registration_view = RegisterAPI.as_view("user_register_api")
action_selection_view = ActionsAPI.as_view("user_actions_api")

# add Rules for API Endpoints
rlservice_blueprint.add_url_rule(
    "/register", view_func=registration_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/actions", view_func=action_selection_view, methods=["POST"]
)
