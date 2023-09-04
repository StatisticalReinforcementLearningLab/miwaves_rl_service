# src/server/config.py

import os
import configparser

from src.algorithm import flat_prob

CONFIG_INI = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_INI)

# Get the database user password and the JWT secret key
database_username = config["DATABASE"]["POSTGRES_USERNAME"]
database_password = config["DATABASE"]["POSTGRES_PASSWORD"]
secret_key = config["JWT"]["SECRET_KEY"]
code_version = config["GIT"]["COMMIT_ID"]
backend_host = config["BACKEND"]["API_URI"]
ema_route = config["BACKEND"]["EMA_ENDPOINT"]
action_route = config["BACKEND"]["ACTION_ENDPOINT"]
study_length = config["STUDY"]["STUDY_LENGTH"]
engagement_backlog = config["STUDY"]["ENGAGEMENT_DATA_WINDOW"]
cannabis_use_backlog = config["STUDY"]["CANNABIS_USE_DATA_WINDOW"]
engagement_threshold = config["STUDY"]["ENGAGEMENT_THRESHOLD"]
cannabis_use_threshold = config["STUDY"]["CANNABIS_USE_THRESHOLD"]

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


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = secret_key
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CODE_VERSION = code_version
    ALGORITHM = flat_prob.FlatProbabilityAlgorithm()
    BACKEND_API = backend_api
    EMA_API = ema_api
    ACTION_API = action_api
    STUDY_LENGTH = int(study_length)
    ENGAGEMENT_DATA_WINDOW = int(engagement_backlog)
    CANNABIS_USE_DATA_WINDOW = int(cannabis_use_backlog)
    ENGAGEMENT_THRESHOLD = float(engagement_threshold)
    CANNABIS_USE_THRESHOLD = float(cannabis_use_threshold)
    STUDY_INDEX = 0


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
