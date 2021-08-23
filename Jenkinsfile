#!groovy

def get_agent(String jobname) {
  if (jobname.contains('linux')) {
    withCredentials([string(credentialsId: 'sl7_agent', variable: 'agent')]) {
      return "${agent}"
    }
  } else if (jobname.contains('windows')) {
    withCredentials([string(credentialsId: 'win10_agent', variable: 'agent')]) {
      return "${agent}"
    }
  } else {
    return ''
  }
}

pipeline {

  agent {
    label get_agent(env.JOB_BASE_NAME)
  }

  stages {
    stage("Build-Pace-Python") {
      steps {
        script {
          if (isUnix()) {
            sh '''
                module load conda/3 &&
                module load gcc &&
                module load cmake &&
                conda create --name pace_python -c conda-forge python=3.7 -y
                conda activate pace_python &&
                python -m pip install --upgrade pip &&
                python -m pip install numpy scipy matplotlib &&
                python -m pip install euphonic brille
                module load matlab
                python setup.py bdist_wheel
            '''
            archiveArtifacts artifacts: 'dist/*whl'
          }
          else {
            powershell './cmake/build_pace_python.ps1'
            archiveArtifacts artifacts: 'dist/*whl'
          }
        }
      }
    }

    stage("Get-Pace-Python-Demo") {
      steps {
        dir('demo') {
          checkout([
            $class: 'GitSCM',
            branches: [[name: "refs/heads/main"]],
            extensions: [[$class: 'WipeWorkspace']],
            userRemoteConfigs: [[url: 'https://github.com/pace-neutrons/pace-python-demo']]
          ])
        }
      }
    }

    stage("Run-Pace-Python-Tests") {
      steps {
        script {
          if (isUnix()) {
            sh '''
                module load conda/3 &&
                conda activate pace_python &&
                python -m pip install $(find dist -name "*whl"|tail -n1) &&
                export LD_LIBRARY_PATH=/opt/software/matlab/R2019b/runtime/glnxa64:/opt/software/matlab/R2019b/bin/glnxa64:/opt/software/matlab/R2019b/sys/os:/opt/software/matlab/R2019b/extern/bin/glnxa64:$LD_LIBRARY_PATH &&
                python test/run_test.py
            '''
          }
          else {
            powershell './cmake/run_pace_python_tests.ps1'
          }
        }
      }
    }
  }

  post {
    always {
      script {
        if (!isUnix()) {
          bat '''
            CALL conda remove -n pace_python --all -y
          '''
        }
      }
    }

    unsuccessful {
      withCredentials([string(credentialsId: 'pace_python_email', variable: 'pace_python_email')]) {
        script {
            mail (
              to: "${pace_python_email}",
              subject: "PACE-Python pipeline failed: ${env.JOB_BASE_NAME}",
              body: "See ${env.BUILD_URL}"
            )
        }
      }
    }

    cleanup {
      deleteDir()
    }

  }
}
