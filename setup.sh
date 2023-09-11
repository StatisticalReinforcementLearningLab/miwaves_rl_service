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
# \db+ to view all tablespaces

# Create database at the specific location
CREATE DATABASE flask_jwt_auth TABLESPACE miwaves_db;
CREATE DATABASE flask_jwt_auth_test TABLESPACE miwaves_db;
#\l+ to view all databases in all tablespaces
# Later connect to see using psql -U <username> -d <database_name>
# and then view tables using \dt, and describe table using \d+ <table_name>

# Exit postgresql using \q

# On windows, set flask app name as - $env:FLASK_APP="src.server"
# Otherwise do - export FLASK_APP=src.server

python manage.py create_db
python manage.py db init
python manage.py db migrate
python manage.py populate_commit_id  # only required one time unless code has changed
# python manage.py drop_db # To drop the entire database USE WITH CAUTION
# python manage.py db stamp head # To reset the database after drop_db
# python manage.py db migrate # To migrate the database after drop_db
# python manage.py db upgrade # To upgrade the database after drop_db

# Export the FLASK_APP environment variable

# To run the server
# python manage.py runserver
flask run