build:
	docker build -t oauth_daemon_example .

run:
	docker run -it -p 80:80 -v /Users/benhorowitz/Sites/oauth_daemon_example/app:/app example

shell:
	docker run -it -p 80:80 -v /Users/benhorowitz/Sites/oauth_daemon_example/app:/app example bash