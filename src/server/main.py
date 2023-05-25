# src/server/main.py

# Server code that hosts the main RL API

from src.server.auth.auth import token_required

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import db
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
        try:
            if not user:
                user = User(
                    id=int(post_data.get("id")),
                    start_date=post_data.get("start_date"),
                    end_date=post_data.get("end_date"),
                    study_level_start_index=post_data.get("study_level_start_index"),
                    study_level_end_index=post_data.get("study_level_end_index"),
                )

                user_status = UserStatus(
                    id=int(post_data.get("id")),
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
        except Exception as e:
            print(e)
            responseObject = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return make_response(jsonify(responseObject)), 401


class ActionsAPI(MethodView):
    """
    Get actions for the specified user
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user exists
        user = User.query.filter_by(id=post_data.get("id")).first()

        try:
            # if user does not exist, return fail
            if not user:
                responseObject = {
                    "status": "fail",
                    "message": "User does not exist.",
                }
                return make_response(jsonify(responseObject)), 202
            else:
                pass
        except Exception as e:
            print(e)
            responseObject = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return make_response(jsonify(responseObject)), 401


class UpdateModelAPI(MethodView):
    """
    Update model weights of the RL algorithm
    """

    @token_required
    def post(self):
        pass


class UpdateNotificationTimeAPI(MethodView):
    """
    Update notification time of the user
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user exists
        user = User.query.filter_by(id=post_data.get("id")).first()

        try:
            # if user does not exist, return fail
            if not user:
                responseObject = {
                    "status": "fail",
                    "message": "User does not exist.",
                }
                return make_response(jsonify(responseObject)), 202
            else:
                # update the notification time
                user_status = UserStatus.query.filter_by(id=post_data.get("id")).first()
                user_status.morning_notification_time_start = post_data.get(
                    "morning_notification_time_start"
                )
                user_status.evening_notification_time_start = post_data.get(
                    "evening_notification_time_start"
                )
                db.session.commit()

                responseObject = {
                    "status": "success",
                    "message": "Successfully updated notification time.",
                }
                return make_response(jsonify(responseObject)), 200
        except Exception as e:
            print(e)
            responseObject = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return make_response(jsonify(responseObject)), 401


# define the API resources
registration_view = RegisterAPI.as_view("user_register_api")
action_selection_view = ActionsAPI.as_view("user_actions_api")
update_model_view = UpdateModelAPI.as_view("update_model_api")
update_notification_time_view = UpdateNotificationTimeAPI.as_view(
    "update_notification_time_api"
)

# add Rules for API Endpoints
rlservice_blueprint.add_url_rule(
    "/register", view_func=registration_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/actions", view_func=action_selection_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/update_model", view_func=update_model_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/notif_time_change",
    view_func=update_notification_time_view,
    methods=["POST"],
)
