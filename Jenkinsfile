/* groovylint-disable LineLength, NestedBlockDepth */
//Top level def for the whole pipeline

def findLatestPatch(String tagsOutput){
    def tagsArray = tagsOutput.split('\n')
    int maxPatch = 0
    String latestTag = ''
    String majorVersion = '1' // Assuming you will set this based on the branch name or another method

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
    return latestTag
}

def incrementPatch(String latestTag){
    if (latestTag) {
        def parts = latestTag.tokenize('.')
        int newPatchVersion = parts[2].toInteger() + 1
        newTagVersion = parts[0] + '.' + parts[1] + '.' + newPatchVersion
        println('New tag version: ' + newTagVersion)
        return newTagVersion
    } else {
        // Handle case where no existing tags match the majorVersion
        println("No existing tags found for the major version: ${majorVersion}. Starting at ${majorVersion}.0.1")
        newTagVersion = majorVersion + '.0.1'
        return newTagVersion
    }
}

pipeline {
    agent any

    environment {
        // Values from env file
        // ECR_LINK
        // REGION
        // IMAGE_NAME
        // CONTAINER_NAME
        // APP_REPO
        // GITOPS_REPO
        // Init empty values, used during pipeline
        OUTPUT_VERSION = ''
        newTagVersion = ''
    }

    stages {
        stage('Checkout Source') {
            steps {
                echo '++++++++++CHECKOUT SOURCE++++++++++'
                script {
                    checkout scm
                    sh """
                        echo "Push from branch - ${BRANCH_NAME}"
                        echo "The full tag = ${env.FULL_TAG}"
                    """
                }
            }
        }

        stage('Setup environment') {
            steps {
                echo '++++++++++ENV SETUP++++++++++'
                script {
                    echo 'Loading variables from .env.groovy'
                    load "$WORKSPACE/.env.groovy"
                    echo "ECR_LINK = ${env.ECR_LINK}"
                    echo "REGION = ${env.REGION}"
                    echo "IMAGE_NAME = ${env.IMAGE_NAME}"
                    echo "CONTAINER_NAME= ${env.CONTAINER_NAME}"
                    echo "APP_REPO = ${env.APP_REPO}"
                    echo "OUTPUT_VERSION = ${env.OUTPUT_VERSION}"
                    echo "newTagVersion = ${env.newTagVersion}"
                }
            }
        }

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
        stage('Unti Test') {
            steps {
                echo '++++++++++LOCAL UNIT TEST++++++++++'
                    // sh '''
                    // docker-compose up -d
                    // sleep 5
                    // docker run --rm --network frontend-network curlimages/curl:7.78.0 curl http://nginx:80
                    // '''
            }
        }

        stage('E2E Test') {
            // agent {
            //     docker {
            //         image 'bash'
            //         args '--network frontend-network'
            //     }
            // }
            // steps {
            //         echo 'Running tests with docker agent...'
            //         sh 'chmod +x ./e2e_test.sh'
            //         sh 'bash ./e2e_test.sh'
            // }
        }

        stage('Handle versioning') {
            steps {
                echo '++++++++++Handle new version++++++++++'
                script {
                    //Fetch and save tags
                    sh 'git fetch --tags'
                    String tagsOutput = sh(script: 'git tag', returnStdout: true).trim() 
                    //Get the one with the largest patch
                    latestTag = findLatestPatch(tagsOutput)
                     //patch++
                    newTagVersion = incrementPatch(latestTag)
                }
            }
        }

        stage('Push To ECR') {
            steps {
                echo '++++++++++PUSH ECR++++++++++'
                sh """
                    docker tag ${IMAGE_NAME}:pre-test "${ECR_LINK}/letsreview:${newTagVersion}"
                    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_LINK}
                    docker push ${ECR_LINK}/letsreview:${newTagVersion}
                """
            }
        }

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
                            valuesFilePath="./LetsReview-GitOps/charts/letsreview-chart/values.yaml"
                            valuesFileContent=\$(cat "\$valuesFilePath")
                            valuesFileContent=\$(echo "\$valuesFileContent" | sed "s/tag: [0-9]\\+\\.[0-9]\\+\\.[0-9]\\+/tag: ${newTagVersion}/g")
                            echo "\$valuesFileContent" > "\$valuesFilePath"
                            cd LetsReview-GitOps
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
            sh 'docker-compose down -v'
            deleteDir()
            cleanWs()
            sh "docker stop ${CONTAINER_NAME}"
        }
    }
}
