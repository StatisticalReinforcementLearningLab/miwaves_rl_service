# manage.py

import os
import unittest
import coverage
import git

from flask.cli import FlaskGroup


COV = coverage.coverage(
    branch=True,
    include='src/*',
    omit=[
        'src/auth/config.py',
        'src/auth/*/__init__.py'
    ]
)
COV.start()

from src.server.auth import models
from src.server import app, db

cli = FlaskGroup(app)

@cli.command("test")
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('src/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command("cov")
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('src/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@cli.command("create_db")
def create_db():
    """Creates the db tables."""
    db.create_all()


@cli.command("drop_db")
def drop_db():
    """Drops the db tables."""
    db.drop_all()

@cli.command("populate_commit_id")
def populate_commit_id():
    """Populates the COMMIT_ID in config.ini"""
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    with open(config_file, 'r+') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('COMMIT_ID'):
                lines[i] = 'COMMIT_ID=' + sha + '\n'
                break
        f.seek(0)
        f.writelines(lines)
        f.truncate()


if __name__ == '__main__':
    cli()