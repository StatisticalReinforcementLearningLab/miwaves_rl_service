# src/tests/test_decision_time_end_api.py


import time
import json
import unittest

from unittest import mock

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

class TestDecisionTimeEndAPI(BaseTestCase):
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'success')
            self.assertTrue(action_data['message'] == 'Successfully updated decision time index.')
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_userid(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            print(action_data)
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid user id.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_finishedema(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid finished ema.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_appuse(self, mock_post):
        """ Test for decision time end for a given user with missing response from server """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid app use flag.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_activity_question_response(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": True,
                        "app_use_flag": True,
                        "cannabis_use": [0, 0, 0, 0, 0, 0, 0],
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid activity question response.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_cannabis_use(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.420427761193874)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": True,
                        "activity_question_response": False,
                        "app_use_flag": True,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid cannabis use.')
        
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_cannabis_use2(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.420427761193874)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": True,
                        "activity_question_response": False,
                        "app_use_flag": True,
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid cannabis use.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_action_taken(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please provide a valid action taken.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_seed(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the seed used for the action selection.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_seed2(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": 9.52,
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the seed used for the action selection.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_act_prob(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the probability of action taken.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_policyid(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the policy id.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_decision_index(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the decision index.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_act_gen_timestamp(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the action generation timestamp.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_rid(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": 1.5,
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the action request id.')
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_rid2(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the action request id.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_timestamp_finished_ema(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the timestamp when the ema was completed.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_message_notification_sent_time(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the time when the message notifications sent')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_message_notification_click_time(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the time when the message notification was clicked')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_morning_notification_time_start(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the morning notification time start.')

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_missingfields_evening_notification_time_start(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'Please specify the evening notification time start.')


    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_multiema_response(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    },
                    "DW2": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": action_data['rid'],
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'More than one decision point returned by the backend api.')
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_empty_emadata_response(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                }
            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'No data returned from the backend api.')
    

    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_missing_userid(self, mock_post):
        """ Test for decision time end with missing user id """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'User does not exist.')
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_for_user_notstarted_trial(self, mock_post):
        """ Test for decision time end with missing user id """
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
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'User study phase has not started.')


    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_failed_response(self, mock_post):
        """ Test for decision time end for a given user """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "fail",
                "message": "Failed by design"
            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            print(action_data)
            self.assertTrue(action_data['message'] == 'Failed by design')
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_decision_time_end_response_invalid_rid(self, mock_post):
        """ Test for decision time end for a given user with invalid rid """
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
            self.assertTrue(action_data['act_prob'] == 0.38976884669491546)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 1)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 1)
            self.assertTrue(action_data['seed'])


            # Put the action data in a mock request
            mock_response = mock.Mock(status_code=200)
            mock_response.json.return_value = {
                "status": "success",
                "ema_data": {
                    "DW1": {
                        "user_id": userid,
                        "finished_ema": False,
                        "activity_question_response": "NA",
                        "app_use_flag": False,
                        "cannabis_use": "NA",
                        "action_taken": action_data['action'],
                        "seed": action_data['seed'],
                        "act_prob": action_data['act_prob'],
                        "policy_id": action_data['policy_id'],
                        "decision_index": action_data['decision_index'],
                        "act_gen_timestamp": action_data['act_gen_timestamp'],
                        "rid": 10,
                        "timestamp_finished_ema": action_data['act_gen_timestamp'],
                        "message_notification_sent_time": action_data['act_gen_timestamp'],
                        "message_notification_click_time": action_data['act_gen_timestamp'],
                        "morning_notification_time_start": [8, 8, 8, 8, 8, 8, 8],
                        "evening_notification_time_start": [20, 20, 20, 20, 20, 20, 20]
                    }
                }

            }

            mock_post.return_value = mock_response

            response = self.client.post(
                '/end_decision_window',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=userid,
                )),
                content_type='application/json'
            )

            action_data = json.loads(response.data.decode())
            self.assertTrue(action_data['status'] == 'fail')
            self.assertTrue(action_data['message'] == 'No action found for the given rid. Please try again.')