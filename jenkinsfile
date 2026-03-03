pipeline {
    agent any

    tools {
        maven 'maven'
    }

    environment {
        FLASK_APP = "flask_demo/app.py"
        PYTHON = 'python3'
    }

    stages {

        stage('Checkout') {
            steps {
                git url: 'https://gitlab.com/changliang23/frameworks_convert.git', branch: 'main'
            }
        }

        stage('Start Flask') {
            steps {
                sh '''
                cd flask_demo
                nohup python app.py > flask.log 2>&1 &
                sleep 5
                '''
            }
        }

        stage('Run Python Tests') {
            steps {
                sh '''
                pytest -v
                '''
            }
        }

        stage('Run Java Tests') {
            steps {
                sh '''
                mvn clean test
                '''
            }
        }
    }

    post {
        always {
            sh 'pkill -f app.py || true'
            archiveArtifacts artifacts: '**/target/surefire-reports/*.xml', allowEmptyArchive: true
            junit '**/target/surefire-reports/*.xml'
        }
        failure {
            echo "❌ Tests failed"
        }
        success {
            echo "✅ All tests passed"
        }
    }
}