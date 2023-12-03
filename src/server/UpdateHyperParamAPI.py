import datetime
import os

import pandas as pd
from src.server import db, app
from src.server.auth.auth import token_required
from src.server.tables import RLActionSelection, RLHyperParamUpdateRequest
from src.server.helpers import return_fail_response


from flask import jsonify, make_response, request
from flask.views import MethodView

import threading
import time

import traceback
import csv

# @shared_task(ignore_result=False)
def update_hyperparam_task(id):
    """Background task for updating hyper-parameters"""

    try:

        with app.app_context():
            # Get all the data from the RLActionSelection table
            rl_action_selection = db.session.query(RLActionSelection)

            # Convert to pandas dataframe
            data = pd.read_sql(
                str(rl_action_selection.statement), db.engine.connect().connection
            )

            # Get the algorithm
            algorithm = app.config.get("ALGORITHM")

            status, message, _, _, ec, _, _ = algorithm.update(data,
                                                    update_posterior=False,
                                                    update_hyperparam=True,
                                                    use_data=False,
                                                    request_id=id)
        
            if not status:
                app.logger.error("Error updating hyper-parameters: %s", message)
                app.logger.error(traceback.format_exc())

                # Update the request status to failed
                request = RLHyperParamUpdateRequest.query.filter_by(id=id).first()
                request.request_status = "Failed"
                request.request_message = message
                request.request_error_code = ec
                request.completed_timestamp = datetime.datetime.now()
                db.session.commit()
            else:
                app.logger.info("Updated hyper-parameters")

                # Update the request status to completed
                request = RLHyperParamUpdateRequest.query.filter_by(id=id).first()
                request.request_status = "Completed"
                request.completed_timestamp = datetime.datetime.now()
                db.session.commit()


    except Exception as e:
        app.logger.error("Error updating hyper-parameters: %s", e)
        app.logger.error(traceback.format_exc())
        if app.config.get("DEBUG"):
            print(e)
            traceback.print_exc()
    


class UpdateHyperParamAPI(MethodView):
    """
    Update model weights of the RL algorithm
    """

    def export_table(self, tablename, time) -> None:
        """Exports the table to a csv file, in a folder inside data/backups/"""

        # Create filename
        filename = f"{tablename.__tablename__}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        folder = f"./data/backups/{time.strftime('%Y-%m-%d_%H-%M-%S')}"

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Create file and write to it
        with open(f"{folder}/{filename}", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([c.name for c in tablename.__table__.columns])
            for row in tablename.query.all():
                writer.writerow(
                    [getattr(row, c.name) for c in tablename.__table__.columns]
                )

    def backup_all_tables(self, time: datetime.datetime) -> tuple[bool, str, str, int]:
        """
        Exports all tables to csv files, in a folder
        :return: True if successful, False otherwise
        :return: error message if unsuccessful, None otherwise
        :return: location of the backup
        :return: error code if unsuccessful, None otherwise
        """

        try:
            # Loop over all tables and export them
            for tablename in db.Model.registry._class_registry.values():
                if hasattr(tablename, "__tablename__"):
                    self.export_table(tablename, time)
        except Exception as e:
            app.logger.error("Error backing up tables: ", e)
            if app.config.get("DEBUG"):
                print("Error backing up tables: ", e)

            return False, "Error backing up tables: " + str(e), None, 400

        return True, None, f"./data/backups/{time.strftime('%Y-%m-%d_%H-%M-%S')}", None

    @token_required
    def post(self):
        try:
            timenow = datetime.datetime.now()

            # log the time when the update request was received
            app.logger.info("Update model request received at: %s", timenow)
            if app.config.get("DEBUG"):
                print("Update model request received at: ", timenow)

            # First backup all the tables
            status, message, location, ec = self.backup_all_tables(timenow)

            app.logger.info("Backup status: %s", status)
            app.logger.info("Backup message: %s", message)
            app.logger.info("Backup location: %s", location)

            if not status:
                return return_fail_response(message, 500, ec)

            # Create a new entry in the RLHyperParamUpdateRequest table
            new_request = RLHyperParamUpdateRequest(backup_location=location, 
                                                    request_timestamp=timenow,
                                                    request_status="Pending",
                                                    request_message=None,
                                                    request_error_code=None,
                                                    completed_timestamp=None)

            try:
                db.session.add(new_request)
                db.session.commit()
            except Exception as e:
                app.logger.error("Error adding new request to RLHyperParamUpdateRequest table: %s", e)
                app.logger.error(traceback.format_exc())
                if app.config.get("DEBUG"):
                    print(e)
                    traceback.print_exc()
                return return_fail_response("Some error occurred. Please try again.", 500, 402)
            
            request_id = new_request.id

            # Send the data to the rl algorithm update
            # task_result = update_hyperparam_task.delay()
            bg_task = threading.Thread(target=update_hyperparam_task, args=(request_id,))
            bg_task.daemon = True
            bg_task.start()
            
            # task_result = update_hyperparam_task()

            # if app.config.get("DEBUG"):
            #     print("Scheduled update of hyperparameters: %s", task_result.id)
            # app.logger.info("Scheduled update of hyperparameters: %s", task_result.id)

            responseObject = {
                "status": "success",
                "message": "Scheduled update of hyperparameters",
                # "taskid": task_result.id,
            }

            return make_response(jsonify(responseObject)), 201

        except Exception as e:
            app.logger.error("Error updating hyper-parameters: %s", e)
            app.logger.error(traceback.format_exc())
            if app.config.get("DEBUG"):
                print(e)
                traceback.print_exc()
            return return_fail_response("Some error occurred. Please try again.", 500, 402)
