from unittest import TestCase
import os
import json
from mock import patch

from flask import Flask
from flask import request

from requests.models import Response

from oauth_daemon import index, cached_authenticate, authenticate, get_or_create_user, facebook, \
    google, email

class TestFacebookAuthenticate(TestCase):
    user = b'{"id": "ffbef342-975a-4b15-be21-2a4040a17ec3", "local_id": "144aa913-4aca-43be-8000-2803f271bd6a", "cover_pictures_id": "346", "password": "pbkdf2:sha1:1000$Ehb68QRI$5baf1409358c46f2a2ccf47bd06ea5d6ca6ec9aa", "profile_picture_url": "generic", "email": "email@gmail.com", "profile_pictures_id": "345"}'

    def get_facebook_user(arg, params, user=user):
        print('In facebook user function')
        print('Arg: ', arg)
        response = Response()
        response.status_code = 201

        if (arg == 'https://graph.facebook.com/debug_token'):
            response._content = b'{"data": {"is_valid": true, "user_id": "ffbef342-975a-4b15-be21-2a4040a17ec3"}}'
        elif (arg == 'https://graph.facebook.com'):
            response._content = user
        
        return response

    @patch('requests.get', side_effect=get_facebook_user)
    def test_facebook_auth(self, get_request_mock, user=user):
        result = facebook('7b435183-aeb3-4eb0-9abd-2023f98c7b45')
        self.assertEqual(json.loads(str(user, 'utf-8')), result)


class TestGoogleAuthenticate(TestCase):
    google_user = {"id": "ffbef342-975a-4b15-be21-2a4040a17ec3",
                   'name': 'test', 'email': 'email@gmail.com'}

    def verify_id_token(arg1, arg2):
        print('In verify id token')
        print('Arg1: ', arg1)
        print('Arg2: ', arg2)
        return {'iss': 'accounts.google.com', "sub": "ffbef342-975a-4b15-be21-2a4040a17ec3", 'name': 'test', 'email': 'email@gmail.com'}

    @patch('oauth2client.client.verify_id_token', side_effect=verify_id_token)
    def test_google_auth(self, verify_id_mock, user=google_user):
        result = google('7b435183-aeb3-4eb0-9abd-2023f98c7b45')
        self.assertEqual(user, result)


class TestLocalAuthenticate(TestCase):
    user = b'{"id": "ffbef342-975a-4b15-be21-2a4040a17ec3", "local_id": "144aa913-4aca-43be-8000-2803f271bd6a", "cover_pictures_id": "346", "password": "pbkdf2:sha1:1000$Ehb68QRI$5baf1409358c46f2a2ccf47bd06ea5d6ca6ec9aa", "profile_picture_url": "generic", "email": "email@gmail.com", "profile_pictures_id": "345"}'

    # Setup function for testing local email authentication
    def setUp(self):
        self.app = Flask(__name__)
        print(self.app)

    def get_user(arg1, user=user):
        print('In user function')
        print('Arg1: ', arg1)
        response = Response()
        response.status_code = 201
        response._content = user
        return response

    @patch('requests.get', side_effect=get_user)
    def test_email_auth(self, get_request_mock, user=user):
        with self.app.test_request_context(headers={'User-Manager-URL': 'test'}):
            result = authenticate('7b435183-aeb3-4eb0-9abd-2023f98c7b45', 'local')
            self.assertEqual(json.loads(str(user, 'utf-8')), result)


class TestGetOrCreateUser(TestCase):
    user = b'{"id": "ffbef342-975a-4b15-be21-2a4040a17ec3", "local_id": "144aa913-4aca-43be-8000-2803f271bd6a", "cover_pictures_id": "346", "password": "pbkdf2:sha1:1000$Ehb68QRI$5baf1409358c46f2a2ccf47bd06ea5d6ca6ec9aa", "profile_picture_url": "generic", "email": "email@gmail.com", "profile_pictures_id": "345"}'

    # Setup function for testing local email authentication
    def setUp(self):
        self.app = Flask(__name__)

    def get_user(arg, user=user):
        print('In user get function: ')
        print('Arg: ', arg)
        response = Response()

        if (arg == 'test/local/test_id'):
            response.status_code = 200
            response._content = user
        elif (arg == 'test/local/no_id'):
            response.status_code = 404
            return response
    
    def post_user(arg, json, user=user):
        print('In user post function')
        print('Arg1: ', arg)
        print('Arg2: ', json)
        response = Response()
        response.status_code = 201
        response._content = user
        return response

    @patch('requests.get', side_effect=get_user)
    def test_email_auth(self, get_request_mock, user=user):
        with self.app.test_request_context(headers={'User-Manager-URL': 'test'}):
            result = get_or_create_user('local', {'local_id': 'test_id'})
            print('Result: ', result)
            self.assertEqual(json.loads(str(user, 'utf-8')), result)

    @patch('requests.post', side_effect=post_user)
    @patch('requests.get', side_effect=get_user)
    def test_email_auth(self, get_request_mock, post_request_mock, user=user):
        with self.app.test_request_context(headers={'User-Manager-URL': 'test'}):
            result = get_or_create_user('local', {'local_id': 'no_id', 'name':'testName', 'email':'email@gmail.com'})
            print('Result: ', result)
            self.assertEqual(json.loads(str(user, 'utf-8')), result)

class TestIndex(TestCase):
    user = b'{"id": "ffbef342-975a-4b15-be21-2a4040a17ec3", "local_id": "144aa913-4aca-43be-8000-2803f271bd6a", "cover_pictures_id": "346", "password": "pbkdf2:sha1:1000$Ehb68QRI$5baf1409358c46f2a2ccf47bd06ea5d6ca6ec9aa", "profile_picture_url": "generic", "email": "email@gmail.com", "profile_pictures_id": "345"}'

    def redis_get(arg, user=user):
        print('In redis get function')
        print('Arg: ', arg)
        return user

    # Setup function for testing local email authentication
    def setUp(self):
        self.app = Flask(__name__)

    def patch_authenticate(arg1, arg2):
        print('In authenticate function')
        print('Arg1: ', arg1)
        print('Arg2: ', arg2)
        return arg2

    @patch('redis.StrictRedis.get', side_effect=redis_get)
    def patch_cached_authenticate(self, redis_mock, user=user):
        result = cached_authenticate('144aa913-4aca-43be-8000-2803f271bd6a', 'local')
        print('Result: ', json.dumps(result))
        self.assertEqual(json.loads(str(user, 'utf-8')), result)
        return result

    def patch_get_or_create(arg1, arg2, user=user):
        print('In get or create function')
        print('Arg1: ', arg1)
        print('Arg2: ', arg2)
        return json.loads(str(user, 'utf-8'))

    @patch('oauth_daemon.get_or_create_user', side_effect=patch_get_or_create)
    @patch('oauth_daemon.cached_authenticate', side_effect=patch_cached_authenticate)
    @patch('oauth_daemon.authenticate', side_effect=patch_authenticate)
    def test_index(self, mock_auth, mock_cached_auth, mock_get_or_create, user=user):
        with self.app.test_request_context(headers={'Auth-Token': 'testToken', 'Auth-Provider': 'testProvider', 'Auth-Fields': 'testFields'}):
            user = json.loads(str(user, 'utf-8'))
            user['auth_result'] = 'testProvider'
            result = index()
            print(result.headers['Auth-Result'])
            self.assertEqual(json.dumps(user), result.headers['Auth-Result'])