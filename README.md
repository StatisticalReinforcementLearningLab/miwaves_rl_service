# MiWaves RL Service API

- ```/src/auth```: Stores the authentication scheme for the API
- ```/src/server```: Stores the server related code, which details the app routes for the API
- ```/src/algorithm```: Stores the RL algorithm

# Setup
- Install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- Install postgres. Download latest postgres from this [link](https://www.postgresql.org/download/)
- Set up conda environment using: ```conda env create -f miwaves.yml``` (If you are on Debian, make sure you have ``gcc`` installed, and ``libpq-dev`` installed)
- Make sure to activate the conda environment using ```conda activate miwaves```
- Clone this repository
- Navigate to the repo folder: ```cd miwaves_rl_service```
- Specify the postgres username and password in ```config.ini```. Also configure the backend API_URI there (it currently does not support authentication with token or user/pass, but that will be added once the backend api has been developed). The default backend URI is specified to be of a mock Postman API.
- Then create the data directories using the following commands
  - ```mkdir data```
  - ```mkdir data/dbs```
  - ```mkdir data/backups```
  - ```mkdir data/logs```
- Assuming the location of storing databases to ```data/dbs/```, give access to <postgres> user using the following command:\
```chown postgres:postgres fullpath/data/dbs```
- Then launch postgresql using the following command - ```psql "postgresql://<username>:<password>@localhost"```
- Then create tablespace in postgres using:
```CREATE TABLESPACE miwaves_db LOCATION 'fullpath/data/dbs';```
  Use ```\db+``` to view all tablespaces
- Then create database at the specified database location:\
  ```CREATE DATABASE flask_jwt_auth TABLESPACE miwaves_db;```\
  ```CREATE DATABASE flask_jwt_auth_test TABLESPACE miwaves_db;```\
 Sidenote: Use ```\l+``` to view all databases in all tablespaces. View tables using ```\dt```, and describe tables using ```\d+ <table_name>```
- Exit postgresql using ```\q```. You can later reconnect using ```psql -U <username> -d <database_name>``` if required.
- Set the FLASK_APP environment variable on terminal/bash before running. On Windows, set flask app name as - ```$env:FLASK_APP="src.server"```. On other platforms do - ```export FLASK_APP=src.server```
- Then run the following commands to set up the databases:\
```python manage.py create_db```\
```python manage.py db init```\
```python manage.py db migrate```\
```python manage.py populate_commit_id``` (this is one time unless the code has changed)
- Now finally, run the server using the following command:\
```flask run```

If commands have added users to the database, and you want to reset the database completely (erase it and start afresh), use the following set of commands in order:\
```python manage.py drop_db``` # To drop the entire database USE WITH CAUTION\
```python manage.py db stamp head``` # To reset the database after drop_db\
```python manage.py create_db``` # To create the database again\
```python manage.py db migrate``` # To migrate the database after drop_db\
```python manage.py db upgrade``` # To upgrade the database after drop_db

# Testing
There is a automated testing suite, which simulates the API calls and tests the responses. To run this suite, look under tests, the main file is ```api.py```. Use flask to run it (maybe run it on port 4000 using ```flask run --port 4000```). The tests are not yet using unittest, but will use it in the future. This file mimics backend API, and provides the ```/ema_study``` endpoint for the RL API to get data from.

# API Routes
- ```/auth/register```: Register a new client to call APIs to get action and provide data. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then return the ```auth_token``` which will be used in headers of subsequent RL API calls as a bearer token to authenticate the client. Currently you can only register **one** client.
- ```/auth/login```: Login an existing client to call APIs to get action and provide data. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then return the ```auth_token``` which will be used in headers of subsequent RL API calls as a bearer token to authenticate the client.
- ```/auth/logout```: Logout an existing client. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then the current ```auth_token``` for that particular user's login is blacklisted - the user has to login again to generate a new token.
- ```/register```: Register a new user for the trial. Expects the baseline information of a particular user. The information fields expected (in JSON) is as follows:
  - ```user_id```: The user id of the user (could be the email)
  - ```morning_notification_time_start```: The morning notification start time preference for the user across all 7 days of the week (7 values). It expects a list of **integers** to signify the start time in 24-hour format for each day of the week, starting from Monday. For example, if the user wants to be notified at 8:30 AM on each day, then the value should be ```[830, 830, 830, 830, 830, 830, 830]```
  - ```evening_notification_time_start```: The evening notification start time preference for the user across all 7 days of the week (7 values). It expects a list of **integers** to signify the start time in 24-hour format for each day of the week, starting from Monday. For example, if the user wants to be notified at 8:30 PM on each day, then the value should be ```[2030, 2030, 2030, 2030, 2030, 2030, 2030]```. Note that the evening notification time start should be greater than the morning notification time start for each day of the week.
  - ```consent_start_date```: Start date of user consent. Format is ```YYYY-MM-DD```. This date is defined as the date when the user has finished the onboarding process and has consented to participate in the trial.
  - ```consent_end_date```: End date of user consent. Format is ```YYYY-MM-DD```. This date is defined as the date when the user's consent ends. For MiWaves, it is currently defined as 30 days after the consent start date.
  - ```rl_start_date```: Start date of RL trial. Format is ```YYYY-MM-DD```. This date is defined as the date when the user's interventions are being guided by the RL algorithm. For MiWaves, currently it is same as the consent start date.
  - ```rl_end_date```: End date of RL trial. Format is ```YYYY-MM-DD```. This date is defined as the date when the user's interventions are no longer guided by the RL algorithm. For MiWaves, currently it is same as the consent end date.
- ```/actions```: Gets the action for a particular user, given the ```user_id``` and whether they completed the EMA response. The client will query this at either survey completion or survey window end + 15 minutes (if they do not answer the EMA). The RL Service API shifts this user’s status from REGISTERED to STARTED when the client first queries for action for a particular user. If the query is for the last study decision time point, it changes the user's status to COMPLETED_AWAITING_REVIEW.  Expects the follows fields from the query:
  - ```user_id```: User ID of the user for which action is being requested
  - ```finished_ema```: [true/false] Whether the user finished the EMA survey.
  - ```activity_question_response```: [true/false] or "NA". This is the response to the question - Since the previous decision point, have you thought about or used any suggestion from MiWaves? It will be "NA" if the user did not answer the EMA.
  - ```app_use_flag```: [true/false] This is true when the user used the app outside of the survey for more than 10 seconds since the last decision window outside of the EMA.
  - ```cannabis_use```: List of [Numbers]. In the past 12 hours, which hours did you use any cannabis product? It will be "NA" if the user did not answer the EMA.
  - Returns the following fields:
    - ```status```: [success] (200) or [failure] (401) of action selection. 
    - ```message```: If failure, says that it failed because some error occurred. Rest of the options below are when the action selection succeeds.
    - ```action```: 0 (do not show an intervention) or 1 (show an intervention)
    - ```seed```: [Integer] Seed used to generate the action
    - ```act_prob```: [Float] Action selection probability
    - ```policy_id```: [Integer] ID of the policy
    - ```decision_index```: [Integer] Decision time index for which the action has been generated for the user
    - ```act_gen_timestamp```: [DateTime] Timestamp as to when the action is generated
    - ```rid```: [Integer] Unique identifier for the requested action (only generated if successful)
- ```/end_decision_window```: The client calls this to nudge the RLService to signal the end of a decision window for a given user. This will trigger the RLService to fetch data for all the users for that decision time. It tries to fetch data from ```API_URI + EMA_ENDPOINT``` url (these two are present and configurable in ```config.ini```). Expects the following fields:
  - ```user_id```: User ID of the user for which the decision window has ended.
  - It tries to fetch data from ```API_URI + EMA_ENDPOINT``` url. It sends a [POST] request to that endpoint with the following fields:
    - ```user_id```: User ID of the user for which the decision window has ended.
    - ```start_time```: The start time of the query for all the ema which has been collected for the user.
    - ```end_time```: The end time of the query for all the ema which has been collected for the user.
    - Expects the following return fields from the end point:
      - ```status```: [success] (200) or [failure] (401) of the request
      - ```message```: If 401 ([failure]), then reason for failure.
      - ```ema_data```: Dictionary with key as a unique identifier for each EMA. The value is a dictionary which has the following fields:
        - ```user_id```: User ID of the user.
        - ```finished_ema```: [true/false] whether the user finished the EMA survey.
        - ```activity_question_response```: [true/false/"NA"] Since the last decision point, have you thought about or used any suggestion from MiWaves? It will be "NA" if the user did not answer the EMA.
        - ```app_use_flag```: [true/false] user used the app outside of the survey for more than 10 seconds since the last decision window
        - ```cannabis_use```: List of [Numbers(0/1)] In the past 12 hours, which hours did the user use cannabis?
        - ```action_taken```: What was the action (0 or 1) taken for that decision window?
        - ```seed```: The seed used by the RL to generate the action for that decision window.
        - ```act_prob```: The action selection probability generated by the RL for generating the action (that was used) for that decision window.
        - ```policy_id```: The policy id of the policy used by the RL to generate the action for that decision window.
        - ```decision_index```: [Integer] Decision time index for which the action has been generated for the user. This is returned by the RL API when the action was generated.
        - ```act_gen_timestamp```: [DateTime] Timestamp as to when the action was generated
        - ```rid```: [Integer] The unique ```/action``` response id (returned in that response)
        - ```timestamp_finished_ema```: ```YYYY-MM-DD HH:MM:SS```. This is the timestamp as to when the user finished the survey. “NA” if user did not finish survey
        - ```message_notification_sent_time```: ```YYYY-MM-DD HH:MM:SS```, or “NA” if not shown. This is the time when the push notification about the intervention message that the user is randomized to is shown. Two cases:
          - User fills the survey, and is shown that they have a new intervention message. I want the timestamp of the moment they were shown that they have a MiWaves message.
          - User does not fill the survey, and is shown that they have a new intervention message through a system notification. I want the timestamp as to when that push notification got displayed/sent.
        - ```message_notification_click_time```: ```YYYY-MM-DD HH:MM:SS```, or “NA” if not shown. This is the time when the user actually clicked on the intervention message notification/button.
        - ```morning_notification_time_start```: The morning notification start time preference for the user across all 7 days of the week (7 values). It expects a list of **integers** to signify the start time in 24-hour format for each day of the week, starting from Monday. For example, if the user wants to be notified at 8:30 AM on each day, then the value should be ```[830, 830, 830, 830, 830, 830, 830]```
        - ```evening_notification_time_start```: The evening notification start time preference for the user across all 7 days of the week (7 values). It expects a list of **integers** to signify the start time in 24-hour format for each day of the week, starting from Monday. For example, if the user wants to be notified at 8:30 PM on each day, then the value should be ```[2030, 2030, 2030, 2030, 2030, 2030, 2030]```. Note that the evening notification time start should be greater than the morning notification time start for each day of the week.
