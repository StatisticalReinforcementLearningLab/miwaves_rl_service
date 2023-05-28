# src/server/main.py

# Server code that hosts the main RL API

import numpy as np
import requests

from src.server.auth.auth import token_required

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import app, db
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

def get_user_data_for_state(user_id: int, decision_idx: int) -> tuple(np.ndarray, np.ndarray):
    """
    Get the data from database to help generate the state for a user on a given day
    """
    # Get all user specific data from the rlactionselection table
    user_data_query = RLActionSelection.query.filter_by(user_id=user_id)

    # Filter the data for the past ENGAGEMENT_DATA_WINDOW days and get the engagement column
    engagement_data = user_data_query.filter(
        RLActionSelection.decision_idx >= decision_idx - app.config["ENGAGEMENT_DATA_WINDOW"]
    ).with_entities(RLActionSelection.reward).all()

    # Filter the data for the past CANNABIS_USE_DATA_WINDOW days and get the cannabis_use column
    cannabis_use_data = user_data_query.filter(
        RLActionSelection.decision_idx >= decision_idx - app.config["CANNABIS_USE_DATA_WINDOW"]
    ).with_entities(RLActionSelection.cannabis_use).all()

    # convert engagement data to numpy array
    engagement_data = np.array(engagement_data)

    # convert cannabis use data to numpy array
    cannabis_use_data = np.array(cannabis_use_data)

    # TODO: Check for None values in the data and replace them with empty arrays
    # Return the engagement and cannabis use data
    return engagement_data, cannabis_use_data

def get_data(decision_time: int) -> None:
    """
    Gets the latest data from the backend api for
    the particular decision_time and for all active users
    """

    try:
        # Get the latest ema data from the backend api
        ema_url = app.config.get('EMA_API')

        # Iterate over all the users in userstatus tables
        for user in UserStatus.query.all():

            if user.user_study_phase != UserStudyPhaseEnum.STARTED or \
                user.user_status != UserStudyPhaseEnum.COMPLETED_AWAITING_REVIEW:
                continue

            # Get used id
            user_id = user.id

            # Create payload for the backend api
            payload = {
                'user_id': user_id,
                'decision_time': decision_time
            }

            # Get the latest ema data for the user from the backend api
            data = requests.get(ema_url, params=payload).json()

            # Get the ema data from the response
            ema_data = data['ema_data']

            # Check if the ema data is empty
            if not ema_data:
                pass
            else:
                # Iterate over all the decision points in each day of the ema data
                for key, value in ema_data.items():
                    # Get the decision point
                    decision_time_idx = key

                    # Get the decision point data
                    decision_point_data = value

                    # Get the data fields from the decision point data
                    date = decision_point_data['date']
                    


            
            # Get the latest user's study phase from the backend api
            try:
                study_phase = data['study_phase']

                if not study_phase:
                    pass
                else:
                    # Update the user's study phase in the database
                    if study_phase == 'ended':
                        user.user_study_phase = UserStudyPhaseEnum.ENDED
            except Exception as e:
                # If DEBUG is True, print the error
                if app.config.get('DEBUG'):
                    print(e)
                pass
            
     

    except Exception as e:
        if app.config.get('DEBUG'):
            print(e)
        return

class RegisterAPI(MethodView):
    """
    Register users (API called by the client to send info about users)
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user already exists
        user = User.query.filter_by(id=post_data.get("user_id")).first()

        # if user does not exist, add the user
        try:
            if not user:
                user = User(
                    id=int(post_data.get("user_id")),
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

        # get the user id
        user_id = post_data.get("user_id")

        # check if user exists
        user = User.query.filter_by(id=user_id).first()

        try:
            # if user does not exist, return fail
            if not user:
                responseObject = {
                    "status": "fail",
                    "message": "User does not exist.",
                }
                return make_response(jsonify(responseObject)), 202
            else:
                # Check the user_status
                user_status = UserStatus.query.filter_by(id=user_id).first()

                # If the user is in the registered phase, set it to started
                if user_status.study_phase == UserStudyPhaseEnum.REGISTERED:
                    user_status.study_phase = UserStudyPhaseEnum.STARTED
                    db.session.commit()

                decision_idx = post_data.get("decision_idx")
                
                # Check if this is the last decision point for the user
                if decision_idx == app.config.get("STUDY_LENGTH"):
                    user_status.study_phase = UserStudyPhaseEnum.COMPLETED_AWAITING_REVIEW
                    db.session.commit()
                
                # Get whether the user finished the ema
                user_finished_ema = post_data.get("finished_ema")

                # Get what the user answered to the activity question
                activity_response = post_data.get("activity_question_response")

                # Get the user's cannabis use level
                cannabis_use = post_data.get("cannabis_use")

                # Get the algorithm
                algorithm = app.config.get("ALGORITHM")

                # Make the last reward
                last_reward = algorithm.make_reward(
                    {
                        "user_finished_ema": user_finished_ema,
                        "activity_response": activity_response
                    }
                )

                # Get the data for determining the user's state
                engagement_data, cannabis_use_data = get_user_data_for_state(
                    user_id=user_id,
                    decision_idx=post_data.get("decision_idx")
                )

                # Make the user's state
                state = algorithm.make_state(
                    {
                        "engagement_data": engagement_data,
                        "cannabis_use_data": cannabis_use_data,
                        "cannabis_use": cannabis_use,
                        "last_reward": last_reward
                    }
                )

                # Get the action
                action, seed, act_prob, policy_id = algorithm.get_action(
                    user_id=user_id,
                    state=state,
                    decision_time=decision_idx
                )

                # TODO: Make another database to store all of the information above
                # instead of relying on the backend to transmit the same information
                # back when the final action is selected

                # Make the response object
                responseObject = {
                    "status": "success",
                    "action": action,
                    "seed": seed,
                    "act_prob": act_prob,
                    "policy_id": policy_id,
                }

                return make_response(jsonify(responseObject)), 200
                

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
        user = User.query.filter_by(id=post_data.get("user_id")).first()

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


class DecisionTimeEndAPI(MethodView):
    """
    Update the system's state to signify end of decision time
    and force it to call the backend api to fetch data for all users
    for that decision point
    """
    
    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # get the decision idx
        decision_idx = post_data.get("decision_idx")


# define the API resources
registration_view = RegisterAPI.as_view("user_register_api")
action_selection_view = ActionsAPI.as_view("user_actions_api")
update_model_view = UpdateModelAPI.as_view("update_model_api")
update_notification_time_view = UpdateNotificationTimeAPI.as_view(
    "update_notification_time_api"
)
decision_time_end_view = DecisionTimeEndAPI.as_view("decision_time_end_api")

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
