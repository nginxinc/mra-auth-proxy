name = ngrefarch/oauth_daemon_example
volumes = -v $(CURDIR)/app:/app -v $(CURDIR)/public_html:/public_html

build:
	docker build -t $(name) .

run:
	docker run -it -p 80:80 $(name)

run-v:
	docker run -it -p 80:80 $(volumes) $(name)

shell:
	docker run -it -p 80:80 -p 8888:8888 $(volumes) $(name) bash

push:
	docker push $(name)