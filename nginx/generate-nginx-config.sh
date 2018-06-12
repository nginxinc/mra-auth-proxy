#!/usr/bin/env bash

wget -O /usr/local/sbin/generate_config -q https://s3-us-west-1.amazonaws.com/fabric-model/config-generator/generate_config
chmod +x /usr/local/sbin/generate_config

FABRIC_TEMPLATE_FILE="/etc/nginx/fabric/fabric_nginx-plus.conf.j2"
ROUTER_MESH_TEMPLATE_FILE="/etc/nginx/router-mesh/router-mesh_nginx-plus.conf.j2"

if [ "$USE_NGINX_PLUS" = false ];
then
    FABRIC_TEMPLATE_FILE="/etc/nginx/fabric/fabric_nginx.conf.j2"
elif [ "$USE_MTLS" = true ];
then
    FABRIC_TEMPLATE_FILE="/etc/nginx/fabric/fabric_mtls_nginx-plus.conf.j2"
fi

echo Generating NGINX configurations...
echo Fabric Template File ${FABRIC_TEMPLATE_FILE}
echo Router Mesh Template File ${ROUTER_MESH_TEMPLATE_FILE}

# Generate configurations for Fabric Model
/usr/local/sbin/generate_config -p /etc/nginx/fabric/fabric_config.yaml -t ${FABRIC_TEMPLATE_FILE} > /etc/nginx/fabric_nginx_dcos.conf
/usr/local/sbin/generate_config -p /etc/nginx/fabric/fabric_config_k8s.yaml -t ${FABRIC_TEMPLATE_FILE} > /etc/nginx/fabric_nginx_kubernetes.conf
/usr/local/sbin/generate_config -p /etc/nginx/fabric/fabric_config_local.yaml -t ${FABRIC_TEMPLATE_FILE} > /etc/nginx/fabric_nginx_local.conf

# Generate configurations for Router Mesh
/usr/local/sbin/generate_config -p /etc/nginx/router-mesh/router-mesh_config_k8s.yaml -t ${ROUTER_MESH_TEMPLATE_FILE} > /etc/nginx/router-mesh_nginx_kubernetes.conf
/usr/local/sbin/generate_config -p /etc/nginx/router-mesh/router-mesh_config_local.yaml -t ${ROUTER_MESH_TEMPLATE_FILE} > /etc/nginx/router-mesh_nginx_local.conf
