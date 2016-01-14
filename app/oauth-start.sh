#!/bin/sh
conf="/var/run/nginx.pid"    # /   (root directory)

/app/oauth-daemon.py &

nginx -c /etc/nginx/nginx-oauth.conf -g "pid $conf; worker_processes 2;" &

service amplify-agent start

sleep 500

while [ -f "$conf" ]
do 
	sleep 500;
done