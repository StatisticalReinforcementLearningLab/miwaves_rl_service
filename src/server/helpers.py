# src/sever/helpers.py

import csv
import datetime

from flask import jsonify, make_response

from src.server import db


def export_table(tablename: db.Model, backup_id: int, time: datetime.datetime = None):
    """Exports the table to a csv file, in a folder inside data/backups/"""
    # If time is None, use current time
    if time is None:
        time = datetime.datetime.now()

    # Create filename
    filename = f"{tablename.__tablename__}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # Create file and write to it
    with open(f"data/backups/{backup_id}/{filename}", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([c.name for c in tablename.__table__.columns])
        for row in tablename.query.all():
            writer.writerow([getattr(row, c.name) for c in tablename.__table__.columns])


def export_all_tables(backup_id: int, time: datetime.datetime = None):
    """Exports all tables to csv files, in a folder inside data/backups/"""
    # If time is None, use current time
    if time is None:
        time = datetime.datetime.now()

    # Loop over all tables and export them
    for tablename in db.Model._decl_class_registry.values():
        if hasattr(tablename, "__tablename__"):
            export_table(tablename, backup_id, time)


def return_fail_response(message: str, code: int, error_code: int = None):
    """Returns a response object with the given status, message, and code"""
    if error_code is not None:
        return make_response(
            jsonify(
                {
                    "status": "fail",
                    "message": message,
                    "error_code": error_code,
                }
            )
        ), code
    else:
        return make_response(jsonify({"status": "fail", "message": message})), code
