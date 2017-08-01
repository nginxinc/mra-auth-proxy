FROM ubuntu:16.04

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

ENV USE_NGINX_PLUS true


# Set the debconf front end to Noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y -q \
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
	wget

# Get SSL/letsencrypt files required for installation
COPY ./letsencrypt-etc vault_env.sh /etc/letsencrypt/
RUN chown -R root:root /etc/letsencrypt && \
	cd /usr/local && \
	wget https://dl.eff.org/certbot-auto && \
	chmod a+x certbot-auto && \
	./certbot-auto --os-packages-only --noninteractive && \
	cd /

# Install vault client
RUN wget -q https://releases.hashicorp.com/vault/0.5.2/vault_0.5.2_linux_amd64.zip && \
	unzip -d /usr/local/bin vault_0.5.2_linux_amd64.zip && \
	. /etc/letsencrypt/vault_env.sh && \
	env && \
	mkdir -p /etc/ssl/nginx && \
	vault token-renew && \
	vault read -field=value secret/nginx-repo.crt > /etc/ssl/nginx/nginx-repo.crt && \
	vault read -field=value secret/nginx-repo.key > /etc/ssl/nginx/nginx-repo.key && \
	vault read -field=value secret/ssl/csr.pem > /etc/ssl/nginx/csr.pem && \
	vault read -field=value secret/ssl/certificate.pem > /etc/ssl/nginx/certificate.pem && \
	vault read -field=value secret/ssl/key.pem > /etc/ssl/nginx/key.pem && \
	vault read -field=value secret/ssl/dhparam.pem > /etc/ssl/nginx/dhparam.pem && \
	vault read -field=value secret/letsencrypt/cert.pem > /etc/letsencrypt/archive/mra.nginxps.com/cert2.pem && \
	vault read -field=value secret/letsencrypt/chain.pem > /etc/letsencrypt/archive/mra.nginxps.com/chain2.pem && \
	vault read -field=value secret/letsencrypt/fullchain.pem > /etc/letsencrypt/archive/mra.nginxps.com/fullchain2.pem && \
	vault read -field=value secret/letsencrypt/privkey.pem > /etc/letsencrypt/archive/mra.nginxps.com/privkey2.pem

# Install nginx
ADD install-nginx.sh /usr/local/bin/
COPY ./nginx /etc/nginx/
RUN /usr/local/bin/install-nginx.sh

# forward request logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
	ln -sf /dev/stderr /var/log/nginx/error.log

RUN rm -r /etc/nginx/conf.d/
COPY ./app/ /app
RUN pip install -r /app/requirements.txt
RUN mkdir /app/cache && \
	chown -R nginx /app/cache


COPY ./app/ /app

CMD ["/app/oauth-start.sh"]

EXPOSE 80 443 8888 9000 8889 28015
