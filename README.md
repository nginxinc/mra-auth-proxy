# NGINX Microservices Reference Architecture: Auth Proxy Service

This repository contains a simple Python application which is used to provide authentication and authorization for the NGINX _Ingenious_ application. 
The _Ingenious_ application has been developed by the NGINX Professional Services team to provide a reference 
architecture for building your own microservices based application using NGINX as the service mesh for the services. 

The Auth Proxy Service is configured to validate authentication tokens and route requests to other components in the NGINX Microservice Reference Architecure: 
- [Album Manager Service](https://github.com/nginxinc/ngra-album-manager "Album Manager")
- [Content Service](https://github.com/nginxinc/ngra-content-service "Content Service")
- [Pages](https://github.com/nginxinc/ngra-pages "Pages Service")
- [Photo Resizer Service](https://github.com/nginxinc/ngra-photoresizer "Photo Resizer")
- [Photo Uploader Service](https://github.com/nginxinc/ngra-photouploader "Photo Uploader")
- [User Manager Service](https://github.com/nginxinc/user-manager "User Manager Service")

In addition, the Auth Proxy Service is configured to use an external service named _fake-s3_. In a production environment, the
application would use a real Amazon S3 implementation. For the purposes of a sample or reference application, we use an image provided by
[lphoward](https://hub.docker.com/r/lphoward/fake-s3/ "Fake S3 image"). 

The default configuration for all the components of the MRA, including the Pages service, is to use the 
[Fabric Model Architecture](https://www.nginx.com/blog/microservices-reference-architecture-nginx-fabric-model/ "Fabric Model").
Instructions for using the [Router Mesh](https://www.nginx.com/blog/microservices-reference-architecture-nginx-router-mesh-model/) or 
[Proxy Model](https://www.nginx.com/blog/microservices-reference-architecture-nginx-proxy-model/) architectures will be made available in the future.

## Quick start
As a single service in the set of services which make up the NGINX Microservices Reference Architecture application, _Ingenious_,
the Auth Proxy service is not meant to function as a standalone service.

There are detailed instructions about the service below, and in order to get started quickly, you can follow these simple 
instructions to quickly build the image. 

0. (Optional) If you don't already have an NGINX Plus license, you can request a temporary developer license 
[here](https://www.nginx.com/developer-license/ "Developer License Form"). If you do have a license, then skip to the next step. 
1. Copy your licenses to the **<repository-path>/auth-proxy/nginx/ssl** directory
2. Run the command ```docker build . -t <your-image-repo-name>/auth-proxy:quickstart``` where <image-repository-name> is the username
for where you store your Docker images
3. Once the image has been built, push it to the docker repository with the command ```docker push -t <your-image-repo-name>/auth-proxy:quickstart```

At this point, you will have an image that is suitable for deployment on to a DC/OS installation, and you can deploy the
image by creating a JSON file and uploading it to your DC/OS installation.

To build customized images for different container engines and set other options, please follow the directions below.

## Building a Customized Image
The Dockerfile for the Auth Proxy service is based on the ubuntu:16.04 image, and installs Python, PIP, and NGINX open source or NGINX Plus. Note that the features
in NGINX Plus make discovery of other services possible, include additional Load Balancing algorithms, persistent SSL/TLS connections, and
advanced health check functionality.

The command, or entrypoint, for the Dockerfile is the [oauth-start.sh script](app/oauth-start.sh "Dockerfile entrypoint"). 
This script sets some local variables, then starts [oauth-daemon.py](app/oauth-start.sh "Oauth Python") and NGINX in order to handle page requests.

### 1. Build options
The Dockerfile sets some ENV arguments which are used when the image is built:

- **USE_NGINX_PLUS**  
    The default value is true. Set this environment variable to true when you want to use NGINX Plus. When this value is false, 
    NGINX open source will be used, and it lacks support for features like service discovery, advanced load balancing,
    and health checks. See [installing nginx plus](#installing-nginx-plus)
    
    When this value is set to false, NGINX open source will be built in to the image and several features, including service
    discovery and advanced load balancing will be disabled.
    
    When the nginx.conf file is built, the [fabric_config_local.yaml](nginx/fabric_config_local.yaml) will be
    used to populate the open source version of the [nginx.conf template](nginx/nginx-fabric.conf.j2)
    
- **USE_VAULT**  
    The default value is false. The installation script uses [vault](https://www.vaultproject.io/) to retrieve the keys necessary to install NGINX Plus.
    Setting this value to true will cause install-nginx.sh to look for a file named vault_env.sh which contains the _VAULT_ADDR_ and _VAULT_TOKEN_
    environment variables.        
    
    ```
    #!/bin/bash
    export VAULT_ADDR=<your-vault-address>
    export VAULT_TOKEN=<your-vault-token>
    ```
    
    You must be certain to include the vault_env.sh file when _USE_VAULT_ is true. There is an entry in the .gitignore
    file for vault_env.sh
    
    In the future, we will release an article on our [blog](https://www.nginx.com/blog/) describing how to use vault with NGINX.
    
- **CONTAINER_ENGINE**  
The container engine used to run the images. It can be one of the following values, and the default is _mesos_. A detailed
description of each of the files is in a [separate README file](nginx/README.md)
     - docker: to run on Docker Cloud 
     
        When the nginx.conf file is built, the [fabric_config_docker.yaml](nginx/fabric_config_docker.yaml) will be
        used to populate the open source version of the [nginx.conf template](nginx/nginx-plus-fabric.conf.j2)
        
     - kubernetes: to run on Kubernetes
     
        When the nginx.conf file is built, the [fabric_config_k8s.yaml](nginx/fabric_config_k8s.yaml) will be
        used to populate the open source version of the [nginx.conf template](nginx/nginx-plus-fabric.conf.j2)
             
     - mesos (default): to run on DC/OS
     
        When the nginx.conf file is built, the [fabric_config.yaml](nginx/fabric_config.yaml) will be
        used to populate the open source version of the [nginx.conf template](nginx/nginx-plus-fabric.conf.j2)
                  
     - local: to run in containers on the machine where the repository has been cloned
     
        When the nginx.conf file is built, the [fabric_config_local.yaml](nginx/fabric_config_local.yaml) will be
        used to populate the open source version of the [nginx.conf template](nginx/nginx-plus-fabric.conf.j2)                  
     
### 2. Decide whether to use NGINX Open Source or NGINX Plus
 
#### <a href="#" id="installing-nginx-oss"></a>Installing NGINX Open Source

Set the _USE_NGINX_PLUS_ property to false in the Dockerfile
    
#### <a href="#" id="installing-nginx-plus"></a>Installing NGINX Plus
Before installing NGINX Plus, you'll need to obtain your license keys. If you do not already have a valid NGINX Plus subscription, you can request 
developer licenses [here](https://www.nginx.com/developer-license/ "Developer License Form") 

Set the _USE_NGINX_PLUS_ property to true in the Dockerfile

If you have not set _USE_VAULT_ to true, then you'll need to manually copy your **nginx-repo.crt** and **nginx-repo.key** files to the _<path-to-repository>/ngra-pages/nginx/ssl/_ directory. 

Download the **nginx-repo.crt** and **nginx-repo.key** files for your NGINX Plus Developer License or subscription, and move them to the root directory of this project. You can then copy both of these files to the `/etc/nginx/ssl` directory of each microservice using the commands below:
```
cp nginx-repo.crt nginx-repo.key <path-to-repository>/auth-proxy/nginx/ssl/
```

### 3. Decide which container engine to use

#### Set the _CONTAINER_ENGINE_ variable
As described above, the _CONTAINER_ENGINE_ environment variable must be set to one of the following four options.
The install-nginx.sh file uses this value to determine which template file to use when populating the nginx.conf file.

- docker 
- kubernetes 
- mesos 
- local

### 4. Build the image

Replace _&lt;your-image-repo-name&gt;_ and execute the command below to build the image. The _&lt;tag&gt;_ argument is optional and defaults to **latest**

```
docker build . -t <your-image-repo-name>/auth-proxy:<tag>
```

### Runtime environment variables
In order to run the image, some environment variables must be set so that they are available during runtime.

| Variable Name | Description | Example Value |
| ------------- | ----------- | ----------- |
| REDIS_HOST    | The host name of the redis database | redis.localhost |
| REDIS_ENABLED | Specifies whether the redis database is enabled, valid values are 0 or 1 | 1 |
| REDIS_PORT    | The port on which redis listens | 6359 |
| REDIS_TTL     | The redis timeout in seconds | 300 |
| AWS_ACCESS_KEY_ID | The AWS access key ID for the associated S3 account | Refer to your AWS account |
| AWS_SECRET_ACCESS_KEY | The AWS secret access key for the associated S3 account| Refer to AWS account |
| PAGES_URL     | The host name of the pages application | pages.localhost |
| AWS_REGION    | The region of the AWS application | us-west-1 |
 