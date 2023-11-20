import datetime
import json
from src.server.ActionsAPI import ActionsAPI
from src.algorithm.base import RLAlgorithm
from src.server import app, db
from src.server.tables import (
    RLActionSelection,
    User,
    UserActionHistory,
    UserStatus,
    UserStudyPhaseEnum,
)
from src.server.auth.auth import token_required
from src.server.helpers import return_fail_response


from flask import jsonify, make_response, request
from flask.views import MethodView
import requests
import traceback


class DecisionTimeEndAPI(MethodView):
    """
    Update the system's state to signify end of decision time
    for a given user. This API is called by the client.
    Increase the decision time index for that user by one.
    """

    @token_required
    def post(self):
        app.logger.info("DecisionTimeEndAPI called")

        # get the post data
        post_data = request.get_json()

        # get the user_id
        user_id = post_data.get("user_id")

        app.logger.info("DecisionTimeEndAPI for User id: %s", user_id)

        # get the user for which decision time has ended
        user = User.query.filter_by(user_id=user_id).first()

        try:
            if not user:
                app.logger.error("User does not exist: %s", user_id)
                return return_fail_response(
                    message="User does not exist.", code=202, error_code=300
                )
            else:
                # get the user's study phase
                user_status = UserStatus.query.filter_by(user_id=user_id).first()

                # if user study phase is not started, return fail
                if user_status.study_phase != UserStudyPhaseEnum.STARTED:
                    app.logger.error(
                        "User study phase has not started for user: %s %s",
                        user_id,
                        user_status.study_phase,
                    )
                    return return_fail_response(
                        message="User study phase has not started.",
                        code=202,
                        error_code=301,
                    )

                # if user study phase is ended, return fail
                if user_status.study_phase == UserStudyPhaseEnum.ENDED:
                    app.logger.error(
                        "User study phase has ended for user: %s %s",
                        user_id,
                        user_status.study_phase,
                    )
                    return return_fail_response(
                        message="User study phase has ended.", code=202, error_code=302
                    )

                # if user study phase has not ended, get the last decision time index data
                else:
                    # Get the algorithm
                    algorithm = app.config.get("ALGORITHM")

                    # Query the backend/client for data for the user for the current decision time
                    status, message, ec = self.update_data(user, algorithm)

                    if not status:
                        app.logger.error(
                            "Error occured in update data for: %s %s %s",
                            user_id,
                            status,
                            message,
                        )
                        if app.config.get("DEBUG"):
                            print(message)
                        return return_fail_response(
                            message=message, code=202, error_code=ec
                        )

                    # TODO: Keeping this here until there is only one
                    # return response check. Later, move this inside update_data
                    # update the decision time index
                    user_status.current_decision_index += 1

                    # update the user's current time of day
                    user_status.current_time_of_day = (
                        1 - user_status.current_time_of_day
                    )

                    # if the current time of day is morning i.e. 0, update study day
                    if user_status.current_time_of_day == 0:
                        # get the current study day
                        user_status.study_day += 1

                    if (
                        user_status.study_phase
                        == UserStudyPhaseEnum.COMPLETED_AWAITING_REVIEW
                    ):
                        # update the user's study phase
                        user_status.study_phase = UserStudyPhaseEnum.ENDED

                    # commit the changes to the database
                    db.session.commit()

                    responseObject = {
                        "status": "success",
                        "message": "Successfully updated decision time index.",
                    }
                    return make_response(jsonify(responseObject)), 200

        except Exception as e:
            db.session.rollback()
            app.logger.error("Error occured in DecisionTimeEndAPI: %s", e)
            if app.config.get("DEBUG"):
                print(e)
            return return_fail_response(
                message="Some error occurred. Please try again.",
                code=401,
                error_code=303,
            )

    @staticmethod
    def check_all_fields_present(post_data: dict) -> tuple[bool, str, int]:
        """
        Check if all fields are present in the post data
        """

        status, message, ec = ActionsAPI.check_all_fields_present(post_data)

        if not status:
            return status, message, ec

        if post_data.get("action_taken") is None or post_data.get(
            "action_taken"
        ) not in [
            0,
            1,
        ]:
            return False, "Please provide a valid action taken.", 304

        if post_data.get("seed") is None or not isinstance(post_data.get("seed"), int):
            return False, "Please specify the seed used for the action selection.", 305

        if post_data.get("act_prob") is None or not isinstance(
            post_data.get("act_prob"), float
        ):
            return False, "Please specify the probability of action taken.", 306

        if post_data.get("policy_id") is None or not isinstance(
            post_data.get("policy_id"), int
        ):
            return False, "Please specify the policy id.", 307

        if post_data.get("decision_index") is None or not isinstance(
            post_data.get("decision_index"), int
        ):
            return False, "Please specify the decision index.", 308

        if post_data.get("act_gen_timestamp") is None:
            return False, "Please specify the action generation timestamp.", 309

        if post_data.get("rid") is None or not isinstance(post_data.get("rid"), int):
            return False, "Please specify the action request id.", 310

        if post_data.get("timestamp_finished_ema") is None:
            return (
                False,
                "Please specify the timestamp when the ema was completed.",
                311,
            )

        if post_data.get("message_notification_sent_time") is None:
            return False, "Please specify the time when the message notifications sent", 312

        if post_data.get("message_notification_click_time") is None:
            return False, "Please specify the time when the message notification was clicked", 313

        if post_data.get("morning_notification_time_start") is None or not isinstance(
            post_data.get("morning_notification_time_start"), list
        ):
            return False, "Please specify the morning notification time start.", 314

        if post_data.get("evening_notification_time_start") is None or not isinstance(
            post_data.get("evening_notification_time_start"), list
        ):
            return False, "Please specify the evening notification time start.", 315

        return True, None, None

    def update_data(self, user: User, algorithm: RLAlgorithm) -> tuple[bool, str]:
        """
        Gets the latest data from the backend api for
        the particular decision_time and for a given user
        and updates the database
        """

        try:
            # Get the latest ema data from the backend api
            ema_url = app.config.get("EMA_API")

            # Get used id
            user_id = user.user_id

            # Get current time
            end_time = datetime.datetime.now()

            # Get the time 3 hours prior
            start_time = end_time - datetime.timedelta(hours=3)

            # Create payload for the backend api
            payload = {
                "user_id": user_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

            print(json.dumps(payload))
            app.logger.info("Payload sent to the backend api: %s", payload)

            # Get the latest ema data for the user from the backend api
            data = requests.post(
                ema_url, data=json.dumps(payload), headers=app.config.get("HEADERS")
            ).json()

            if app.config.get("DEBUG"):
                print(data)
                
            app.logger.info("Data returned from the backend api: %s", data)

            if data["status"] == "fail":
                return False, data["message"], 316

            # Get the ema data from the response
            ema_data = data["ema_data"]

            # Check if the ema data is empty
            if not ema_data:
                return False, "No data returned from the backend api.", 317
            else:
                # Iterate over all the decision points returned by the backend api
                # But there should ONLY be one decision point
                # TODO: Make a check for only one decision point

                if len(ema_data) > 1:
                    return (
                        False,
                        "More than one decision point returned by the backend api.",
                        318,
                    )

                for key, value in ema_data.items():
                    # First check if all fields are present
                    status, message, ec = self.check_all_fields_present(value)

                    # If all fields are not present, continue, and log the event
                    if not status:
                        if app.config.get("DEBUG"):
                            print(key, value)
                            print(message)
                        return False, message, ec

                    # Get the user status for the user
                    user_status = UserStatus.query.filter_by(user_id=user_id).first()

                    # TODO: Add postgres SAVEPOINTS and session managers

                    # Update the morning and evening notification time start
                    user_status.morning_notification_time_start = value.get(
                        "morning_notification_time_start"
                    )
                    user_status.evening_notification_time_start = value.get(
                        "evening_notification_time_start"
                    )

                    # Get the action history using rid
                    action_history = UserActionHistory.query.filter_by(
                        index=value.get("rid")
                    ).first()

                    if action_history is None:
                        return (
                            False,
                            "No action found for the given rid. Please try again.",
                            319,
                        )

                    print(value.get("rid"))
                    print(action_history)

                    app.logger.info("RID: %s", value.get("rid"))
                    app.logger.info("Action history: %s", action_history)
                    

                    cb_use = value.get("cannabis_use")
                    if cb_use == "NA":
                        cb_use = []

                    # Update the algorithm with the data
                    try:
                        algorithm.update_design_row(
                            user_id=user_id,
                            state=action_history.state,
                            action=int(value.get("action_taken")),
                            act_prob=value.get("act_prob"),
                            reward=action_history.reward,
                            decision_index=int(value.get("decision_index")),
                        )
                    except Exception as e:
                        if app.config.get("DEBUG"):
                            print(e)
                            traceback.print_exc()
                        app.logger.error(
                            "Error occured in update_data: %s", traceback.format_exc()
                        )
                        return (
                            False,
                            "Some error occurred while updating the algorithm with the data.",
                            321,
                        )

                    # Add a record to RLActionSelection table
                    rl_action_selection = RLActionSelection(
                        user_id=user_id,
                        user_decision_idx=value.get("decision_index"),
                        morning_notification_time=value.get(
                            "morning_notification_time_start"
                        ),
                        evening_notification_time=value.get(
                            "evening_notification_time_start"
                        ),
                        day_in_study=user_status.study_day,
                        action=value.get("action_taken"),
                        policy_id=value.get("policy_id"),
                        seed=value.get("seed"),
                        prior_ema_completion_time=value.get("timestamp_finished_ema"),
                        action_selection_timestamp=value.get("act_gen_timestamp"),
                        message_sent_notification_timestamp=value.get("message_notification_sent_time"),
                        message_click_notification_timestamp=value.get(
                            "message_notification_click_time"
                        ),
                        act_prob=value.get("act_prob"),
                        cannabis_use=cb_use,
                        state_vector=action_history.state,
                        reward=action_history.reward,
                        row_complete=True,
                    )

                    db.session.add(rl_action_selection)

        except Exception as e:
            db.session.rollback()
            if app.config.get("DEBUG"):
                print(e)
            app.logger.error("Error occured in update_data: %s", e)
            app.logger.error("Error occured in update_data: %s", traceback.format_exc())
            return False, "Some error occurred. Please try again.", 320

        else:
            db.session.commit()

        return True, "Successfully updated decision time index.", None
