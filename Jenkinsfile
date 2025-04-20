pipeline {
    agent any

    environment {
        // Server
        HOST = credentials('HOST')
        PORT = credentials('PORT')
        OPENAI_API_KEY = credentials('OPENAI_API_KEY')
        MODEL_NAME = credentials('MODEL_NAME')
        EMBEDDING_MODEL_NAME = credentials('EMBEDDING_MODEL_NAME')
        MAPBOX_API_KEY = credentials('MAPBOX_API_KEY')

        // Elasticsearch
        ELASTIC_USERNAME = credentials('ELASTIC_USERNAME')
        ELASTIC_PASSWORD = credentials('ELASTIC_PASSWORD')
        ES_HOST = credentials('ES_HOST')
        ES_PORT = credentials('ES_PORT')
    }

    stages {
        stage('Remove Old Docker Image') {
            steps {
                script {
                    // Stop and remove the old container if it exists
                    sh 'docker stop travel-core-container || true'
                    sh 'docker rm travel-core-container || true'

                    // Remove the old image
                    sh 'docker rmi $(docker images -q travel-core) || true'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the new Docker image
                    sh 'docker build -t travel-core .'
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Run the newly built container with environment variables
                    sh '''
                        docker run -d \
                            --restart unless-stopped \
                            --name travel-core-container \
                            -p ${PORT}:${PORT} \
                            -e HOST="$HOST" \
                            -e PORT="$PORT" \
                            -e OPENAI_API_KEY="$OPENAI_API_KEY" \
                            -e MODEL_NAME="$MODEL_NAME" \
                            -e EMBEDDING_MODEL_NAME="$EMBEDDING_MODEL_NAME" \
                            -e MAPBOX_API_KEY="$MAPBOX_API_KEY" \
                            -e ELASTIC_USERNAME="$ELASTIC_USERNAME" \
                            -e ELASTIC_PASSWORD="$ELASTIC_PASSWORD" \
                            -e ES_HOST="$ES_HOST" \
                            -e ES_PORT="$ES_PORT" \
                            travel-core
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully'
            cleanWs()
        }
        failure {
            echo 'Pipeline failed'
            script {
                sh 'docker stop travel-core-container || true'
                sh 'docker rm travel-core-container || true'
                cleanWs()
            }
        }
        always {
            echo 'Pipeline completed'
            cleanWs()
        }
    }
}
