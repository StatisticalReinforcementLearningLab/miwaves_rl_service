# src/tests/test_register_api.py


import time
import json
import unittest

from src.server import db
from src.server.auth.models import Client, BlacklistToken
from src.tests.base import BaseTestCase

def register_client(self, username, password):
    return self.client.post(
        '/auth/register',
        data=json.dumps(dict(
            api_user=username,
            api_pass=password
        )),
        content_type='application/json',
    )

class TestActionsAPI(BaseTestCase):
    
    def test_request_action(self):
        """ Test for requesting action for a user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=False,
                    activity_question_response="NA",
                    app_use_flag=False,
                    cannabis_use="NA"
                )),
                content_type='application/json'
            )
            action_data = json.loads(response.data.decode())
            print(action_data)
            self.assertTrue(action_data['status'] == 'success')
            self.assertTrue(action_data['act_gen_timestamp'] is not None)
            self.assertTrue(action_data['act_prob'] >= 0.2 and action_data['act_prob'] <= 0.8)
            self.assertTrue(action_data['act_prob'] - 0.38976884669491546 < 1e-5)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])
    
    def test_request_action_2(self):
        """ Test for requesting action for a user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=False,
                    activity_question_response="NA",
                    app_use_flag=True,
                    cannabis_use="NA"
                )),
                content_type='application/json'
            )
            action_data = json.loads(response.data.decode())
            print(action_data)
            self.assertTrue(action_data['status'] == 'success')
            self.assertTrue(action_data['act_gen_timestamp'] is not None)
            self.assertTrue(action_data['act_prob'] >= 0.2 and action_data['act_prob'] <= 0.8)
            self.assertTrue(action_data['act_prob'] - 0.38976884669491546 < 1e-5)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])
    
    def test_request_action_3(self):
        """ Test for requesting action for a user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    activity_question_response=False,
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            action_data = json.loads(response.data.decode())
            print(action_data)
            self.assertTrue(action_data['status'] == 'success')
            self.assertTrue(action_data['act_gen_timestamp'] is not None)
            self.assertTrue(action_data['act_prob'] >= 0.2 and action_data['act_prob'] <= 0.8)
            self.assertTrue(action_data['act_prob'] - 0.420427761193874 < 1e-5)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])
    
    def test_request_action_4(self):
        """ Test for requesting action for a user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    activity_question_response=False,
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 0]
                )),
                content_type='application/json'
            )
            action_data = json.loads(response.data.decode())
            print(action_data)
            self.assertTrue(action_data['status'] == 'success')
            self.assertTrue(action_data['act_gen_timestamp'] is not None)
            self.assertTrue(action_data['act_prob'] >= 0.2 and action_data['act_prob'] <= 0.8)
            self.assertTrue(action_data['act_prob'] - 0.4350909065012242 < 1e-5)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])
    
    def test_request_action_nonregistered_user(self):
        """ Test for requesting action for user who has not been registered """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    activity_question_response="NA",
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User {} does not exist.'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)
    
    def test_getaction_missing_fields_userid(self):
        """ Test for missing fields in getaction for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    finished_ema=True,
                    activity_question_response="NA",
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User None does not exist.')
    
    def test_getaction_missing_fields_finishedema(self):
        """ Test for missing fields in getaction for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    activity_question_response="NA",
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid finished ema.')
    
    def test_getaction_missing_fields_activityquestion(self):
        """ Test for missing fields in activityquestion for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    app_use_flag=True,
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid activity question response.')
    
    def test_getaction_missing_fields_activityquestion_cbuse_noema(self):
        """ Test for missing fields in activityquestion and cannabis use for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=False,
                    app_use_flag=True,
                    cannabis_use="NA"
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['act_gen_timestamp'] is not None)
            self.assertTrue(data['act_prob'] >= 0.2 and data['act_prob'] <= 0.8)
            self.assertTrue(data['act_prob'] == 0.38976884669491546)
            self.assertTrue(data['action'] in [0, 1])
            self.assertTrue(data['decision_index'] == 1)
            self.assertTrue(data['policy_id'] == 0)
            self.assertTrue(data['rid'] == 1)
            self.assertTrue(data['seed'])
    
    def test_getaction_missing_fields_appuseflag(self):
        """ Test for missing fields in appuseflag for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    activity_question_response="NA",
                    cannabis_use=[0, 0, 0, 0, 0, 0, 1]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid app use flag.')
    
    def test_getaction_missing_fields_cannabisuse(self):
        """ Test for missing fields in cannabisuse for user """
        with self.client:
            response_client = register_client(self, 'joe@gmail.com', '123456')
            data_register = json.loads(response_client.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(response_client.content_type == 'application/json')
            self.assertEqual(response_client.status_code, 201)

            token = data_register['auth_token']
            userid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    rl_start_date='2021-01-01',
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User {} was added!'.format(userid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

            userid = 'test@miwaves.app'
            response = self.client.post(
                '/actions',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                    finished_ema=True,
                    activity_question_response=False,
                    app_use_flag=True,
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid cannabis use.')
    
    # TODO: Add test for 60 decision points (so need to invoke end decision time index)