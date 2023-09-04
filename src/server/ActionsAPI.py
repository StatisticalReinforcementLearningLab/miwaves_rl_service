from src.server import app, db
from src.server.auth.auth import token_required
from src.server.tables import (
    User,
    UserStatus,
    UserStudyPhaseEnum,
    RLActionSelection,
    UserActionHistory,
)


from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server.helpers import return_fail_response

import numpy as np


class ActionsAPI(MethodView):
    """
    Get actions for the specified user
    """

    @staticmethod
    def check_all_fields_present(post_data: dict) -> tuple[bool, str]:
        """
        Check if all fields are present in the post data
        :param post_data: The post data from the request
        """

        if not post_data.get("user_id"):
            return False, "Please provide a valid user id."
        if post_data.get("finished_ema") is None or not isinstance(
            post_data.get("finished_ema"), bool
        ):
            return False, "Please provide a valid finished ema."
        if post_data.get("app_use_flag") is None or not isinstance(
            post_data.get("app_use_flag"), bool
        ):
            return False, "Please provide a valid app use flag."
        # if not post_data.get("activity_question_response"):
        #     return False, "Please provide a valid activity question response."
        # if not post_data.get("cannabis_use"):
        #     return False, "Please provide a valid cannabis use."
        return True, None

    @staticmethod
    def get_raw_reward_data(post_data: dict) -> dict:
        """
        Get the raw reward data from the post data
        and return it in a dictionary. Also return
        whether the data was successfully retrieved
        :param post_data: The post data from the request
        """
        # Get whether the user finished the ema
        user_finished_ema = post_data.get("finished_ema")

        # Get what the user answered to the activity question
        activity_response = post_data.get("activity_question_response")

        # Get whether the user used the app outside of the survey
        # for more than 10 seconds since the last decision point
        used_app = post_data.get("app_use_flag")

        # Return the raw reward data
        raw_reward_data = {
            "user_finished_ema": user_finished_ema,
            "used_app": used_app,
            "activity_response": activity_response,
        }

        return raw_reward_data

    @staticmethod
    def _get_user_data_for_state(
        user_id: str, decision_idx: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Get the data from database to help generate the state for a user on a given day
        :param user_id: The user id
        :param decision_idx: The decision index
        """
        # Get all user specific data from the rlactionselection table
        user_data_query = RLActionSelection.query.filter_by(user_id=user_id)

        # Filter the data for the past ENGAGEMENT_DATA_WINDOW days and get the engagement column
        engagement_data = (
            user_data_query.filter(
                RLActionSelection.user_decision_idx
                > decision_idx - app.config["ENGAGEMENT_DATA_WINDOW"]
            )
            .with_entities(RLActionSelection.reward)
            .all()
        )

        # Filter the data for the past CANNABIS_USE_DATA_WINDOW days and get the cannabis_use column
        cannabis_use_data = (
            user_data_query.filter(
                RLActionSelection.user_decision_idx
                > decision_idx - app.config["CANNABIS_USE_DATA_WINDOW"]
            )
            .with_entities(RLActionSelection.cannabis_use)
            .all()
        )

        # convert engagement data to numpy array
        engagement_data = np.array(engagement_data)

        # convert cannabis use data to numpy array
        cannabis_use_data = np.array(cannabis_use_data)

        # TODO: Check for None values in the data and replace them with empty arrays
        # Return the engagement and cannabis use data
        return engagement_data, cannabis_use_data

    def get_raw_state_data(
        self,
        post_data: dict,
        user_id: str,
        decision_idx: int,
        time_of_day: int,
        reward: float,
    ):
        """
        Get the raw state data from the post data and the database
        and return it in a dictionary.
        :param post_data: The post data from the request
        :param user_id: The user id
        :param decision_idx: The decision index (t)
        :param time_of_day: The time of day
        :param reward: The reward for previous action (R_t)
        """
        # Get the user's cannabis use
        # This will be some sort of dictionary of the hours
        # in which they used cannabis
        recent_cannabis_use = post_data.get("cannabis_use")

        if recent_cannabis_use == "NA":
            recent_cannabis_use = []

        # Get the data for determining the user's state
        engagement_data, cannabis_use_data = self._get_user_data_for_state(
            user_id=user_id, decision_idx=decision_idx
        )

        raw_state_data = {
            "engagement_data": engagement_data,
            "cannabis_use_data": cannabis_use_data,
            "recent_cannabis_use": recent_cannabis_use,
            "time_of_day": time_of_day,
            "reward": reward,
        }

        return raw_state_data

    @token_required
    def post(self):
        """
        Get actions for the specified user
        """
        # get the post data
        post_data = request.get_json()

        # get the user id
        user_id = post_data.get("user_id")

        # check if user exists
        user = User.query.filter_by(user_id=user_id).first()

        try:
            # if user does not exist, return fail
            if not user:
                return return_fail_response(
                    message=f"User {user_id} does not exist.",
                    code=202,
                )
                # responseObject = {
                #     "status": "fail",
                #     "message": f"User {user_id} does not exist.",
                # }
                # return make_response(jsonify(responseObject)), 202
            else:
                try:
                    # Check all fields are present
                    status, message = self.check_all_fields_present(post_data)

                    if not status:
                        return return_fail_response(
                            message=message,
                            code=202,
                        )

                    # Check the user_status
                    user_status = UserStatus.query.filter_by(user_id=user_id).first()

                    # If the user is in the registered phase, set it to started
                    if user_status.study_phase == UserStudyPhaseEnum.REGISTERED:
                        user_status.study_phase = UserStudyPhaseEnum.STARTED

                    # Get the decision index and time of day
                    decision_idx = user_status.current_decision_index + 1
                    time_of_day = 1 - user_status.current_time_of_day

                    # Check if this is the last decision point for the user
                    if decision_idx == app.config.get("STUDY_LENGTH"):
                        user_status.study_phase = (
                            UserStudyPhaseEnum.COMPLETED_AWAITING_REVIEW
                        )

                    # Get the raw reward data
                    raw_reward_data = self.get_raw_reward_data(post_data)

                    # Get the algorithm
                    algorithm = app.config.get("ALGORITHM")

                    # Make the reward
                    try:
                        reward = algorithm.make_reward(raw_reward_data)
                    except Exception as e:
                        if app.config.get("DEBUG"):
                            print(e)
                        return return_fail_response(
                            message="Failed to compute reward",
                            code=202,
                        )

                    raw_state_data = self.get_raw_state_data(
                        post_data, user_id, decision_idx, time_of_day, reward
                    )

                    # Make the user's state
                    try:
                        state = algorithm.make_state(raw_state_data)
                    except Exception as e:
                        if app.config.get("DEBUG"):
                            print(e)
                        return return_fail_response(
                            message="Failed to compute state",
                            code=202,
                        )

                    # Get the action
                    try:
                        action, seed, act_prob, policy_id = algorithm.get_action(
                            user_id=user_id, state=state, decision_time=decision_idx
                        )

                        new_useraction = UserActionHistory(
                            user_id,
                            decision_idx,
                            raw_reward_data["user_finished_ema"],
                            raw_reward_data["activity_response"],
                            raw_reward_data["used_app"],
                            raw_state_data["recent_cannabis_use"],
                            reward,
                            state,
                            action,
                            seed,
                            act_prob,
                            policy_id,
                        )

                        db.session.add(new_useraction)

                    except Exception as e:
                        db.session.rollback()
                        if app.config.get("DEBUG"):
                            print(e)
                        return return_fail_response(
                            message="Failed to compute action",
                            code=202,
                        )

                except Exception as e:
                    if app.config.get("DEBUG"):
                        print(e)
                    return return_fail_response(
                        message="Some error occurred. Please try again.",
                        code=401,
                    )

                else:
                    db.session.commit()

                    # Make the response object
                    responseObject = {
                        "status": "success",
                        "rid": new_useraction.index,
                        "action": action,
                        "seed": seed,
                        "act_prob": act_prob,
                        "policy_id": policy_id,
                        "decision_index": decision_idx,
                        "act_gen_timestamp": new_useraction.timestamp,
                    }

                    return make_response(jsonify(responseObject)), 200

        except Exception as e:
            print(e)
            return return_fail_response(
                message="Some error occurred. Please try again.",
                code=401,
            )
