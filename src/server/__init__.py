# src/server/__init__.py

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'src.server.auth.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)

from src.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)

from src.server.main import rlservice_blueprint
app.register_blueprint(rlservice_blueprint)