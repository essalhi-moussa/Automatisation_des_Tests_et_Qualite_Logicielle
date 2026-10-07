// Pipeline Jenkins declaratif equivalent a .gitlab-ci.yml (alternative locale).
// Prerequis Jenkins : plugins Pipeline, Allure Jenkins Plugin, JUnit, Email Extension (emailext), NodeJS (optionnel).
// Outils attendus : Maven 3.9 et JDK 17 declares dans "Global Tool Configuration" (noms ci-dessous),
// Chrome installe sur l agent, newman et newman-reporter-htmlextra disponibles (npm i -g ...).
pipeline {
    agent any

    tools {
        maven 'Maven-3.9'
        jdk 'JDK-17'
    }

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    }

    parameters {
        string(name: 'API_BASE_URL', defaultValue: 'https://reqres.in', description: 'URL de l API (mock local : http://localhost:3999)')
        booleanParam(name: 'RUN_PERF', defaultValue: false, description: 'Executer le test de charge JMeter')
        booleanParam(name: 'RUN_ZAP', defaultValue: false, description: 'Executer le scan OWASP ZAP (Docker requis)')
    }

    environment {
        // Pour une cle API personnalisee : definir la variable d environnement REQRES_API_KEY (Credentials > withCredentials)
        MAVEN_CLI = '-B -ntp'
    }

    stages {
        stage('Build') {
            steps {
                sh 'mvn $MAVEN_CLI -DskipTests test-compile'
            }
        }

        stage('Tests API') {
            parallel {
                stage('RestAssured') {
                    steps {
                        sh 'mvn $MAVEN_CLI -P api test -Dapi.base.url=${API_BASE_URL}'
                    }
                    post {
                        always { junit allowEmptyResults: true, testResults: 'target/surefire-reports/TEST-*.xml' }
                    }
                }
                stage('Newman') {
                    steps {
                        sh '''
                            mkdir -p reports/api/newman
                            newman run postman/Reqres.postman_collection.json \
                              -e postman/reqres-public.postman_environment.json \
                              --env-var "baseUrl=${API_BASE_URL}" \
                              -r cli,htmlextra,junit \
                              --reporter-htmlextra-export reports/api/newman/rapport-newman.html \
                              --reporter-junit-export reports/api/newman/newman-junit.xml
                        '''
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'reports/api/newman/newman-junit.xml'
                            publishHTML(target: [reportDir: 'reports/api/newman', reportFiles: 'rapport-newman.html',
                                                 reportName: 'Rapport Newman', keepAll: true, allowMissing: true,
                                                 alwaysLinkToLastBuild: true])
                        }
                    }
                }
            }
        }

        stage('Tests UI (Selenium)') {
            steps {
                sh 'mvn $MAVEN_CLI -P ui test -Dheadless=true'
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'target/surefire-reports/TEST-*.xml' }
            }
        }

        stage('Performance (JMeter)') {
            when { expression { params.RUN_PERF } }
            steps {
                sh 'bash scripts/run-jmeter.sh jenkins'
            }
            post {
                always { archiveArtifacts artifacts: 'reports/perf/jenkins/**', allowEmptyArchive: true }
            }
        }

        stage('Securite (ZAP)') {
            when { expression { params.RUN_ZAP } }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'bash scripts/zap-scan.sh'
                }
            }
            post {
                always { archiveArtifacts artifacts: 'reports/security/**', allowEmptyArchive: true }
            }
        }
    }

    post {
        always {
            // Plugin Allure : genere et publie le rapport a partir de target/allure-results
            allure includeProperties: false, jdk: '', results: [[path: 'target/allure-results']]
            archiveArtifacts artifacts: 'target/surefire-reports/**, reports/**', allowEmptyArchive: true
        }
        success {
            emailext(
                to: '${DEFAULT_RECIPIENTS}',
                subject: "[SUCCES] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Pipeline reussi.\nDetails : ${env.BUILD_URL}\nRapport Allure : ${env.BUILD_URL}allure/"
            )
        }
        failure {
            emailext(
                to: '${DEFAULT_RECIPIENTS}',
                subject: "[ECHEC] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Pipeline en echec.\nJournal : ${env.BUILD_URL}console\nRapport Allure : ${env.BUILD_URL}allure/",
                attachLog: true
            )
        }
    }
}
