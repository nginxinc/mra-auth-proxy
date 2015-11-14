import json
import os
import requests

from flask import Flask
from flask import request
from flask import abort
from flask import Response

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

facebook_app_id = os.environ.get("FACEBOOK_APP_ID")
facebook_app_secret = os.environ.get("FACEBOOK_APP_SECRET")

facebook_app_access_token = facebook_app_id + '|' + facebook_app_secret

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/facebook')
def facebook():
	input_token = request.headers.get('X-Access-Token')

	token = requests.get(
			'https://graph.facebook.com/debug_token',
			params = {
				'input_token': input_token,
				'access_token' :facebook_app_access_token
			}
		).json()

	app.logger.debug(token)

	try:
		if token['data']['is_valid']:
			profile = requests.get(
					'https://graph.facebook.com',
					params = {
						'access_token': facebook_app_access_token,
						'id': token['data']['user_id'],
						'fields': 'id,name,email,picture'
					}
				).json()

			resp = Response(status=200)
			resp.headers['X-OAuth-Result'] = json.dumps(profile)
			return resp
		else:
			app.logger.error(token.data.error)
			abort(401)
	except Exception as e:
		app.logger.error(e)
		app.logger.error(token)
		abort(401)

	

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug = True)