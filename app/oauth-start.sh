#!/bin/sh
NGINX_PID="/var/run/nginx.pid"    # /   (root directory)
APP="oauth-daemon.py"

NGINX_CONF="/etc/nginx/nginx.conf";
NGINX_FABRIC="/etc/nginx/nginx-fabric.conf";
NGINX_FABRIC2="/etc/nginx/nginx-fabric-2.conf";

/app/$APP &

if [ "$NETWORK" = "fabric" ]
then
    NGINX_CONF=$NGINX_FABRIC;
    echo This is the nginx conf = $NGINX_CONF;
    echo fabric configuration set;
fi

if [ "$NETWORK" = "fabric2" ]
then
    NGINX_CONF=$NGINX_FABRIC2;
    echo This is the nginx conf = $NGINX_CONF;
    echo fabric2 configuration set;
fi


nginx -c "$NGINX_CONF" -g "pid $NGINX_PID;" &

service amplify-agent start

################----AN UGLY HACK TO DEAL WITH DOCKERCLOUD'S RELIANCE ON SEARCH DOMAINS---################
# SEARCH_DOMAIN=`cat /etc/resolv.conf | awk -F " " '/search/ {print $2}'`
# echo `curl "http://localhost/upstream_conf?add=&upstream=user-manager&server=router-mesh.$SEARCH_DOMAIN"`
# echo `curl "http://localhost/upstream_conf?add=&upstream=pages&server=pages.$SEARCH_DOMAIN"`
# echo `curl "http://localhost/upstream_conf?remove=&upstream=user-manager&id=0"`
# echo `curl "http://localhost/upstream_conf?remove=&upstream=pages&id=0"`
#########################################################################################################

sleep 5
APP_PID=`ps aux | grep "$APP" | grep -v grep`

while [ -f "$NGINX_PID" ] &&  [ "$APP_PID" ];
do 
	sleep 5;
	APP_PID=`ps aux | grep "$APP" | grep -v grep`;
	#echo "The python process: $PID"
done
