#!/usr/bin/python

import json
import requests
import os
import redis
import traceback

from flask import Flask
from flask import request
from flask import abort
from flask import Response
from oauth2client import client, crypt

#
#  oauth_daemon.py
#  AuthProxy
#
#  Copyright (C) 2017 NGINX Inc. All rights reserved.
#

# Initialize Flask
app = Flask(__name__)

# Initialize REDIS cache, if REDIS_ENABLED environment variable is true
if os.environ.get('REDIS_ENABLED'):
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=os.environ.get('REDIS_PORT')
    )
else:
    r = None


#
# Handle traffic on the "/" path
#
@app.route('/')
def index():

    try:
        # These headers are set in default-location.conf and are
        # set as cookies in ingenious.js based on callbacks from
        # facebook and google authentication
        auth_token = request.headers.get('Auth-Token')
        auth_provider = request.headers.get('Auth-Provider')
        auth_fields = request.headers.get('Auth-Fields')
        auth_result = ''
        # Ensure that auth_token and auth_provider are set before
        # attempting to authenticate/authorize the user
        if auth_token is not None and auth_token != '' and auth_provider is not None and auth_provider != '':
            if r is None:
                # authenticate against the provider
                auth_result = authenticate(auth_token, auth_provider)
            else:
                # authenticate against the cache, if the REDIS_ENABLED environment variable is true
                auth_result = cached_authenticate(auth_token, auth_provider)

        # set a default response value
        resp = Response(status=401)

        # Verify that auth_result has been set by one of the authenticate methods
        if auth_result != '':
            result = get_or_create_user(auth_provider, auth_result)
            result['auth_result'] = auth_result
            app.logger.debug(json.dumps(result))
            resp = Response(status=200)
            resp.headers['Auth-Result'] = json.dumps(result)

            # set the response headers
            for field in auth_fields.split(','):
                if field in result:
                    resp.headers['Auth-' + field] = result[field]

        return resp
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
        abort(401)


#
# Authenticate the user using the cache
# @param auth_token: the string from the Auth-Token header
# @param auth_provider: the string from the Auth-Provider header
#
def cached_authenticate(auth_token, auth_provider):
    key = auth_token + '_' + auth_provider
    app.logger.debug('Key: ' + key)

    # look for the user in the cache
    result = r.get(key)
    app.logger.debug(result)

    if result is None:
        # if no result was found in the cache, then
        # call the authenticate method
        result = authenticate(auth_token, auth_provider)
        app.logger.debug(result)
        if 'id' in result and result['id'] is not None:
            r.setex(key, json.dumps(result), int(os.environ.get('REDIS_TTL')))
    else:
        result = json.loads(str(result, 'utf-8'))

    return result


#
# Authenticate the user against the provider
# @param auth_token: the string from the Auth-Token header
# @param auth_provider: the string from the Auth-Provider header
#
def authenticate(auth_token, auth_provider):

    if auth_provider == 'facebook':
        # authenticate calling the facebook API
        auth_result = facebook(auth_token)
    elif auth_provider == 'google':
        # authenticate calling the google API
        auth_result = google(auth_token)
    elif auth_provider == 'local':
        # authenticate against the user-manager service
        auth_result = email(auth_token)
    else:
        app.logger.error('No auth provider matches')
        abort(401)

    return auth_result


#
# Get or Create the user from the user-manager database
# @param auth_provider: the string from the Auth-Provider header
# @param auth_result: the JSON result from one of the authenticate methods
#
def get_or_create_user(auth_provider, auth_result):

    # this header is set in default-location.conf
    url = request.headers.get('User-Manager-URL')

    # when using the local authentication provider, the auth ID is stored in the
    # local_id entry of the auth_result
    auth_id = auth_result['local_id'] \
        if 'local_id' in auth_result and auth_provider == 'local' else auth_result['id']
    response = requests.get((url + '/{}/{}').format(auth_provider, auth_id))
    app.logger.debug((url + '/{}/{}').format(auth_provider, auth_id))

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        payload = {
            'name': auth_result['name'],
            'email': auth_result['email'],
            auth_provider + '_id': auth_id
        }
        return requests.post(url, json=payload).json()
    else:
        app.logger.error(response)


#
# Authenticate using Facebook
# @param input_token: the string previously assigned to the authenticated user
#
def facebook(input_token):
    facebook_app_id = os.environ.get('FACEBOOK_APP_ID')
    facebook_app_secret = os.environ.get('FACEBOOK_APP_SECRET')
    facebook_app_access_token = facebook_app_id + '|' + facebook_app_secret

    token_verification_params = {
        'input_token': input_token,
        'access_token': facebook_app_access_token
    }

    token = requests.get('https://graph.facebook.com/debug_token', params=token_verification_params).json()

    app.logger.debug(token)

    if token['data']['is_valid']:
        user_info_params = {
            'access_token': facebook_app_access_token,
            'id': token['data']['user_id'],
            'fields': 'id,name,email,picture'
        }

        profile = requests.get('https://graph.facebook.com', params=user_info_params).json()

        return profile
    else:
        app.logger.error(token.data.error)
        abort(401)


#
# Authenticate using Google
# @param token: the string previously assigned to the authenticated user
#
def google(token):
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')

    try:
        idinfo = client.verify_id_token(token, google_client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

        app.logger.debug(idinfo)

        result = {
            'id': idinfo['sub'],
            'name': idinfo['name'],
            'email': idinfo['email']
        }

        return result
    except crypt.AppIdentityError:
        # Invalid token
        abort(401)


#
# Authenticate using the User manager service
# @param auth_token: the string previously assigned to the authenticated user
#
def email(auth_token):
    url = request.headers.get('User-Manager-URL')

    return requests.get(url + '/local/' + auth_token).json()


#
# Main method to start the flask application
#
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=os.environ.get('FLASK_DEBUG', False))
