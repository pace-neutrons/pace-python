#!groovy

def get_agent(String jobname) {
  if (jobname.contains('linux')) {
    return "rocky8"
  } else if (jobname.contains('windows')) {
     
    return "icdpacewin"
    
  } else {
    return ''
  }
}

// def get_github_token() {
//   withCredentials([string(credentialsId: 'pace_python_release', variable: 'github_token')]) {
//     return "${github_token}"
//   }
// }

// def setGitHubBuildStatus(String status, String message) {
//     script {
//         withCredentials([string(credentialsId: 'PacePython_API_Token',
//                 variable: 'api_token')]) {
//           if (isUnix()) {
//             sh """
//                 curl -H "Authorization: token ${api_token}" \
//                 --request POST \
//                 --data '{ \
//                     "state": "${status}", \
//                     "description": "${message} on ${env.JOB_BASE_NAME}", \
//                     "target_url": "$BUILD_URL", \
//                     "context": "${env.JOB_BASE_NAME}" \
//                 }' \
//                 https://api.github.com/repos/pace-neutrons/pace-python/statuses/${env.GIT_COMMIT}
//             """
//           }
//           else {
//             return powershell(
//             script: """
//                 \$body = @"
//                   {
//                     "state": "${status}",
//                     "description": "${message} on ${env.JOB_BASE_NAME}",
//                     "target_url": "$BUILD_URL",
//                     "context": "${env.JOB_BASE_NAME}"
//                   }
// "@
//                 [Net.ServicePointManager]::SecurityProtocol = "tls12, tls11, tls"
//                 Invoke-RestMethod -URI "https://api.github.com/repos/pace-neutrons/pace-python/statuses/${env.GIT_COMMIT}" \
//                     -Headers @{Authorization = "token ${api_token}"} \
//                     -Method 'POST' \
//                     -ContentType "application/json" \
//                     -Body \$body
//             """,
//             returnStdout: true
//             )
//           }
//         }
//     }
// }

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
                module load matlab/2020b
                module load cmake
                module load conda
                conda create -n py37 -c conda-forge python=3.7 -y
                conda activate py37
                conda install -c conda-forge setuptools
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
      // environment {
      //   LD_LIBRARY_PATH = "/usr/local/MATLAB/MATLAB_Runtime/v98/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v98/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v98/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v98/extern/bin/glnxa64"
      //   LD_PRELOAD = "/usr/local/MATLAB/MATLAB_Runtime/v98/sys/os/glnxa64/libiomp5.so"
      // }
      steps {
        script {
          if (isUnix()) {
            sh '''
                module load conda
                module load matlab
                eval "$(/opt/conda/bin/conda shell.bash hook)"
                conda env remove -n py37
                conda create -n py37 -c conda-forge python=3.7 -y
                conda activate py37
                conda install -c conda-forge scipy euphonic -y
                python -m pip install brille
                python -m pip install $(find dist -name "*cp37*whl"|tail -n1)
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

    // success {
    //     script {
    //       setGitHubBuildStatus("success", "Successful")
    //     }
    // }

    // unsuccessful {
    //   withCredentials([string(credentialsId: 'pace_python_email', variable: 'pace_python_email')]) {
    //     script {
    //         //mail (
    //         //  to: "${pace_python_email}",
    //         //  subject: "PACE-Python pipeline failed: ${env.JOB_BASE_NAME}",
    //         //  body: "See ${env.BUILD_URL}"
    //         //)
    //         setGitHubBuildStatus("failure", "Unsuccessful")
    //     }
    //   }
    // }

    cleanup {
      deleteDir()
    }

  }
}
