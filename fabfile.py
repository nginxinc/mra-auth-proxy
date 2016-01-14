#!/usr/bin/env python

from fabric.api import env, run, sudo, warn_only

env.hosts = [ '54.183.181.71' ]
env.user = 'ubuntu'

def deploy(tag='latest'):
	#pull latest image
	run('docker pull ngrefarch/auth-proxy')
	
	with warn_only():
		#stop all running docker containers
		run('docker stop $(docker ps -a -q)')

		#remove all stopped docker containers
		run('docker rm $(docker ps -a -q)')

	#start a docker container with the specified tag
	cmd = 'docker run -d -p 80:80 -p 443:443 ngrefarch/auth-proxy:{tag}'
	run(cmd.format(tag=tag))

	with warn_only():
		#clean up old docker images
		run('docker rmi $(docker images -a -q)')