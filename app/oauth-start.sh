#!/bin/sh
NGINX_PID="/var/run/nginx.pid"    # /   (root directory)
APP="oauth_daemon.py"

NGINX_CONF="/etc/nginx/nginx.conf";
NGINX="nginx";

python /usr/src/app/$APP &

if [ "$NETWORK" = "fabric" ]
then
    echo fabric configuration set;
fi

if [ "$DEBUG" = "true" ]
then
    NGINX="nginx-debug";
    echo System is set to DEBUG;
fi

$NGINX -c "$NGINX_CONF" -g "pid $NGINX_PID;" &

sleep 5
APP_PID=`ps aux | grep "$APP" | grep -v grep`

while [ "$APP_PID" ];
do 
	sleep 5;
	APP_PID=`ps aux | grep "$APP" | grep -v grep`;
done
