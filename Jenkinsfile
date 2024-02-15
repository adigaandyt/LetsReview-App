/* groovylint-disable NestedBlockDepth */
//Top level def for the whole pipeline

pipeline {
    agent any

    environment {
        ECR_LINK = '644435390668.dkr.ecr.eu-west-1.amazonaws.com'
        REGION = 'eu-west-1'
        OUTPUT_VERSION = ''
        IMAGE_NAME = 'ourlib-img'
        CONTAINER_NAME = 'ourlib-cont'
        newTagVersion = ''
        APP_REPO = 'git@github.com:adigaandyt/LetsReview.git'
        GITOPS_REPO = 'git@github.com:adigaandyt/ourlibrary_gitops.git'
    }

    stages {
        stage('Setup environment') {
            steps {
                echo '++++++++++ENV SETUP++++++++++'
                script {
                    if (BRANCH_NAME == 'main') { env.DEPLOY_PORT = '80' }
                    else if (BRANCH_NAME == 'staging') { env.DEPLOY_PORT = '3000' }
                    env.FULL_TAG = "${BRANCH_NAME}-${BUILD_NUMBER}"
                }
            }
        }

        stage('Checkout Source') {
            steps {
                echo '++++++++++CHECKOUT SOURCE++++++++++'
                script {
                    sh """
                        echo "Push from branch - ${BRANCH_NAME}"
                        echo "The full tag = ${env.FULL_TAG}"
                    """
                    checkout scm
                }
            }
        }

        //Build the image and give it a pre-test tag until it passes the tests
        //Also make sure containers aren't running from previous runs
        //I could make image name and container names as variables in the compose file but there's no need
        //TODO: MAKE IT WORK WITH DOCKER COMPOSE THERES
        //TODO: FIX THE NETWORK ISSUE WITH DOCKER COMPOSE
        //docker run --name ourlib-cont -d --rm -p 8000:8000 --network art-network ourlib-img:pre-test
        stage('Build') {
            steps {
                echo '++++++++++BUILD IMAGE++++++++++'
                script {
                    sh """
                        docker build --no-cache -t ${IMAGE_NAME}:pre-test ${WORKSPACE}
                    """
                }
            }
        }

        //Simple curl to test it's working
        stage('Local Test') {

            steps {
                echo '++++++++++LOCAL UNIT TEST++++++++++'
                retry(2) {
                    sh """
                    docker-compose up --env WORKSPACE_DIR=${WORKSPACE}
                    docker run --rm --network frontend-network curlimages/curl:7.78.0 curl http://nginx:80
                    docker-compose down
                """
                }
            }
        }

        //Test passed, push the image to ECR with the branch name as the version
        //TODO: add versioning along with the branch name
        //Using the amazon ECR plugin

        stage('Handle versioning') {
            steps {
                echo '++++++++++Handle new version++++++++++'
                script {
                    // Fetch tags and define initial variables
                    sh 'git fetch --tags'
                    String tagsOutput = sh(script: 'git tag', returnStdout: true).trim()
                    def tagsArray = tagsOutput.split('\n')
                    int maxPatch = 0
                    String latestTag = ''
                    String majorVersion = '' // Assuming you will set this based on the branch name or another method

                    // Find the highest patch version for the major version
                    tagsArray.each { tag ->
                        // Ensure the tag is relevant and follows semantic versioning
                        if (tag.startsWith(majorVersion)) {
                            def parts = tag.tokenize('.')
                            if (parts.size() == 3) {
                                int patchVersion = parts[2].toInteger()
                                if (patchVersion >= maxPatch) {
                                    maxPatch = patchVersion
                                    latestTag = tag
                                }
                            }
                        }
                    }

                    // Increment the patch version for the new tag
                    if (latestTag) {
                        def parts = latestTag.tokenize('.')
                        int newPatchVersion = parts[2].toInteger() + 1
                        newTagVersion = parts[0] + '.' + parts[1] + '.' + newPatchVersion
                        println('New tag version: ' + newTagVersion)
                    // Here, you can now use newTagVersion for further steps, like tagging the current commit
                    } else {
                        // Handle case where no existing tags match the majorVersion
                        println("No existing tags found for the major version: ${majorVersion}. Starting at ${majorVersion}.0.1")
                        newTagVersion = majorVersion + '.0.1'
                    // Use this newTagVersion as needed
                    }
                }
            }
        }

        stage('Push To ECR') {
            steps {
                echo '++++++++++PUSH ECR++++++++++'
                sh """
                    docker tag ${IMAGE_NAME}:pre-test "${ECR_LINK}/our_library:${newTagVersion}"
                    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_LINK}
                    docker push ${ECR_LINK}/our_library:${newTagVersion}
                """
            }
        }

        //TODO: Only increase tag when there's a git message saying so
        stage('Tag GIT') {
            steps {
                script {
                    echo '++++++++++Add Git Tag++++++++++'
                    sshagent(['jenkins-ssh']) {
                        sh """
                            git remote set-url origin ${APP_REPO}
                            git tag ${newTagVersion}
                            git push --tags
                        """
                    }
                }
            }
        }

        stage('GitOps Tag') {
            steps {
                script {
                    echo '++++++++++GitOps Tag++++++++++'
                    sshagent(['jenkins-ssh']) {
                        sh """
                            git clone ${GITOPS_REPO}
                            valuesFilePath="./ourlibrary_gitops/ourlibrary-chart/values.yaml"
                            valuesFileContent=\$(cat "\$valuesFilePath")
                            valuesFileContent=\$(echo "\$valuesFileContent" | sed "s/tag: [0-9]\\+\\.[0-9]\\+\\.[0-9]\\+/tag: ${newTagVersion}/g")
                            echo "\$valuesFileContent" > "\$valuesFilePath"
                            cd ourlibrary_gitops
                            git add .
                            git commit -m "Update Helm chart tag: ${newTagVersion}"
                            git push origin main
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            sh 'docker-compose down'
            deleteDir()
            cleanWs()
            sh "docker stop ${CONTAINER_NAME}"
        }
    }
}
