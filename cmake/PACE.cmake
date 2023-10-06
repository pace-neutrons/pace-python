include(Download)

message(STATUS "Downloading PACE")

download(
    PROJ SPINW
    GIT_REPOSITORY https://github.com/${SPINW_REPO}.git
    GIT_TAG ${SPINW_VERSION}
    GIT_SHALLOW 1
)

if(WIN32)
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-win64-R2019b.zip
    )
else()
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-linux-R2019b.tar.gz
    )
endif()
