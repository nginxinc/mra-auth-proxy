#!/bin/sh
conf="/var/run/nginx.pid"    # /   (root directory)
APP="oauth-daemon.py"
PID=`ps aux | grep $APP | grep -v grep`

nginx_conf="/etc/nginx/nginx.conf";
nginx_fabric="/etc/nginx/nginx-fabric.conf";

/app/$APP &

if [ "$NETWORK" = "fabric" ]
then
    nginx_conf=$nginx_fabric;
    echo This is the nginx conf = $nginx_conf;
    echo fabric configuration set;
fi

nginx -c "$nginx_conf" -g "pid $pid;" &

service amplify-agent start

sleep 30

while [ -f "$conf" ] &&  [ "$PID" ];
do 
	sleep 5;
	PID=`ps aux | grep $APP | grep -v grep`;
	#echo "The python process: $PID"
done
