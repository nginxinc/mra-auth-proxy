tag = ngrefarch/auth-proxy
volumes = -v $(CURDIR)/app:/app -v $(CURDIR)/nginx-oauth.conf:/etc/nginx/nginx-oauth.conf
ports = -p 80:80 -p 443:443

build: check-env
	docker build --build-arg VAULT_TOKEN=$(VAULT_TOKEN) -t $(tag) .

build-clean:
	docker build --no-cache --build-arg VAULT_TOKEN=$(VAULT_TOKEN) -t $(tag) .

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

check-env:
ifndef VAULT_TOKEN
    $(error VAULT_TOKEN is undefined)
endif