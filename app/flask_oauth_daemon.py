#!/usr/bin/python
#''''which python2 >/dev/null && exec python2 "$0" "$@" # '''
#''''which python  >/dev/null && exec python  "$0" "$@" # '''

# Copyright (C) 2014-2015 Nginx, Inc.

import json
import os
import requests

from flask import Flask
from flask import request
from flask import abort
from flask import Response

from os.path import join, dirname
from dotenv import load_dotenv

from oauth2client import client, crypt

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

facebook_app_id = os.environ.get("FACEBOOK_APP_ID")
facebook_app_secret = os.environ.get("FACEBOOK_APP_SECRET")
facebook_app_access_token = facebook_app_id + '|' + facebook_app_secret

google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

app = Flask(__name__)

@app.route('/')
def index():
	try:	
		auth_token = request.headers.get('Auth-Token')

		if request.headers.get('Auth-Provider') == 'facebook':
			result = facebook(auth_token)
		elif request.headers.get('Auth-Provider') == 'google':
			result = google(auth_token)
		else:
			app.logger.error('No auth provider matches')
			abort(401)

		resp = Response(status=200)
		resp.headers['X-OAuth-Result'] = json.dumps(result)
		resp.headers['X-OAuth-name'] = result['name']
		resp.headers['X-OAuth-email'] = result['email']
		return resp
	except Exception as e:
		app.logger.error(e)
		abort(401)
	

def facebook(input_token):
	token_verification_params = {
		'input_token': input_token,
		'access_token' :facebook_app_access_token
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
	app.run(host='0.0.0.0', port=8888, debug = True)