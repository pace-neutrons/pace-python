include(Download)

message(STATUS "Downloading PACE")

download(
    PROJ SPINW
    GIT_REPOSITORY https://github.com/mducle/spinw.git
    GIT_TAG b0c3e8670a1513d8655605fa3f80ea182cfebcb8
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
