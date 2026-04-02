pipeline {
    agent any

    environment {
        REGISTRY = "myacr123.azurecr.io"
        IMAGE_NAME = "backend"
        EMAIL = "developer@gmail.com"
    }

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/3-tier-app.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('backend') {
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir('backend') {
                    sh 'pytest'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $REGISTRY/$IMAGE_NAME:latest backend/'
            }
        }

        // ✅ This runs ONLY if above stages SUCCESS
        stage('Push to ACR') {
            steps {
                sh '''
                az acr login --name myacr123
                docker push $REGISTRY/$IMAGE_NAME:latest
                '''
            }
        }
    }

    post {
        success {
            mail to: "${EMAIL}",
                 subject: "SUCCESS: Image pushed to ACR",
                 body: "Build successful. Docker image pushed to ACR."
        }

        failure {
            mail to: "${EMAIL}",
                 subject: "FAILED: Build Error",
                 body: "Build or test failed. Image NOT pushed to ACR."
        }
    }
}
