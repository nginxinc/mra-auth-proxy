FROM ubuntu:16.04

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

ENV USE_NGINX_PLUS=true \
    USE_VAULT=false \
# CONTAINER_ENGINE specifies the container engine to which the
# containers will be deployed. Valid values are:
# - kubernetes
# - mesos (default)
# - local
    CONTAINER_ENGINE=kubernetes

COPY nginx/ssl/ /etc/ssl/nginx/
# Set the debconf front end to Noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get update && apt-get install -y -q \
	apt-transport-https \
	jq \
	vim \
	curl \
	libffi-dev \
	libssl-dev \
	lsb-release \
	python \
	python-dev \
	python-pip \
	unzip \
	wget && \
    cd /usr/local && \
    wget https://dl.eff.org/certbot-auto && \
    chmod a+x certbot-auto && \
    ./certbot-auto --os-packages-only --noninteractive && \
    cd /

# Install nginx
ADD install-nginx.sh /usr/local/bin/
COPY ./nginx /etc/nginx/
RUN /usr/local/bin/install-nginx.sh && \
# forward request logs to Docker log collector
    ln -sf /dev/stdout /var/log/nginx/access_log && \
    ln -sf /dev/stderr /var/log/nginx/error_log

COPY ./app/ /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt && \
#    mkdir /app/cache && \
    chown -R nginx /usr/src/app/cache

CMD ["/usr/src/app/oauth-start.sh"]

EXPOSE 80 443 8888 9000 8889 28015
