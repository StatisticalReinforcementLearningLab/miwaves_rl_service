# src/tests/test_register_api.py


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

class TestUpdateHyperParamAPI(BaseTestCase):
    
    @mock.patch('src.server.DecisionTimeEndAPI.requests.post')
    def test_update_hyperparams(self, mock_post):
        """ Test for updating hyperparameters """
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
            self.assertTrue(action_data['act_prob'] == 0.4173058709851035)
            self.assertTrue(action_data['action'] in [0, 1])
            self.assertTrue(action_data['decision_index'] == 2)
            self.assertTrue(action_data['policy_id'] == 0)
            self.assertTrue(action_data['rid'] == 2)
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

            response = self.client.post(
                '/update_hyperparameters',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                content_type='application/json'
            )

            print(response)

            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Scheduled update of hyperparameters')

            response = self.client.post(
                '/update_parameters',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                content_type='application/json'
            )

            print(response)

            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully updated parameters/posteriors.')
