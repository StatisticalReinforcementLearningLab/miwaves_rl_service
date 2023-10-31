# src/server/main.py

# Server code that hosts the main RL API

from src.server.ActionsAPI import ActionsAPI
from src.server.DecisionTimeEndAPI import DecisionTimeEndAPI
from src.server.RegisterAPI import RegisterAPI
from src.server.UpdatePosteriorAPI import UpdatePosteriorAPI
from src.server.UpdateHyperParamAPI import UpdateHyperParamAPI
# from src.server.UpdateNotificationTimeAPI import UpdateNotificationTimeAPI


from flask import Blueprint

from src.server.auth.models import Client
from src.server.tables import (
    AlgorithmStatus,
)

rlservice_blueprint = Blueprint("rlservice", __name__)


# define the API resources
registration_view = RegisterAPI.as_view("user_register_api")
action_selection_view = ActionsAPI.as_view("user_actions_api")
decision_time_end_view = DecisionTimeEndAPI.as_view("decision_time_end_api")
update_posterior_view = UpdatePosteriorAPI.as_view("update_model_api")
update_hyperparameters_view = UpdateHyperParamAPI.as_view("update_hyperparam_api")
# update_notification_time_view = UpdateNotificationTimeAPI.as_view(
#     "update_notification_time_api"
# )

# add Rules for API Endpoints
rlservice_blueprint.add_url_rule(
    "/register", view_func=registration_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/actions", view_func=action_selection_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/end_decision_window", view_func=decision_time_end_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/update_parameters", view_func=update_posterior_view, methods=["POST"]
)
rlservice_blueprint.add_url_rule(
    "/update_hyperparameters", view_func=update_hyperparameters_view, methods=["POST"]
)

# rlservice_blueprint.add_url_rule(
#     "/notif_time_change",
#     view_func=update_notification_time_view,
#     methods=["POST"],
# )
