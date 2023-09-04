# src/algorithm/flat_prob.py

# Imports
import numpy as np
import pandas as pd
from src.algorithm.base import RLAlgorithm


class FlatProbabilityAlgorithm(RLAlgorithm):
    """Flat probability algorithm"""

    def __init__(self, nusers: int = 10, prob: float = 0.5) -> None:
        """
        Initialize flat probability algorithm
        :param nusers: number of users
        :param prob: probability of taking action
        """
        self.prob = prob
        self.policyid = 0
        self.maxseed = 2**16 - 1

    def get_action(
        self, user_id: int, state: np.ndarray, decision_time: int, seed: int = -1
    ) -> tuple[int, int, float, int]:
        """
        Get action
        :param user_id: user id of the user
        :param state: state of the user
        :param decision_time: decision time of the user for which action is to be taken
        :param seed: seed for random number generator
        :return: action, seed, probability of taking action, and policy id
        """

        if seed != -1:
            np.random.seed(seed)
        else:
            # set seed
            np.random.seed()

            # generate seed
            seed = np.random.randint(0, self.maxseed)

            # set seed
            np.random.seed(seed)

        # get action
        action = np.random.binomial(1, self.prob)

        return action, seed, self.prob, self.policyid

    def update(self, data: pd.DataFrame) -> tuple[bool, str, int, dict]:
        """
        Update algorithm
        :param data: data to update algorithm
        :return: True if algorithm is updated, False otherwise
        :return: error message if algorithm is not updated, None otherwise
        :return: policy id
        :return: algorithm parameters
        """
        # TODO: Put checks for dataframe columns

        # Dump the data to a csv file

        self.policyid += 1

        return True, "", self.policyid, {}

    @staticmethod
    def make_state(params: dict) -> list:
        """
        Make state from parameters
        :param params: parameters
        :return: state
        """

        if "engagement_data" not in params:
            raise ValueError("engagement_data not in params")
        if "recent_cannabis_use" not in params:
            raise ValueError("recent_cannabis_use not in params")
        if "reward" not in params:
            raise ValueError("reward not in params")
        if "time_of_day" not in params:
            raise ValueError("time_of_day not in params")

        # if "cannabis_use_data" not in params:
        #     raise ValueError("cannabis_use_data not in params")

        engagement_data = params["engagement_data"]
        recent_cannabis_use = np.array(params["recent_cannabis_use"])
        reward = params["reward"]
        time_of_day = params["time_of_day"]

        # TODO: Change based on 12/24 hour weighted avg.
        # cannabis_use_data = params["cannabis_use_data"]

        average_reward = np.mean([*engagement_data[-2:], reward])

        # create S1
        if average_reward >= 2:
            S1 = 1
        else:
            S1 = 0

        # create S2 based on time of day
        S2 = time_of_day

        # create S3 based on last cannabis use
        # if user used cannabis in the past decision point, S3 = 1
        # else S3 = 0
        # if recent_cannabis_use == 1:
        #     S3 = 1
        # elif recent_cannabis_use == 0:
        #     S3 = 0
        # else:
        #     S3 = 1
        if np.any(recent_cannabis_use == 1):
            S3 = 1
        elif np.all(recent_cannabis_use == 0):
            S3 = 0
        else:
            S3 = 1

        return [S1, S2, S3]

    @staticmethod
    def make_reward(params: dict) -> float:
        """
        Make reward from parameters
        :param params: parameters
        :return: reward
        """
        param_keys = params.keys()

        if "user_finished_ema" not in param_keys:
            raise ValueError("user_finished_ema not in params")
        if "used_app" not in param_keys:
            raise ValueError("used_app not in params")
        if "activity_response" not in param_keys:
            raise ValueError("activity_response not in params")

        reward = 0

        if params["user_finished_ema"]:
            if params["activity_response"]:
                reward = 3
            else:
                reward = 2
        elif params["used_app"]:
            reward = 1
        return reward

    def get_policyid(self) -> int:
        """
        Get policy id
        This is used to check if the algorithm has been updated
        Only used for testing
        :return: policy id
        """
        return self.policyid
