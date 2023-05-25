# First install postgresql

# Then create the following directories
mkdir data
mkdir data/dbs
mkdir data/backups
mkdir data/logs

# Location of storing databases, give access to <postgres> user
chown postgres:postgres fullpath/data/dbs

# Launch postgresql
psql "postgresql://<username>:<password>@localhost"

# Create tablespace
CREATE TABLESPACE miwaves_db LOCATION 'fullpath/data/dbs';

# Create database at the specific location
CREATE DATABASE flask_jwt_auth TABLESPACE miwaves_db;
CREATE DATABASE flask_jwt_auth_test TABLESPACE miwaves_db;

# On windows, set flask app name as - $env:FLASK_APP="src.server"
# Otherwise do - export FLASK_APP=src.server

python manage.py create_db
python manage.py db init
python manage.py db migrate
python manage.py populate_commit_id  # only required one time unless code has changed

# To run the server
# python manage.py runserver
flask run