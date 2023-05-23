mkdir data
mkdir data/dbs

# Location of storing databases, give access to <postgres> user
chown postgres:postgres fullpath/data/dbs

# Launch postgresql
psql "postgresql://<username>:<password>@localhost"

# Create tablespace
CREATE TABLESPACE miwaves_db LOCATION 'fullpath/data/dbs'

# Create database at the specific location
CREATE DATABASE flask_jwt_auth TABLESPACE miwaves_db;
CREATE DATABASE flask_jwt_auth_test TABLESPACE miwaves_db
