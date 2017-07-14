#!/bin/bash

wget -O /usr/local/sbin/generate_config -q https://s3-us-west-1.amazonaws.com/fabric-model/config-generator/generate_config
chmod +x /usr/local/sbin/generate_config

if [ "$USE_NGINX_PLUS" = true ];
then
  echo "Installing NGINX Plus"

  wget -q -O /etc/ssl/nginx/CA.crt https://cs.nginx.com/static/files/CA.crt
  wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add -
  wget -q -O /etc/apt/apt.conf.d/90nginx https://cs.nginx.com/static/files/90nginx
  printf "deb https://plus-pkgs.nginx.com/`lsb_release -is | awk '{print tolower($0)}'` `lsb_release -cs` nginx-plus\n" >/etc/apt/sources.list.d/nginx-plus.list

  # Install NGINX Plus
  apt-get update
  apt-get install -o Dpkg::Options::="--force-confold" -y nginx-plus

  /usr/local/sbin/generate_config -p /etc/nginx/fabric_config.yaml -t /etc/nginx/nginx-plus-fabric.conf.j2 > /etc/nginx/nginx-fabric.conf
else
  echo "Installing NGINX OSS"

  wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add -
  printf "deb http://nginx.org/packages/`lsb_release -is | awk '{print tolower($0)}'`/ `lsb_release -cs` nginx\n" >/etc/apt/sources.list.d/nginx.list

  apt-get update
  apt-get install -o Dpkg::Options::="--force-confold" -y nginx

    /usr/local/sbin/generate_config -p /etc/nginx/fabric_config.yaml -t /etc/nginx/nginx-fabric.conf.j2 > /etc/nginx/nginx-fabric.conf
fi
