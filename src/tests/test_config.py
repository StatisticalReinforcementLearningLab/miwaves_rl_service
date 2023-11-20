import configparser
import os

from src.server import app
from flask import current_app
from flask_testing import TestCase

CONFIG_INI = "config.ini"

class TestDevelopmentConfig(TestCase):
    """Test development configuration."""
    def create_app(self):
        app.config.from_object('src.server.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_INI)

        # Get the database secret key
        database_secret_key = config['DATABASE']['POSTGRES_PASSWORD']
        
        self.assertTrue(app.config['DEBUG'])
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:' + str(database_secret_key) + '@localhost/flask_jwt_auth'
        )

class TestTestingConfig(TestCase):
    """Test testing configuration."""
    def create_app(self):
        app.config.from_object('src.server.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_INI)

        # Get the database secret key
        database_secret_key = config['DATABASE']['POSTGRES_PASSWORD']
        
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:' + str(database_secret_key) + '@localhost/flask_jwt_auth_test'
        )