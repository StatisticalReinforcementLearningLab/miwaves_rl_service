import copy
import time
import flask
import pandas as pd
import numpy as np
import requests
import json
import datetime
import pickle as pkl
from sklearn.linear_model import LogisticRegression

app = flask.Flask(__name__)

user_data = {}
last_decision_point = {}
# full_df = pd.DataFrame()

PATH = "./../data/dataset/combined_data.csv"
USERMODEL_PATH = "./../models/usermodels/MLR.pkl"
SIMULATION_FOLDER = "./../data/simulations/"
RANDOMVARS_PATH = "./../models/randomvars/randomvars.pkl"

base_url = "http://127.0.0.1:5000/"
client_register_url = base_url + "auth/register"
register_url = base_url + "register"
actions_url = base_url + "actions"
windowend_url = base_url + "end_decision_window"
update_post_url = base_url + "update_parameters"
update_hp_url = base_url + "update_hyperparameters"

# auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDY0NzA4MTQsImlhdCI6MTY5ODY5NDgxNCwic3ViIjoxfQ.3XgtFEY7iQa3mTPOXR7taiMvFd2S1KO7o63E3lgOuew"
headers = {
    'Content-type':'application/json', 
    'Accept':'application/json'
}

# Normalization constants

CB_MEAN = 1.3
CB_STD = 1.35

APP_USE_MEAN = 350
APP_USE_STD = 350

DAY_MEAN = 15.5
DAY_STD = 14.5

def format_data_for_prediction(data, action, day, start_day = 0):
    """
    Formats data for prediction
    """
    X = pd.DataFrame(
        data[
            [
                "intercept",
                "engagement",
                "std_app_usage",
                "std_cannabis_use",
                "weekend",
                "std_day",
            ]
        ].astype(float)
    )
    X["weekend"] = 1 if (day + start_day) % 7 >= 5 else 0

    # Add columns to the data
    X["act_engagement"] = action * X["engagement"]
    X["act_std_app_usage"] = action * X["std_app_usage"]
    X["act_std_cannabis_use"] = action * X["std_cannabis_use"]
    X["act_std_day"] = action * X["std_day"]
    X["act_weekend"] = action * X["weekend"]
    X["act_intercept"] = action * X["intercept"]

    # Format data again
    X = X[
        [
            "intercept",
            "engagement",
            "std_app_usage",
            "std_cannabis_use",
            "weekend",
            "std_day",
            "act_intercept",
            "act_engagement",
            "act_std_app_usage",
            "act_std_cannabis_use",
            "act_weekend",
            "act_std_day",
        ]
    ].astype(float)

    return X


def normalize(df):
    df["std_cannabis_use"] = (df["cannabis_use"] - CB_MEAN) / CB_STD
    df["std_app_usage"] = (df["time_spent"] - APP_USE_MEAN) / APP_USE_STD
    df["std_day"] = (df["day"] - DAY_MEAN) / DAY_STD

    df["engagement"] = df["IsSurveyCompleted"].astype(float)
    df["std_day"] = df["std_day"].astype(float)
    df["std_cannabis_use"] = df["std_cannabis_use"].astype(float)
    df["std_app_usage"] = df["std_app_usage"].astype(float)
    df["weekend"] = df["weekend"].astype(float)
    df["intercept"] = 1.0

    return df

def load_data():
    # Load data
    df = pd.read_csv(PATH)

    # Normalize data
    df = normalize(df)

    return df


def load_user_models() -> LogisticRegression:
    # Load user models
    with open(USERMODEL_PATH, "rb") as f:
        user_models = pkl.load(f)

    return user_models

