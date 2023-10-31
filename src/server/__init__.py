# src/server/__init__.py

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import logging

logging.basicConfig(
    filename="./data/logs/API_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)
app = Flask(__name__)
CORS(app)

app_settings = os.getenv("APP_SETTINGS", "src.server.config.DevelopmentConfig")
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)

from src.server.auth.views import auth_blueprint

app.register_blueprint(auth_blueprint)

from src.server.main import rlservice_blueprint

app.register_blueprint(rlservice_blueprint)

app.logger.info("Server started")