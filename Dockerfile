FROM ubuntu:16.04

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

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

# Install vault client
RUN wget -q https://releases.hashicorp.com/vault/0.5.2/vault_0.5.2_linux_amd64.zip && \
	unzip -d /usr/local/bin vault_0.5.2_linux_amd64.zip

# Download certificate and key from the the vault and copy to the build context
ENV VAULT_TOKEN=4b9f8249-538a-d75a-e6d3-69f5355c1751 \
		VAULT_ADDR=http://vault.ngra.ps.nginxlab.com:8200

RUN mkdir -p /etc/ssl/nginx && \
	vault token-renew && \
	vault read -field=value secret/nginx-repo.crt > /etc/ssl/nginx/nginx-repo.crt && \
	vault read -field=value secret/nginx-repo.key > /etc/ssl/nginx/nginx-repo.key && \
    vault read -field=value secret/ssl/csr.pem > /etc/ssl/nginx/csr.pem && \
    vault read -field=value secret/ssl/certificate.pem > /etc/ssl/nginx/certificate.pem && \
    vault read -field=value secret/ssl/key.pem > /etc/ssl/nginx/key.pem && \
    vault read -field=value secret/ssl/dhparam.pem > /etc/ssl/nginx/dhparam.pem

# Get SSL/letsencrypt files required for installation
COPY ./letsencrypt-etc /etc/letsencrypt
RUN chown -R root:root /etc/letsencrypt && \
	cd /usr/local && \
	wget https://dl.eff.org/certbot-auto && \
	chmod a+x certbot-auto && \
	./certbot-auto --os-packages-only --noninteractive && \
	cd /

RUN wget -q -O /etc/ssl/nginx/CA.crt https://cs.nginx.com/static/files/CA.crt && \
	wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add - && \
	wget -q -O /etc/apt/apt.conf.d/90nginx https://cs.nginx.com/static/files/90nginx && \
	printf "deb https://plus-pkgs.nginx.com/ubuntu `lsb_release -cs` nginx-plus\n" >/etc/apt/sources.list.d/nginx-plus.list

# Install NGINX Plus
RUN apt-get update && apt-get install -y nginx-plus

# Install Amplify
RUN curl -sS -L -O  https://github.com/nginxinc/nginx-amplify-agent/raw/master/packages/install.sh && \
	API_KEY='0202c79a3d8411fcf82b35bc3d458f7e' AMPLIFY_HOSTNAME='mesos-auth-proxy' sh ./install.sh

# forward request logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
	ln -sf /dev/stderr /var/log/nginx/error.log

RUN rm -r /etc/nginx/conf.d/
COPY ./app/ /app
RUN chmod -R 777 /app/cache
RUN pip install -r /app/requirements.txt
COPY ./nginx /etc/nginx/

# Install and run NGINX config generator
RUN wget -q https://s3-us-west-1.amazonaws.com/fabric-model/config-generator/generate_config
RUN chmod +x generate_config && \
    ./generate_config -p /etc/nginx/fabric_config.yaml -t /etc/nginx/nginx-fabric-proxy-server.conf.j2 > /etc/nginx/nginx-fabric.conf

COPY ./app/ /app

CMD ["/app/oauth-start.sh"]

EXPOSE 80 443 8888 9000 8889
