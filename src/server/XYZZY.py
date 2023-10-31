from src.server import db
from src.server.auth.auth import token_required
from src.server.tables import User, UserStatus


from flask import jsonify, make_response, request
from flask.views import MethodView


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