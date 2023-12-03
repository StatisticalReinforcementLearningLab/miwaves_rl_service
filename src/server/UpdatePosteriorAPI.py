import datetime
import os

import pandas as pd
from src.server import db, app
from src.server.auth.auth import token_required
from src.server.tables import RLActionSelection, RLWeights
from src.server.helpers import return_fail_response


from flask import jsonify, make_response, request
from flask.views import MethodView

import traceback
import csv


class UpdatePosteriorAPI(MethodView):
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

            if not status:
                return return_fail_response(message, 500, ec)

            # Get all the data from the RLActionSelection table
            rl_action_selection = db.session.query(RLActionSelection)

            # Convert to pandas dataframe
            data = pd.read_sql(
                str(rl_action_selection.statement), db.engine.connect().connection
            )

            # Get the algorithm
            algorithm = app.config.get("ALGORITHM")

            # Send the data to the rl algorithm update
            status, message, policyid, params, ec, user_list, hp_update_id = algorithm.update(data,
                                                                     update_posterior=True,
                                                                     update_hyperparam=False,
                                                                     use_data=False)

            if not status:
                # TODO: put this in logger
                return return_fail_response(message, 500, ec)
            
            app.logger.info("Updated posterior")
            app.logger.info("policyid: " + str(policyid))
            app.logger.info("params: " + str(params))

            # Create a RLWeights object
            rl_weights = RLWeights(
                policy_id=policyid,
                update_timestamp=timenow,
                posterior_mean_array=params.get("posterior_mean_array"),
                posterior_var_array=params.get("posterior_var_array"),
                posterior_theta_pop_mean_array=params.get(
                    "posterior_theta_pop_mean_array"
                ),
                posterior_theta_pop_var_array=params.get(
                    "posterior_theta_pop_var_array"
                ),
                noise_var=params.get("noise_var"),
                random_eff_cov_array=params.get("random_eff_cov_array"),
                data_pickle_file_path=location,
                user_list=user_list,
                hp_update_id=hp_update_id,
            )

            # Add the rl_weights object to the database
            try:
                db.session.add(rl_weights)
                db.session.commit()
            except Exception as e:
                app.logger.error("Error adding rl_weights to internal database: %s", e)
                app.logger.error(traceback.format_exc())
                if app.config.get("DEBUG"):
                    print(e)
                    traceback.print_exc()
                db.session.rollback()
                return return_fail_response(
                    "Some error occurred. Please try again.", 500, 401
                )
            else:
                if app.config.get("DEBUG"):
                    print("DB Committed new rl_weights")
                app.logger.info("DB Committed new rl_weights")

                responseObject = {
                    "status": "success",
                    "message": "Successfully updated parameters/posteriors.",
                    "policyid": policyid,
                }

                return make_response(jsonify(responseObject)), 201

        except Exception as e:
            app.logger.error("Error updating hyper-parameters: %s", e)
            app.logger.error(traceback.format_exc())
            if app.config.get("DEBUG"):
                print(e)
                traceback.print_exc()
            return return_fail_response("Some error occurred. Please try again.", 500, 402)
