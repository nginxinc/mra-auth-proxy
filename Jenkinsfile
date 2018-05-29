#!groovy
pipeline {
// agent needs to build go, so start with golang:1.10-alpine
    agent { docker { image 'jnonino/jenkins-python-slave' }  }
    environment {
        NG_BRANCH = env.BRANCH_NAME.toLowerCase()
        TOKEN_RO=credentials('creds-dev-ro')
    }
    options { disableConcurrentBuilds() }
    stages {

        stage ('BuildImage') {
            steps {
            // this is the list of commands that will be run in the agent
              sh '''
                echo "Building ${NG_BRANCH} Number ${BUILD_NUMBER} - home: ${HOME}"
                echo "get the NGINX Plus keys"
                curl -k -sS -H "X-Vault-Token:${TOKEN_RO}" ${VAULT_CREDS_PATH}/nginx-repo.key | jq -r .data.key > nginx/ssl/nginx-repo.key
                curl -k -sS -H "X-Vault-Token:${TOKEN_RO}" ${VAULT_CREDS_PATH}/nginx-repo.crt | jq -r .data.cert > nginx/ssl/nginx-repo.crt
                echo "tagging images with:${REGISTRY_HOST}/mra/ngrefarch/mra-auth-proxy/${NG_BRANCH}"
                docker build -t ${REGISTRY_HOST}/mra/ngrefarch/mra-auth-proxy/${NG_BRANCH}/mra-auth-proxy:${BUILD_NUMBER} .
                docker push ${REGISTRY_HOST}/mra/ngrefarch/mra-auth-proxy/${NG_BRANCH}/mra-auth-proxy:${BUILD_NUMBER}
                docker rmi $(docker images -f "dangling=true" -q) || true
              '''
        }
      }

   }
    post {
        always {
            print "Post operations"
        }
        success {
            print "SUCCESSFUL build ${env.JOB_NAME} [${env.BUILD_NUMBER}] (${env.BUILD_URL})"
          script {
            if (currentBuild.getPreviousBuild() &&
              currentBuild.getPreviousBuild().getResult().toString() != "SUCCESS") {
                emailext body: "Auth Proxy Recovery: ${env.BUILD_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "BUILD ERROR:${env.BRANCH_NAME}"
            }
          }
        }
        failure {
            emailext body: "Auth Proxy Error on: ${env.BUILD_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "BUILD ERROR:${env.BRANCH_NAME}"
        }
        unstable {
            print "UNSTABLE JOB build ${env.JOB_NAME} [${env.BUILD_NUMBER}] (${env.BUILD_URL})"
        }
    }
}