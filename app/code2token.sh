#!/bin/sh

CLIENT_ID=108432233305-b54d09r3l39vbkoj4gkjd7lar67habo7.apps.googleusercontent.com
CLIENT_SECRET=loAdwBqjulSEBh6k1c_ybozb
RURI=http://ngra.ps.nginxlab.com/login

rm -f /tmp/access_token.json 2>&1 /dev/null
if [ $# -eq 0 ]; then
	read -p "Enter authorization code: " AUTHZ_CODE
else
	AUTHZ_CODE=$1
fi

echo "INFO: exchanging authorization code for access token"
curl -s -o /tmp/access_token.json -H "Content-type: application/x-www-form-urlencoded" --data "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&code=$AUTHZ_CODE&grant_type=authorization_code&redirect_uri=$RURI" 'https://www.googleapis.com/oauth2/v3/token'
if [ $? -ne 0 ]; then
	echo "ERROR: problem obtaining access token"
	cat /tmp/access_token.json
	exit 1
fi

echo "INFO: extracting access token from response"
if [ `grep -c access_token /tmp/access_token.json` -eq 0 ]; then
	echo "ERROR: could not extract access token from response"
	cat /tmp/access_token.json
	exit 1
fi

echo "INFO: testing application"
ACCESS_TOKEN=`grep access_token /tmp/access_token.json | cut -f4 -d\"`
curl -H "Authorization: Bearer $ACCESS_TOKEN" $RURI
