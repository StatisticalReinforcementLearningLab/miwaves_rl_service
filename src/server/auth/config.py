# src/server/auth/config.py

import os
import configparser

CONFIG_INI = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_INI)

# Get the database user password and the JWT secret key
database_username = config['DATABASE']['POSTGRES_USERNAME']
database_password = config['DATABASE']['POSTGRES_PASSWORD']
secret_key = config['JWT']['SECRET_KEY']

database_name = 'flask_jwt_auth'
postgres_local_base = "postgresql://" + str(database_username) + ":" + str(database_password) + "@localhost/"

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = secret_key
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = secret_key
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name