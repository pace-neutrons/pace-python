#!groovy

def get_agent(String jobname) {
  if (jobname.contains('linux')) {
    withCredentials([string(credentialsId: 'manylinux_agent', variable: 'agent')]) {
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
                podman run -v `pwd`:/mnt localhost/pace_python_builder /mnt/manylinux/jenkins_build_script.sh
            '''
            archiveArtifacts artifacts: 'wheelhouse/*whl'
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
                eval "$(/opt/conda/bin/conda shell.bash hook)"
                conda env remove -n py37
                conda create -n py37 -c conda-forge python=3.7 -y
                conda activate py37
                conda install -c conda-forge scipy euphonic -y
                python -m pip install brille
                python -m pip install $(find -name "*cp37*whl"|tail -n1)
                export LD_LIBRARY_PATH=/usr/local/MATLAB/MATLAB_Runtime/v98/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v98/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v98/sys/os:/usr/local/MATLAB/MATLAB_Runtime/v98/extern/bin/glnxa64:$LD_LIBRARY_PATH
                export LD_PRELOAD=/usr/local/MATLAB/MATLAB_Runtime/v98/sys/os/glnxa64/libiomp5.so
                python test/run_test.py || true
                test -f success
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
