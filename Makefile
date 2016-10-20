tag = ngrefarch/auth-proxy:mesos
volumes = -v $(CURDIR)/app:/app -v $(CURDIR)/nginx:/etc/nginx
ports = -p 80:80 -p 443:443
env = --env-file=.env

build:
	docker build -t $(tag) .

build-clean:
	docker build --no-cache -t $(tag) .

run:
	docker run -it ${env} $(ports) $(tag)

run-v:
	docker run -it ${env} $(ports) $(volumes) $(tag)

shell:
	docker run -it ${env} $(ports) $(volumes) $(tag) bash

push:
	docker push $(tag)

test:
	echo "Tests not yet implemented"
