#!/bin/sh
NGINX_PID="/var/run/nginx.pid"    # /   (root directory)
APP="oauth-daemon.py"

NGINX_CONF="/etc/nginx/nginx.conf";
NGINX_FABRIC="/etc/nginx/nginx-fabric.conf";
NGINX_FABRIC2="/etc/nginx/nginx-fabric-2.conf";
NGINX="nginx";

/app/$APP &

if [ "$NETWORK" = "fabric" ]
then
    NGINX_CONF=$NGINX_FABRIC;
    echo This is the nginx conf = $NGINX_CONF;
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
