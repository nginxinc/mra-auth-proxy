FROM python:3.5

RUN useradd --create-home -s /bin/bash auth-proxy

ARG CONTAINER_ENGINE_ARG
ARG GOOGLE_CLIENT_ID_ARG
ARG FACEBOOK_APP_ID_ARG
ARG FACEBOOK_SECRET_KEY_ARG
ARG USE_NGINX_PLUS_ARG
ARG USE_VAULT_ARG
ARG NETWORK_ARG

MAINTAINER NGINX Docker Maintainers "mra-dev@nginx.com"

# CONTAINER_ENGINE specifies the container engine to which the
# containers will be deployed. Valid values are:
# - kubernetes (default)
# - mesos
# - local
ENV USE_NGINX_PLUS=${USE_NGINX_PLUS_ARG:-true} \
    USE_VAULT=${USE_VAULT_ARG:-false} \
    CONTAINER_ENGINE=${CONTAINER_ENGINE_ARG:-kubernetes} \
    NETWORK=${NETWORK_ARG:-fabric} \
    GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID_ARG} \
    FACEBOOK_APP_ID=${FACEBOOK_APP_ID_ARG} \
    FACEBOOK_APP_SECRET=${FACEBOOK_SECRET_KEY_ARG}

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get update && apt-get install -y -q \
    apt-transport-https \
    libffi-dev \
    libssl-dev \
    lsb-release \
    wget && \
    cd /

COPY nginx/ssl/ /etc/ssl/nginx/
COPY ./app/ /usr/src/app
WORKDIR /usr/src/app

# Install nginx
ADD install-nginx.sh /usr/local/bin/
COPY ./nginx /etc/nginx/
RUN /usr/local/bin/install-nginx.sh && \
    ln -sf /dev/stdout /var/log/nginx/access_log && \
    ln -sf /dev/stderr /var/log/nginx/error_log

# Build the application
RUN pip install -r /usr/src/app/requirements.txt && \
    python -m unittest

RUN chmod -R 777 /usr/src/app

CMD ["/usr/src/app/oauth-start.sh"]

EXPOSE 80 443
