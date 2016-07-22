#!/bin/sh
conf="/var/run/nginx.pid"    # /   (root directory)

/app/oauth-daemon.py &

nginx -c /etc/nginx/nginx-oauth.conf -g "pid $conf;" &

#curl "http://localhost/upstream_conf?add=&upstream=backend&server=$PAGES_URL&max_fails=0"

service amplify-agent start

sleep 30

while [ -f "$conf" ]
do 
	sleep 5;
	print "in the while loop\n";
done