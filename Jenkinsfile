#!groovy

properties([
  parameters([
    string(
      name: 'Agent',
      defaultValue: 'rocky8',
      description: 'Agent to run the build on.',
      trim: true
    ),
    string(
      name: 'PYTHON_VERSION',
      defaultValue: '3.8',
      description: 'Version of python to run the build with.',
      trim: true
    ),
    string(
      name: 'MATLAB_VERSION',
      defaultValue: '2020b',
      description: 'Version of Matlab to run the build with.',
      trim: true
    )
  ])
])

def get_agent(String jobname) {
  if (jobname.contains('linux')) {
    return "rocky8"
  } else if (jobname.contains('windows')) {
     
    return "icdpacewin"
    
  } else {
    return ''
  }
}

def get_github_token() {
  withCredentials([string(credentialsId: 'pace_python_release', variable: 'github_token')]) {
    return "${github_token}"
  }
}

def setGitHubBuildStatus(String status, String message) {
    script {
        withCredentials([string(credentialsId: 'PacePython_API_Token',
                variable: 'api_token')]) {
          if (isUnix()) {
            sh """
                curl -H "Authorization: token ${api_token}" \
                --request POST \
                --data '{ \
                    "state": "${status}", \
                    "description": "${message} on ${env.JOB_BASE_NAME}", \
                    "target_url": "$BUILD_URL", \
                    "context": "${env.JOB_BASE_NAME}" \
                }' \
                https://api.github.com/repos/pace-neutrons/pace-python/statuses/${env.GIT_COMMIT}
            """
          }
          else {
            return powershell(
            script: """
                \$body = @"
                  {
                    "state": "${status}",
                    "description": "${message} on ${env.JOB_BASE_NAME}",
                    "target_url": "$BUILD_URL",
                    "context": "${env.JOB_BASE_NAME}"
                  }
"@
                [Net.ServicePointManager]::SecurityProtocol = "tls12, tls11, tls"
                Invoke-RestMethod -URI "https://api.github.com/repos/pace-neutrons/pace-python/statuses/${env.GIT_COMMIT}" \
                    -Headers @{Authorization = "token ${api_token}"} \
                    -Method 'POST' \
                    -ContentType "application/json" \
                    -Body \$body
            """,
            returnStdout: true
            )
          }
        }
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
                module purge
                module load matlab/\$MATLAB_VERSION
                module load cmake
                module load conda
                module load gcc
                conda create -n py37 -c conda-forge python=\$PYTHON_VERSION -y
                conda activate py37
                conda install -c conda-forge setuptools
                python setup.py bdist_wheel
            '''
            archiveArtifacts artifacts: 'dist/*whl'
          }
          else {
            powershell ''' 
                conda create -n py37 -c conda-forge python=\$env:PYTHON_VERSION -y
                conda activate py37
                conda install -c conda-forge setuptools
                python setup.py bdist_wheel -DMatlab_ROOT_DIR=/opt/modules-common/software/MATLAB/R\$env:MATLAB_VERSION
            '''
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
      environment {
        LD_LIBRARY_PATH = "/opt/modules-common/software/MATLAB/R2020b/runtime/glnxa64:/opt/modules-common/software/MATLAB/R2020b/bin/glnxa64"
        LD_PRELOAD = "/opt/modules-common/software/MATLAB/R2020b/sys/os/glnxa64/libiomp5.so"
      }
      steps {
        script {
          if (isUnix()) {
            sh '''
                module purge
                module load conda
                module load matlab/\$MATLAB_VERSION
                eval "$(/opt/conda/bin/conda shell.bash hook)"
                conda env remove -n py37
                conda create -n py37 -c conda-forge python=\$PYTHON_VERSION -y
                conda activate py37
                conda install -c conda-forge scipy euphonic -y
                python -m pip install brille
                python -m pip install $(find dist -name "*whl"|tail -n1)
                python test/run_test.py -v || true
                test -f success
            '''
          }
          else {
            powershell '''
                conda env remove -n py37
                conda create -n py37 -c conda-forge python=\$env:PYTHON_VERSION -y
                conda activate py37
                conda install -c conda-forge scipy euphonic -y
                python -m pip install brille
                python -m pip install ./dist/*.whl
                python test/run_test.py -v
            '''
          }
        }
      }
    }

    // stage("Push release") {
    //   environment {
    //     GITHUB_TOKEN = get_github_token()
    //   }
    //   steps {
    //     script {
    //       if (env.ref_type == 'tag') {
    //         if (isUnix()) {
    //           sh '''
    //             podman run -v `pwd`:/mnt localhost/pace_python_builder /mnt/installer/jenkins_compiler_installer.sh
    //             eval "$(/opt/conda/bin/conda shell.bash hook)"
    //             conda activate py37
    //             pip install requests pyyaml
    //             python release.py --github --notest
    //           '''
    //         } else {
    //           powershell './cmake/run_release.ps1'
    //         }
    //       }
    //     }
    //   }
    // }

  }

  post {

    success {
        script {
          setGitHubBuildStatus("success", "Successful")
        }
    }

    unsuccessful {
      withCredentials([string(credentialsId: 'pace_python_email', variable: 'pace_python_email')]) {
        script {
            //mail (
            //  to: "${pace_python_email}",
            //  subject: "PACE-Python pipeline failed: ${env.JOB_BASE_NAME}",
            //  body: "See ${env.BUILD_URL}"
            //)
            setGitHubBuildStatus("failure", "Unsuccessful")
        }
      }
    }

    cleanup {
      deleteDir()
    }

  }
}
