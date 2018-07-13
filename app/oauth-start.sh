#!/bin/sh
NGINX_PID="/var/run/nginx.pid"    # /   (root directory)
NGINX_CONF="";
APP="oauth_daemon.py"

su auth-proxy -c 'python /usr/src/app/oauth_daemon.py' &

if [ "$DEBUG" = "true" ]
then
    NGINX="nginx-debug";
    echo System is set to DEBUG;
fi

python /usr/src/app/${APP} &

sleep 5
APP_PID=`ps aux | grep "$APP" | grep -v grep`


case "$NETWORK" in
    fabric)
        NGINX_CONF="/etc/nginx/fabric_nginx_$CONTAINER_ENGINE.conf"
        echo 'Fabric configuration set'
        ;;
    router-mesh)
        NGINX_CONF="/etc/nginx/router-mesh_nginx_$CONTAINER_ENGINE.conf"
        echo 'Router Mesh configuration set'
        ;;
    proxy)
        ;;
    *)
        echo 'Network not supported'
        exit 1;
esac

nginx -c "$NGINX_CONF" -g "pid $NGINX_PID;" &

sleep 10

while [ -f "$NGINX_PID" ] &&  [ "$APP_PID" ];
do
	sleep 5;
	APP_PID=`ps aux | grep "$APP" | grep -v grep`;
done
