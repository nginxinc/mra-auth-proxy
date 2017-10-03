#!/usr/bin/python

import json
import requests
import string
import os
import redis
import traceback

from flask import Flask
from flask import request
from flask import abort
from flask import Response
from oauth2client import client, crypt

#
#  oauth-daemon.py
#  AuthProxy
#
#  Copyright (C) 2017 NGINX Inc. All rights reserved.
#

app = Flask(__name__)

if os.environ.get('REDIS_ENABLED'):
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=os.environ.get('REDIS_PORT')
    )
else:
    r = None


@app.route('/')
def index():
    try:
        # These headers are set in default-location.conf and are
        # set as cookies in ingenious.js based on callbacks from
        # facebook and google authentication
        auth_token = request.headers.get('Auth-Token')
        auth_provider = request.headers.get('Auth-Provider')
        auth_fields = request.headers.get('Auth-Fields')
        
        # if auth_token is None or auth_provider is None:
        #     raise crypt.AppIdentityError("auth_token or auth_provider is None")
        auth_result = ''

        # if request.method == 'POST' and auth_provider == 'email':
        #     auth_token = request.data.form['email']
        #     auth_pass = request.data.form['password']

        if auth_token is not None and auth_token != '' and auth_provider is not None and auth_provider != '':
            if r is None:
                auth_result = authenticate(auth_token, auth_provider)
            else:
                auth_result = cached_authenticate(auth_token, auth_provider)

        resp = Response(status=401)

        if auth_result != '':
            result = get_or_create_user(auth_provider, auth_result)
            result['auth_result'] = auth_result

            app.logger.debug(json.dumps(result))

            resp = Response(status=200)
            resp.headers['Auth-Result'] = json.dumps(result)

            for field in string.split(auth_fields, ','):
                if field in result:
                    resp.headers['Auth-' + field] = result[field]

        return resp
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc('/dev/stdout')
        abort(401)


def cached_authenticate(auth_token, auth_provider):
    key = auth_token + '_' + auth_provider
    app.logger.debug('Key: ' + key)

    result = r.get(key)

    if result is None:
        result = authenticate(auth_token, auth_provider)
        app.logger.debug(result)

        if result['id'] is not None:
            r.setex(key, json.dumps(result), int(os.environ.get('REDIS_TTL')))
    else:
        result = json.loads(result)

    return result


def authenticate(auth_token, auth_provider):
    if auth_provider == 'facebook':
        auth_result = facebook(auth_token)
    elif auth_provider == 'google':
        auth_result = google(auth_token)
    elif auth_provider == 'local':
        auth_result = email(auth_token)
    else:
        app.logger.error('No auth provider matches')
        abort(401)

    return auth_result


def get_or_create_user(auth_provider, auth_result):
    url = request.headers.get('User-Manager-URL')
    auth_id = auth_result['local_id'] if auth_provider == 'local' else auth_result['id']
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


def facebook(input_token):
    facebook_app_id = request.headers.get('Facebook-App-ID')
    facebook_app_secret = request.headers.get('Facebook-App-Secret')
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


def google(token):
    google_client_id = request.headers.get('Google-Client-ID')

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


def email(auth_token):
    url = request.headers.get('User-Manager-URL')

    return requests.get(url + '/local/' + auth_token).json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=os.environ.get('FLASK_DEBUG', False))
