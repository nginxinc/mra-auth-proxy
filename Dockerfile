FROM ubuntu:14.04

MAINTAINER NGINX Docker Maintainers "docker-maint@nginx.com"

# Set the debconf front end to Noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y -q \
	apt-transport-https \
	libffi-dev \
	libssl-dev \
	python \
	python-dev \
	python-pip \
	unzip \
	wget

# Install vault client
RUN wget https://releases.hashicorp.com/vault/0.5.2/vault_0.5.2_linux_amd64.zip && \
	unzip -d /usr/local/bin vault_0.5.2_linux_amd64.zip

# Download certificate and key from the the vault and copy to the build context
ENV VAULT_TOKEN=4b9f8249-538a-d75a-e6d3-69f5355c1751 \
		VAULT_ADDR=http://vault.ngra.ps.nginxlab.com:8200

RUN mkdir -p /etc/ssl/nginx && \
	vault token-renew && \
	vault read -field=value secret/nginx-repo.crt > /etc/ssl/nginx/nginx-repo.crt && \
	vault read -field=value secret/nginx-repo.key > /etc/ssl/nginx/nginx-repo.key

# Get other files required for installation
RUN wget -q -O /etc/ssl/nginx/CA.crt https://cs.nginx.com/static/files/CA.crt && \
	wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add - && \
	wget -q -O /etc/apt/apt.conf.d/90nginx https://cs.nginx.com/static/files/90nginx && \
	printf "deb https://plus-pkgs.nginx.com/ubuntu `lsb_release -cs` nginx-plus\n" >/etc/apt/sources.list.d/nginx-plus.list

# Install NGINX Plus
RUN apt-get update && apt-get install -y nginx-plus

# forward request logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
	ln -sf /dev/stderr /var/log/nginx/error.log

COPY ./nginx-oauth.conf /etc/nginx/
COPY ./app/ /app
COPY ./amplify_install.sh /amplify_install.sh

RUN pip install -r /app/requirements.txt
RUN API_KEY='0202c79a3d8411fcf82b35bc3d458f7e' HOSTNAME='auth-proxy' sh ./amplify_install.sh

CMD ["/app/oauth-start.sh"]

EXPOSE 80 443 8888 9000 8889
