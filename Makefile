volumes = -v $(CURDIR)/app:/app -v $(CURDIR)/public_html:/public_html

build:
	docker build -t oauth_daemon_example .

run:
	docker run -it -p 80:80 oauth_daemon_example

run-v:
	docker run -it -p 80:80 $(volumes) oauth_daemon_example	

shell:
	docker run -it -p 80:80 -p 8888:8888 $(volumes) oauth_daemon_example bash