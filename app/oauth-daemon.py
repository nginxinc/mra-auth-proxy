#!/usr/bin/python
# ''''which python2 >/dev/null && exec python2 "$0" "$@" # '''
# ''''which python  >/dev/null && exec python  "$0" "$@" # '''

# Copyright (C) 2014-2015 Nginx, Inc.

import json
import requests
import string
from flask import Flask
from flask import request
from flask import abort
from flask import Response
from oauth2client import client, crypt
import os
import redis
import traceback

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
        auth_token = request.headers.get('Auth-Token')
        auth_provider = request.headers.get('Auth-Provider')
        auth_fields = request.headers.get('Auth-Fields')

        if r is not None:
            auth_result = cached_authenticate(auth_token, auth_provider)
        else:
            auth_result = authenticate(auth_token, auth_provider)

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
    app.logger.debug('Key:' + key)

    result = r.get(key)

    if result is not None:
        result = json.loads(result)
    else:
        result = authenticate(auth_token, auth_provider)
        app.logger.debug(result)
        r.setex(key, json.dumps(result), int(os.environ.get('REDIS_TTL')))

    return result


def authenticate(auth_token, auth_provider):
    if auth_provider == 'facebook':
        auth_result = facebook(auth_token)
    elif auth_provider == 'google':
        auth_result = google(auth_token)
    else:
        app.logger.error('No auth provider matches')
        abort(401)

    return auth_result


def get_or_create_user(auth_provider, auth_result):
    url = request.headers.get('User-Manager-URL')
    response = requests.get((url + '/{}/{}').format(auth_provider, auth_result['id']))

    if (response.status_code == 200):
        return response.json()
    elif (response.status_code == 404):
        payload = {
            'name': auth_result['name'],
            'email': auth_result['email'],
            auth_provider + '_id': auth_result['id']
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
        # If multiple clients access the backend server:
        # if idinfo['aud'] not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID]:
        # 	raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        # if idinfo['hd'] != APPS_DOMAIN_NAME:
        # 	raise crypt.AppIdentityError("Wrong hosted domain.")

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=os.environ.get('FLASK_DEBUG', False))
