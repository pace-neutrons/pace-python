include(Download)

message(STATUS "Downloading PACE")

download(
    PROJ SPINW
    GIT_REPOSITORY https://github.com/mducle/spinw.git
    GIT_TAG e3e57aae432f6737aff81d31ccda6e7dce741cef
    GIT_SHALLOW 1
)

if(WIN32)
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v3.5.2/Horace-3.5.2-win64-R2019b.zip
    )
else()
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v3.5.2/Horace-3.5.2-linux-R2019b.tar.gz
    )
endif()
