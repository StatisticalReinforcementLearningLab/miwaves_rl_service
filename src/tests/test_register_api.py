# src/tests/test_register_api.py


import time
import json
import unittest

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

class TestRegisterAPI(BaseTestCase):
    
    def test_user_registration(self):
        """ Test for user registration """
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
    
    def test_user_registration_duplicate(self):
        """ Test for duplicate user registration """
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

            newuserid = 'test@miwaves.app'
            response = self.client.post(
                '/register',
                headers=dict(
                    Authorization='Bearer ' + token
                ),
                data=json.dumps(dict(
                    user_id=newuserid,
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User {} already exists.'.format(newuserid))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)
    
    def test_user_registration_missing_fields_userid(self):
        """ Test for missing fields in user registration """
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid user id.')
    
    def test_user_registration_missing_fields_rlstartdate(self):
        """ Test for missing fields in user registration """
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
                    rl_end_date='2021-01-30',
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid rl start date.')
    
    def test_user_registration_missing_fields_rlenddate(self):
        """ Test for missing fields in user registration """
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
                    consent_start_date='2021-01-01',
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid rl end date.')
    
    def test_user_registration_missing_fields_consentstartdate(self):
        """ Test for missing fields in user registration """
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
                    consent_end_date='2021-01-30',
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid consent start date.')

    def test_user_registration_missing_fields_consentenddate(self):
        """ Test for missing fields in user registration """
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
                    morning_notification_time_start=[8, 8, 8, 8, 8, 8, 8],
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid consent end date.')
    
    def test_user_registration_missing_fields_morning_starttime(self):
        """ Test for missing fields in user registration """
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
                    evening_notification_time_start=[20, 20, 20, 20, 20, 20, 20]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid morning notification time.')
    
    def test_user_registration_missing_fields_evening_starttime(self):
        """ Test for missing fields in user registration """
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
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Please provide a valid evening notification time.')

    def test_user_registration_invalid_starttimes(self):
        """ Test for invalid start times in user registration """
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

            # Test invalid morning start time
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
                    morning_notification_time_start=8.5,
                    evening_notification_time_start=20.5
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Some error occurred while adding user info to internal database. Please try again.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)
