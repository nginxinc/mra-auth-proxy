#!/bin/sh
NGINX_PID="/var/run/nginx.pid"    # /   (root directory)
NGINX_CONF="";
NGINX="nginx";
APP="oauth_daemon.py"

if [ "$DEBUG" = "true" ]
then
    NGINX="nginx-debug";
    echo System is set to DEBUG;
fi

case "$NETWORK" in
    fabric)
        NGINX_CONF="/etc/nginx/fabric_nginx_$CONTAINER_ENGINE.conf"
        echo 'Fabric configuration set'
        $NGINX -c "$NGINX_CONF" -g "pid $NGINX_PID;" &
        ;;
    router-mesh)
        ;;
    *)
        echo 'Network not supported'
esac

python /usr/src/app/$APP &

sleep 5
APP_PID=`ps aux | grep "$APP" | grep -v grep`

while [ "$APP_PID" ];
do 
	sleep 5;
	APP_PID=`ps aux | grep "$APP" | grep -v grep`;
done
