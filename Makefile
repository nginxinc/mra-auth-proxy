tag = ngrefarch/auth-proxy
volumes = -v $(CURDIR)/app:/app -v $(CURDIR)/nginx-oauth.conf:/etc/nginx/nginx-oauth.conf
ports = -p 81:80

build:
	docker build -t $(tag) .

build-clean:
	docker build --no-cache -t $(tag) .

run:
	docker run -it $(ports) $(tag)

run-v:
	docker run -it $(ports) $(volumes) $(tag)

shell:
	docker run -it $(ports) $(volumes) $(tag) bash

push:
	docker push $(tag)

test:
	echo "Tests not yet implemented"
