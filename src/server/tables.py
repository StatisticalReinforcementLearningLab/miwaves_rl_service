# src/server/tables.py

# Server code that has the database table schemas for the users and algorithms in the trial

import datetime
import enum

from src.server import app, db
from sqlalchemy.dialects.postgresql import ARRAY



class User(db.Model):
    """User Model for storing user related details"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    study_level_start_index = db.Column(db.Integer, nullable=True)
    study_level_end_index = db.Column(db.Integer, nullable=True)
    # TODO: Add columns for other baseline details of the user

    def __init__(
        self,
        id: int,
        start_date: datetime.date,
        end_date: datetime.date,
        study_level_start_index: int,
        study_level_end_index: int,
    ):
        self.id = id
        self.start_date = start_date
        self.end_date = end_date
        self.study_level_start_index = study_level_start_index
        self.study_level_end_index = study_level_end_index

    def update_study_level_start_index(self, study_level_start_index: int):
        self.study_level_start_index = study_level_start_index

    def update_study_level_end_index(self, study_level_end_index: int):
        self.study_level_end_index = study_level_end_index

    # @staticmethod
    # def decode_auth_token(auth_token):
    #     """
    #     Validates the auth token
    #     :param auth_token:
    #     :return: integer|string
    #     """
    #     try:
    #         payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
    #         is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
    #         if is_blacklisted_token:
    #             return 'Token blacklisted. Please log in again.'
    #         else:
    #             return payload['sub']
    #     except jwt.ExpiredSignatureError:
    #         return 'Signature expired. Please log in again.'
    #     except jwt.InvalidTokenError:
    #         return 'Invalid token. Please log in again.'


class UserStudyPhaseEnum(enum.Enum):
    """Indicates the user's study phase as an enum"""

    REGISTERED = 1
    STARTED = 2
    COMPLETED = 3


class UserStatus(db.Model):
    """User Status Model for storing user status related details"""

    __tablename__ = "user_status"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    study_phase = db.Column(db.Enum(UserStudyPhaseEnum), nullable=False)
    study_day = db.Column(db.Integer, nullable=False)
    morning_notification_time_start = db.Column(db.Integer, nullable=True)
    evening_notification_time_start = db.Column(db.Integer, nullable=True)

    def __init__(
        self,
        id: int,
        study_phase: UserStudyPhaseEnum,
        study_day: int,
        morning_notification_time_start: int,
        evening_notification_time_start: int,
    ):
        self.id = id
        self.study_phase = study_phase
        self.study_day = study_day
        self.morning_notification_time_start = morning_notification_time_start
        self.evening_notification_time_start = evening_notification_time_start


class AlgorithmStatus(db.Model):
    """Algorithm status Model for storing algorithm status related details"""

    __tablename__ = "algorithm_status"

    policy_id = db.Column(db.Integer, primary_key=True, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)
    update_day_in_study = db.Column(db.Integer, nullable=False)
    current_decision_time = db.Column(db.Integer, nullable=False)
    current_day_in_study = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        policy_id: int,
        update_time: datetime.datetime,
        update_day_in_study: int,
        current_decision_time: int,
        current_day_in_study: int,
    ):
        self.policy_id = policy_id
        self.update_time = update_time
        self.update_day_in_study = update_day_in_study
        self.current_decision_time = current_decision_time
        self.current_day_in_study = current_day_in_study


class RLWeights(db.Model):
    """Table to store the RL weights"""

    __tablename__ = "rl_weights"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    update_timestamp = db.Column(db.DateTime, nullable=False)
    posterior_mean_array = db.Column(ARRAY(db.Float), nullable=False)
    posterior_var_array = db.Column(ARRAY(db.Float), nullable=False)
    noise_var = db.Column(db.Float, nullable=False)
    random_eff_cov_array = db.Column(ARRAY(db.Float), nullable=False)
    code_commit_id = db.Column(
        db.String, nullable=False, default=app.config.get("CODE_VERSION")
    )

    def __init__(
        self,
        update_timestamp: datetime.datetime,
        posterior_mean_array: list,
        posterior_var_array: list,
        noise_var: float,
        random_eff_cov_array: list,
        code_commit_id: str = app.config.get("CODE_VERSION"),
    ):
        self.update_timestamp = update_timestamp
        self.posterior_mean_array = posterior_mean_array
        self.posterior_var_array = posterior_var_array
        self.noise_var = noise_var
        self.random_eff_cov_array = random_eff_cov_array
        self.code_commit_id = code_commit_id


class RLActionSelection(db.Model):
    """
    Stores the user data tuple corresponding to the
    action that was executed and the components of the
    reward for that user decision time (imputed afterwards)
    """

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    user_decision_idx = db.Column(db.Integer, primary_key=True, nullable=False)
    morning_notification_time = db.Column(db.Integer, nullable=False)
    evening_notification_time = db.Column(db.Integer, nullable=False)
    day_in_study = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    policy_id = db.Column(
        db.Integer, db.ForeignKey("algorithm_status.policy_id"), nullable=False
    )
    policy_creation_time = db.Column(db.DateTime, nullable=False)
    prior_ema_completion_time = db.Column(db.DateTime, nullable=True)
    decision_timestamp = db.Column(db.DateTime, nullable=True)
    action_selection_timestamp = db.Column(db.DateTime, nullable=True)
    probability_of_selection = db.Column(db.Float, nullable=True)
    state_vector = db.Column(
        ARRAY(db.Float), nullable=True
    )  # TODO: Describe the order here
    reward_component_vector = db.Column(ARRAY(db.Float), nullable=True)
    reward = db.Column(db.Float, nullable=True)