@app.route('/')
def run_simulation():
    num_users = 10
    num_days = 10
    start_users = 4
    rolling_users = 2
    recruitment_interval = 3

    rng = np.random.default_rng(seed=42)

    # Load data
    df = load_data()

    # Load user models
    user_models = load_user_models()

    list_of_users = df["user_id"].unique()

    # Sample NUSERS from list_of_users with replacement
    sampled_users = rng.choice(list_of_users, num_users, replace=True)

    # Calculate additional waves
    additional_waves = int(np.ceil((num_users - start_users) / rolling_users))

    # Calculate number of study level days
    total_days = num_days + additional_waves * recruitment_interval

    # Calculate the study level start and end dates
    user_start_dates = [0] * num_users
    user_end_dates = [num_days] * num_users

    # Calculate study level end dates
    for wave in range(additional_waves):
        for uid in range(rolling_users):
            user_start_dates[start_users + wave * rolling_users + uid] = (
                0 + (wave + 1) * recruitment_interval
            )
            user_end_dates[start_users + wave * rolling_users + uid] = (
                num_days + (wave + 1) * recruitment_interval
            )

    print(sampled_users)

    # First register the client
    payload = {
        "api_user": "backend",
        "api_pass": "testpass",
    }
    data = requests.post(
        client_register_url,
        data=json.dumps(payload),
        headers=headers,
    )

    auth_token = data.json()["auth_token"]
    headers["Authorization"] = "Bearer " + auth_token
    
    # Cycle through all users and register them
    for user in range(len(sampled_users)):
        payload = {
            "user_id": str(user) + "_" + str(sampled_users[user]),
            "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
            "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20],
            "rl_start_date": datetime.datetime(2024, 1, 1).strftime("%Y-%m-%d"),
            "rl_end_date": datetime.datetime(2024, 1, 31).strftime("%Y-%m-%d"),
            "consent_start_date": datetime.datetime(2024, 1, 1).strftime("%Y-%m-%d"),
            "consent_end_date": datetime.datetime(2024, 1, 31).strftime("%Y-%m-%d"),
        }
        print(json.dumps(payload))
        data = requests.post(
            register_url,
            data=json.dumps(payload),
            headers=headers,
        )

        print(data.json())
        # print(payload)

    # return "Simulation complete"

    # Run simulation for total_days, with num_days for each user
    for day in range(total_days):

        # Iterate over morning and evenings
        for time_of_day in range(2):

            # Iterate over all users
            for user in range(len(sampled_users)):

                # Do not loop over users who haven't begun or finished
                if day < user_start_dates[user] or day >= user_end_dates[user]:
                    continue

                user_day = day - user_start_dates[user]

                # Calculate study level decision point index
                study_decision_point = day * 2 + time_of_day + 1

                # Calculate the user decision point index
                user_decision_point = (day - user_start_dates[user]) * 2 + time_of_day + 1

                # Calculate the user id
                user_id = str(user) + "_" + str(sampled_users[user])

                dp_data = pd.DataFrame(
                    df[
                        (df["day"] == user_day + 1)
                        & (df["time_of_day"] == time_of_day)
                        & (df["user_id"] == sampled_users[user])
                    ]
                )

                cannabis_use = [dp_data["cannabis_use"].values[0]]*12


                # If it is the first decision point of the user, figure out the data variables
                if user_decision_point == 1:
                    # Get the initial reward which influences the first state
                    reward = rng.choice([0, 1, 2], p=[0.33, 0.33, 0.34])
                    
                else:
                    last_action = int(user_data[user_id][user_decision_point - 1]["action"])

                    # Format the data for the user model prediction
                    X = format_data_for_prediction(dp_data, last_action, user_day)

                    # Get the user model
                    user_model = user_models[sampled_users[user]]

                    # Predict the reward
                    probabilities = user_model.predict_proba(X)

                    # Sample the reward
                    reward = rng.choice(user_model.classes_, p=probabilities[0])

                
                # Get the initial state of the user
                
                if reward == 3:
                    activity_question = True
                    survey_completion = True
                    app_use_flag = True
                    reported_cannabis_use = copy.deepcopy(cannabis_use)
                elif reward == 2:
                    activity_question = False
                    survey_completion = True
                    app_use_flag = True
                    reported_cannabis_use = copy.deepcopy(cannabis_use)
                elif reward == 1:
                    activity_question = "NA"
                    survey_completion = False
                    app_use_flag = True
                    reported_cannabis_use = "NA"
                else:
                    activity_question = "NA"
                    survey_completion = False
                    app_use_flag = False
                    reported_cannabis_use = "NA"
                
                # Send the ema data to get action for the user
                payload = {
                    "user_id": user_id,
                    "activity_question_response": activity_question,
                    "finished_ema": survey_completion,
                    "app_use_flag": app_use_flag,
                    "cannabis_use": reported_cannabis_use,
                }

                print(json.dumps(payload))

                data = requests.post(
                    actions_url,
                    data=json.dumps(payload),
                    headers=headers,
                ).json()

                print(data)

                # If the status is successful, continue
                if data["status"] == "success":

                    # Get the action from the response
                    action = data["action"]
                    seed = data["seed"]
                    act_prob = data["act_prob"]
                    policy_id = data["policy_id"]
                    decision_idx = data["decision_index"]
                    act_gen_timestamp = data["act_gen_timestamp"]
                    rid = data["rid"]

                    if user_id not in user_data:
                        user_data[user_id] = {}

                    # Save the response data for the user_data
                    user_data[user_id][int(decision_idx)] = {
                        "action": action,
                        "seed": seed,
                        "act_prob": act_prob,
                        "policy_id": policy_id,
                        "decision_idx": decision_idx,
                        "act_gen_timestamp": act_gen_timestamp,
                        "rid": rid,
                        "finished_ema": survey_completion,
                        "activity_question_response": activity_question,
                        "cannabis_use": reported_cannabis_use,
                        "app_use_flag": app_use_flag,
                    }

                    last_decision_point[user_id] = decision_idx
                    
                
                else:
                    print(data["message"])
            
            # Signal that a decision window has ended for each user
            for user in range(len(sampled_users)):

                # Do not loop over users who haven't begun or finished
                if day < user_start_dates[user] or day >= user_end_dates[user]:
                    continue

                user_id = str(user) + "_" + str(sampled_users[user])

                # Calculate the user decision point index
                user_decision_point = (day - user_start_dates[user]) * 2 + time_of_day + 1

                # Calculate study level decision point index
                study_decision_point = day * 2 + time_of_day + 1

                # Send the end of decision window signal
                payload = {
                    "user_id": user_id,
                }

                data = requests.post(
                    windowend_url,
                    data=json.dumps(payload),
                    headers=headers,
                ).json()

                print(data)
                
            # Sleep for 5 seconds
            # time.sleep(5)

        # At the end of 7 days, ask the algorithm to update the hyperparameters
        if day % 7 == 6:
            payload = {}
            data = requests.post(
                update_hp_url,
                data=json.dumps(payload),
                headers=headers,
            ).json()
            print(data)

        # At the end of each day, ask the algorithm to update the parameters
        payload = {}
        data = requests.post(
            update_post_url,
            data=json.dumps(payload),
            headers=headers,
        ).json()
        print(data)

    return "Simulation complete"

