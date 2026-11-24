pipeline {
  agent any
  stages {
    stage('Archivos del proyecto') {
      steps {
        sh 'test -f compose.yaml'
        sh 'test -f db/init.sql'
        sh 'test -f nginx/default.conf'
        sh 'test -f .env.ejemplo'
      }
    }
    stage('Credenciales protegidas') {
      steps {
        sh 'grep -qx ".env" .gitignore'
        sh 'test ! -f .env'
      }
    }
    stage('Estructura de Compose') {
      steps {
        sh 'grep -Eq "^ +nginx:" compose.yaml'
        sh 'grep -Eq "^ +app:" compose.yaml'
        sh 'grep -Eq "^ +db:" compose.yaml'
        sh 'grep -q "healthcheck:" compose.yaml'
        sh 'grep -Eq "image: .*/inventario-app:[0-9]+[.][0-9]+" compose.yaml'
      }
    }
    stage('Historial en Git') {
      steps {
        sh 'git log --oneline -5'
      }
    }
    stage('Sistema disponible') {
      steps {
        sh 'curl -fsS http://nginx/salud'
      }
    }
    stage('Acceso protegido') {
      steps {
        sh 'test "$(curl -s -o /dev/null -w "%{http_code}" http://nginx/)" = "302"'
      }
    }
  }
}
