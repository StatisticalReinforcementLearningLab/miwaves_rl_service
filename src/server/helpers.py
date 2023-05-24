# src/sever/helpers.py

import csv
import datetime

from src.server import db


def export_table(tablename: db.Model, backup_id: int, time: datetime.datetime = None):
    """Exports the table to a csv file, in a folder inside data/backups/"""
    if time is None:
        time = datetime.datetime.now()
    filename = f"{tablename.__tablename__}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with open(f"data/backups/{backup_id}/{filename}", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([c.name for c in tablename.__table__.columns])
        for row in tablename.query.all():
            writer.writerow([getattr(row, c.name) for c in tablename.__table__.columns])
