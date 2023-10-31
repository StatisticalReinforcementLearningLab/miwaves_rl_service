# src/server/config.py

import os
import configparser
import numpy as np
import scipy.linalg as linalg
import json

from src.algorithm import mixed_effects, smooth_allocation

CONFIG_INI = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_INI)

# Get the database user password and the JWT secret key
database_username = config["DATABASE"]["POSTGRES_USERNAME"]
database_password = config["DATABASE"]["POSTGRES_PASSWORD"]
secret_key = config["JWT"]["SECRET_KEY"]
code_version = config["GIT"]["COMMIT_ID"]
backend_host = config["BACKEND"]["API_URI"]
backend_auth_token = config["BACKEND"]["API_TOKEN"]
ema_route = config["BACKEND"]["EMA_ENDPOINT"]
action_route = config["BACKEND"]["ACTION_ENDPOINT"]
study_length = config["ALGORITHM"]["STUDY_LENGTH"]
engagement_backlog = config["ALGORITHM"]["ENGAGEMENT_DATA_WINDOW"]
cannabis_use_backlog = config["ALGORITHM"]["CANNABIS_USE_DATA_WINDOW"]
seed = config["ALGORITHM"]["SEED"]

baseline_prior_mean = np.array(json.loads(config["PRIOR"]["BASELINE_PRIOR_MEAN"]))
baseline_prior_var = np.diag(json.loads(config["PRIOR"]["BASELINE_PRIOR_VAR"]))
advantage_prior_mean = np.array(json.loads(config["PRIOR"]["ADVANTAGE_PRIOR_MEAN"]))
advantage_prior_var = np.diag(json.loads(config["PRIOR"]["ADVANTAGE_PRIOR_VAR"]))
init_noise_var = float(config["PRIOR"]["INIT_NOISE_VAR"])
init_sigma_u_var = float(config["PRIOR"]["INIT_SIGMA_U_VAR"])

L_MIN = config["ALLOCATION_FUNCTION"]["L_MIN"]
L_MAX = config["ALLOCATION_FUNCTION"]["L_MAX"]
LOGISTIC_B = config["ALLOCATION_FUNCTION"]["LOGISTIC_B"]
LOGISTIC_C = config["ALLOCATION_FUNCTION"]["LOGISTIC_C"]
LOGISTIC_SIGMA = config["ALLOCATION_FUNCTION"]["LOGISTIC_SIGMA"]

B = float(LOGISTIC_B) / float(LOGISTIC_SIGMA)

# Load the random variables
random_vars_path = config["ALLOCATION_FUNCTION"]["RANDOM_VARS_PATH"]
random_vars = smooth_allocation.load_random_vars(random_vars_path)
allocation_function = smooth_allocation.get_allocation_function(
    func_type="smooth",
    B=float(B),
    randomvars=random_vars,
    C=float(LOGISTIC_C),
    L_min=float(L_MIN),
    L_max=float(L_MAX),
)

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}
headers["Authorization"] = "Bearer " + backend_auth_token

database_name = "flask_jwt_auth"
postgres_local_base = (
    "postgresql://"
    + str(database_username)
    + ":"
    + str(database_password)
    + "@localhost/"
)
backend_api = backend_host
ema_api = backend_api + ema_route
action_api = backend_api + action_route

PRIOR_MEAN = np.hstack(
    (baseline_prior_mean, advantage_prior_mean, advantage_prior_mean)
)
PRIOR_VAR = linalg.block_diag(
    baseline_prior_var, advantage_prior_var, advantage_prior_var
)

INIT_SIGMA_U = np.diag([float(init_sigma_u_var) for i in range(len(PRIOR_MEAN))])


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = secret_key
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CODE_VERSION = code_version
    # ALGORITHM = flat_prob.FlatProbabilityAlgorithm()
    ALGORITHM = mixed_effects.MixedEffectsAlgorithm(
        num_days=study_length,
        prior_mean=PRIOR_MEAN,
        prior_cov=PRIOR_VAR,
        init_cov_u=INIT_SIGMA_U,
        init_noise_var=init_noise_var,
        alloc_func=allocation_function,
        rng=np.random.default_rng(int(seed)),
        debug=True,
        logger_path="./data/logs",
    )
    BACKEND_API = backend_api
    EMA_API = ema_api
    ACTION_API = action_api
    STUDY_LENGTH = int(study_length)
    ENGAGEMENT_DATA_WINDOW = int(engagement_backlog)
    CANNABIS_USE_DATA_WINDOW = int(cannabis_use_backlog)
    STUDY_INDEX = 0
    HEADERS = headers


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name


class TestingConfig(BaseConfig):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + "_test"
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SECRET_KEY = secret_key
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name