@app.route('/ema_study', methods=['POST'])
def ema_study():
    '''
    Serves data for the EMA study
    '''

    # Get post data
    data = flask.request.get_json()

    print("EMA REQUEST: ", data)

    # Get the user id
    user_id = data["user_id"]
    start_time = data["start_time"]
    end_time = data["end_time"]

    # Respond with the latest decision point data
    idx = last_decision_point[user_id]
    payload = {
        "status": "success",
        "ema_data": { idx: {
            "user_id": user_id,
            "finished_ema": user_data[user_id][idx]["finished_ema"],
            "activity_question_response": user_data[user_id][idx]["activity_question_response"],
            "app_use_flag": user_data[user_id][idx]["app_use_flag"],
            "cannabis_use": user_data[user_id][idx]["cannabis_use"],
            "action_taken": user_data[user_id][idx]["action"],
            "seed": user_data[user_id][idx]["seed"],
            "act_prob": user_data[user_id][idx]["act_prob"],
            "policy_id": user_data[user_id][idx]["policy_id"],
            "decision_index": user_data[user_id][idx]["decision_idx"],
            "act_gen_timestamp": user_data[user_id][idx]["act_gen_timestamp"],
            "rid": user_data[user_id][idx]["rid"],
            "timestamp_finished_ema": user_data[user_id][idx]["act_gen_timestamp"],
            "message_notification_sent_time": user_data[user_id][idx]["act_gen_timestamp"],
            "message_notification_click_time": user_data[user_id][idx]["act_gen_timestamp"],
            "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
            "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20],
        }}
    }

    print(payload)

    return flask.jsonify(payload), 200