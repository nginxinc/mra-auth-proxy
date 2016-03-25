FROM ubuntu:14.04

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

# Set the debconf front end to Noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y -q \
	apt-transport-https \
	jq \
	libffi-dev \
	libssl-dev \
	python \
	python-dev \
	python-pip \
	wget

# Download certificate and key from the the vault and copy to the build context
ARG VAULT_TOKEN
RUN mkdir -p /etc/ssl/nginx
RUN wget -q -O - --header="X-Vault-Token: $VAULT_TOKEN" http://vault.ngra.ps.nginxlab.com:8200/v1/secret/nginx-repo.crt | jq -r .data.value > /etc/ssl/nginx/nginx-repo.crt
RUN wget -q -O - --header="X-Vault-Token: $VAULT_TOKEN" http://vault.ngra.ps.nginxlab.com:8200/v1/secret/nginx-repo.key | jq -r .data.value > /etc/ssl/nginx/nginx-repo.key

# Get other files required for installation
#COPY ./nginx-repo.key /etc/ssl/nginx/
#COPY ./nginx-repo.crt /etc/ssl/nginx/
COPY ./dhparam.pem /etc/ssl/nginx/
COPY ./letsencrypt-etc /etc/letsencrypt
COPY /letsencrypt /usr/local/letsencrypt
RUN chown -R root /etc/letsencrypt

RUN wget -q -O /etc/ssl/nginx/CA.crt https://cs.nginx.com/static/files/CA.crt && \
	wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add - && \
	wget -q -O /etc/apt/apt.conf.d/90nginx https://cs.nginx.com/static/files/90nginx && \
	printf "deb https://plus-pkgs.nginx.com/ubuntu `lsb_release -cs` nginx-plus\n" >/etc/apt/sources.list.d/nginx-plus.list

# Install NGINX Plus
RUN apt-get update && apt-get install -y nginx-plus-extras

# forward request logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
	ln -sf /dev/stderr /var/log/nginx/error.log

COPY ./nginx-oauth.conf /etc/nginx/
COPY ./nginx-gz.conf /etc/nginx/
COPY ./nginx-ssl.conf /etc/nginx/
COPY ./app/ /app
COPY ./amplify_install.sh /amplify_install.sh
#COPY ./nginx /usr/sbin/nginx

RUN pip install -r /app/requirements.txt
RUN API_KEY='0202c79a3d8411fcf82b35bc3d458f7e' HOSTNAME='auth-proxy' sh ./amplify_install.sh

CMD ["/app/oauth-start.sh"]

EXPOSE 80 443 8888 9000 8889