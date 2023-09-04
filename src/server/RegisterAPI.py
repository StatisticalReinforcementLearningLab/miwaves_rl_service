from src.server import db
from src.server.auth.auth import token_required
from src.server.tables import User, UserStatus, UserStudyPhaseEnum


from flask import jsonify, make_response, request
from flask.views import MethodView

import traceback


def check_all_fields_present(post_data):
    """
    Check if all fields are present in the post data
    """

    if not post_data.get("user_id"):
        return False, "Please provide a valid user id."
    if not post_data.get("rl_start_date"):
        return False, "Please provide a valid rl start date."
    if not post_data.get("rl_end_date"):
        return False, "Please provide a valid rl end date."
    if not post_data.get("consent_start_date"):
        return False, "Please provide a valid consent start date."
    if not post_data.get("consent_end_date"):
        return False, "Please provide a valid consent end date."
    if not post_data.get("morning_notification_time_start"):
        return False, "Please provide a valid morning notification time."
    if not post_data.get("evening_notification_time_start"):
        return False, "Please provide a valid evening notification time."
    return True, None


class RegisterAPI(MethodView):
    """
    Register users (API called by the client to send info about users)
    """

    @token_required
    def post(self):
        # get the post data
        post_data = request.get_json()

        # check if user already exists
        user = User.query.filter_by(user_id=post_data.get("user_id")).first()

        # if user does not exist, add the user
        try:
            if not user:
                # Check all fields are present
                status, message = check_all_fields_present(post_data)
                if not status:
                    responseObject = {
                        "status": "fail",
                        "message": message,
                    }
                    return make_response(jsonify(responseObject)), 202

                user = User(
                    user_id=str(post_data.get("user_id")),
                    rl_start_date=post_data.get(
                        "rl_start_date"
                    ),  # TODO: Change based on Pei-Yao's specification
                    rl_end_date=post_data.get("rl_end_date"),
                    consent_start_date=post_data.get(
                        "rl_start_date"
                    ),  # TODO: Change based on Pei-Yao's specification
                    consent_end_date=post_data.get("rl_end_date"),
                    # study_level_start_index=post_data.get("study_level_start_index"), #TODO: for now not required
                    # study_level_end_index=post_data.get("study_level_end_index"),
                )

                user_status = UserStatus(
                    user_id=str(post_data.get("user_id")),
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
                try:
                    db.session.add(user)
                    db.session.add(user_status)
                except Exception as e:
                    db.session.rollback()
                    print(e)  # TODO: Set it to logger
                    traceback.print_exc()
                    responseObject = {
                        "status": "fail",
                        "message": "Some error occurred while adding user info to internal database. Please try again.",
                    }
                    return make_response(jsonify(responseObject)), 401
                else:
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": f"User {post_data.get('user_id')} was added!",
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    "status": "fail",
                    "message": f"User {post_data.get('user_id')} already exists.",
                }
                return make_response(jsonify(responseObject)), 202
        except Exception as e:
            print(e)  # TODO: Set it to logger
            db.session.rollback()
            responseObject = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return make_response(jsonify(responseObject)), 401
