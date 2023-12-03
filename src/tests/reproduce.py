from sqlalchemy import create_engine, MetaData, Table
import configparser

from src.algorithm import mixed_effects
from src.server.config import ProductionConfig, allocation_function
from src.server.ActionsAPI import ActionsAPI
import pandas as pd
import numpy as np

postgres_local_base = ProductionConfig.SQLALCHEMY_DATABASE_URI

engine = create_engine(postgres_local_base)
meta = MetaData()
meta.reflect(bind=engine)

table_names = meta.tables.keys()
tables = {}
table_columns = {}
num_params = 24

# print(meta.tables.keys())

# Create a connection object
connection = engine.connect()

# Fetch data for all the tables, and store them in a dictionary as pandas dataframes
for table_name in table_names:
    # table = Table(table_name, meta, autoload=True, autoload_with=engine)
    # tables[table_name] = connection.execute(table.select()).fetchall()
    # table_columns[table_name] = table.columns.keys()
    df = pd.read_sql_table(table_name, connection)
    tables[table_name] = df
    table_columns[table_name] = df.columns.values.tolist()

    # print(df)

# Close the connection
connection.close()



# For each row, check if the generated reward is the same as the one in the database
user_action = tables["user_action_history"]
user_action_cols = table_columns["user_action_history"]
print(user_action_cols)

action_history = tables["rl_action_selection"]
action_history_cols = table_columns["rl_action_selection"]
print(action_history_cols)

policy_table = tables["rl_weights"]
policy_table_cols = table_columns["rl_weights"]
print(policy_table_cols)


alg = ProductionConfig.ALGORITHM

# Iterate over each row in rl_action_selection, and check the reward
for idx, row in action_history.iterrows():
    # print(row[action_history_cols.index("rid")])
    user_id = row["user_id"]
    rid = row["rid"]
    decision_idx = row["user_decision_idx"]
    
    # Find the row in the table rl_action_selection that corresponds to this rid
    result = user_action[user_action["index"] == rid]

    user_id = result["user_id"].values[0]
    finished_ema = result["finished_ema"].values[0]
    app_use_flag = result["app_use_flag"].values[0]
    activity_question_response = result["activity_question_response"].values[0]
    if activity_question_response == "true":
        activity_question_response = True
    elif activity_question_response == "false":
        activity_question_response = False
    else:
        pass
    recent_cannabis_use = result["cannabis_use"].values[0]

    if recent_cannabis_use == {}:
        recent_cannabis_use = 0

    reward_data = ActionsAPI.get_raw_reward_data({
        "user_id": user_id,
        "finished_ema": finished_ema,
        "app_use_flag": app_use_flag,
        "activity_question_response": activity_question_response,
        "cannabis_use": recent_cannabis_use,
    })

    reward = alg.make_reward(reward_data)

    assert row["reward"] == result["reward"].values[0] == reward

    # Get the past 3 rewards from the decision_idx in the user_action_history table
    engagement_data = action_history[(action_history["user_decision_idx"] > decision_idx - ProductionConfig.ENGAGEMENT_DATA_WINDOW) & (action_history["user_decision_idx"] < decision_idx) & (action_history["user_id"] == user_id)]["reward"].values.tolist()

    raw_state_data = {
        "engagement_data": engagement_data,
        "cannabis_use_data": [],
        "recent_cannabis_use": recent_cannabis_use,
        "time_of_day": ((decision_idx - 1) % 2),
        "reward": reward,
    }
    # print(decision_idx, user_id, engagement_data)

    state = alg.make_state(raw_state_data)

    # print(decision_idx, user_id, recent_cannabis_use, state, result["state"].values[0], row["state_vector"])
    # print(engagement_data)

    assert row["state_vector"] == result["state"].values[0] == state

    policy_id = row["policy_id"]

    if policy_id == 0:
        post_mean_user = np.array(alg.prior_mean)
        post_var_user = np.array(alg.prior_cov)
        theta_mean = np.array(alg.prior_mean)
        theta_var = np.array(alg.prior_cov)
        sigma_u = np.array(alg.sigma_u)
    else:
        post_mean = np.array(policy_table[(policy_table["policy_id"] == policy_id)]["posterior_mean_array"].values[0]).reshape(-1, num_params)
        n = post_mean.shape[0]
        post_var = np.array(policy_table[(policy_table["policy_id"] == policy_id)]["posterior_var_array"].values[0]).reshape(num_params * n, num_params * n)
        theta_mean = np.array(policy_table[(policy_table["policy_id"] == policy_id)]["posterior_theta_pop_mean_array"].values[0])
        theta_var = np.array(policy_table[(policy_table["policy_id"] == policy_id)]["posterior_theta_pop_var_array"].values[0])
        user_list = policy_table[(policy_table["policy_id"] == policy_id)]["user_list"].values[0]
        sigma_u = np.array(policy_table[(policy_table["policy_id"] == policy_id)]["random_eff_cov_array"].values[0])
    
    if decision_idx < 3:
        post_mean_user = theta_mean
        post_var_user = theta_var + sigma_u
    else:
        user_index = user_list.index(user_id)
        post_mean_user = post_mean[user_index]
        post_var_user = post_var[user_index * num_params: (user_index + 1) * num_params, user_index * num_params: (user_index + 1) * num_params]

    advantage_default = [
            1,
            state[0],
            state[1],
            state[2],
            state[0] * state[1],
            state[0] * state[2],
            state[1] * state[2],
            state[0] * state[1] * state[2],
        ]

    advantage_with_intercept = np.array(advantage_default)

    beta_mean = np.array(post_mean_user[-8:])

    # Compute the posterior covariance of the adv term
    beta_cov = np.array(post_var_user[-8:, -8:])

    # Compute the posterior mean of the adv*beta distribution
    adv_beta_mean = advantage_with_intercept.T.dot(beta_mean)

    # Compute the posterior variance of the adv*beta distribution
    adv_beta_var = advantage_with_intercept.T @ beta_cov @ advantage_with_intercept

    # Call the allocation function
    prob = allocation_function(mean=adv_beta_mean, var=adv_beta_var)

    print(user_id, decision_idx)

    assert prob == row["act_prob"]

    seed = int(row["seed"])

    rng = np.random.default_rng(seed=seed)
    action = rng.binomial(1, prob)

    assert action == int(row["action"])
