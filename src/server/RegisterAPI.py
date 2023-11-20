from src.server import app, db
from src.server.auth.auth import token_required
from src.server.tables import User, UserStatus, UserStudyPhaseEnum


from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server.helpers import return_fail_response

import traceback


def check_all_fields_present(post_data) -> tuple[bool, str, int]:
    """
    Check if all fields are present in the post data
    """

    if not post_data.get("user_id") and not isinstance(post_data.get("user_id"), str):
        return False, "Please provide a valid user id.", 100
    if not post_data.get("rl_start_date"):
        return False, "Please provide a valid rl start date.", 101
    if not post_data.get("rl_end_date"):
        return False, "Please provide a valid rl end date.", 102
    if not post_data.get("consent_start_date"):
        return False, "Please provide a valid consent start date.", 103
    if not post_data.get("consent_end_date"):
        return False, "Please provide a valid consent end date.", 104
    if not post_data.get("morning_notification_time_start"):
        return False, "Please provide a valid morning notification time.", 105
    if not post_data.get("evening_notification_time_start"):
        return False, "Please provide a valid evening notification time.", 106
    return True, None, None


class RegisterAPI(MethodView):
    """
    Register users (API called by the client to send info about users)
    """

    @token_required
    def post(self):

        app.logger.info("RegisterAPI called")

        # get the post data
        post_data = request.get_json()

        app.logger.info(f"post_data: {post_data}")

        # check if user already exists
        user = User.query.filter_by(user_id=post_data.get("user_id")).first()

        # if user does not exist, add the user
        try:
            if not user:
                # Check all fields are present
                status, message, ec = check_all_fields_present(post_data)
                if not status:
                    return return_fail_response(message, 202, ec)

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
                    app.logger.error("Error adding user info to internal database: %s", e)
                    app.logger.error(traceback.format_exc())
                    if app.config.get("DEBUG"):
                        print(e)
                        traceback.print_exc()
                    error_message = "Some error occurred while adding user info to internal database. Please try again."
                    ec = 107
                    return return_fail_response(error_message, 401, ec)
                else:
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": f"User {post_data.get('user_id')} was added!",
                    }
                    return make_response(jsonify(responseObject)), 201
            else:
                message = f"User {post_data.get('user_id')} already exists."
                ec = 108
                return return_fail_response(message, 202, ec)
            
        except Exception as e:
            if app.config.get("DEBUG"):
                print(e)  # TODO: Set it to logger
            app.logger.error("Error adding user info to internal database: %s", e)
            app.logger.error(traceback.format_exc())
            db.session.rollback()
            message = "Some error occurred while adding user info to internal database. Please try again."
            ec = 109
            return return_fail_response(message, 401, ec)
