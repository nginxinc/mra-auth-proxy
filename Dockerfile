FROM ngrefarch/python_base:3.5

ARG CONTAINER_ENGINE_ARG
ARG GOOGLE_CLIENT_ID_ARG
ARG FACEBOOK_APP_ID_ARG
ARG FACEBOOK_SECRET_KEY_ARG

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

ENV USE_NGINX_PLUS=true \
    USE_VAULT=false \
# CONTAINER_ENGINE specifies the container engine to which the
# containers will be deployed. Valid values are:
# - kubernetes
# - mesos (default)
# - local
    CONTAINER_ENGINE=${CONTAINER_ENGINE_ARG:-kubernetes} \
    GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID_ARG} \
    FACEBOOK_APP_ID=${FACEBOOK_APP_ID_ARG} \
    FACEBOOK_APP_SECRET=${FACEBOOK_SECRET_KEY_ARG}

COPY nginx/ssl/ /etc/ssl/nginx/
COPY ./app/ /usr/src/app
WORKDIR /usr/src/app

# Install nginx
ADD install-nginx.sh /usr/local/bin/
COPY ./nginx /etc/nginx/
RUN /usr/local/bin/install-nginx.sh && \
# forward request logs to Docker log collector
    ln -sf /dev/stdout /var/log/nginx/access_log && \
    ln -sf /dev/stderr /var/log/nginx/error_log

RUN pip install -r /usr/src/app/requirements.txt && \
#    mkdir /app/cache && \
    chown -R nginx /usr/src/app/cache && \
    python -m unittest

CMD ["/usr/src/app/oauth-start.sh"]

EXPOSE 80 443
