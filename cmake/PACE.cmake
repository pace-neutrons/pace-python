include(Download)

message(STATUS "Downloading PACE")

download(
    PROJ MEUPHONIC
    GIT_REPOSITORY https://github.com/mducle/horace-euphonic-interface.git
    GIT_TAG eb2f29705feb895b188944f5758f1ead850e4c97
)

download(
    PROJ BRILLEM
    GIT_REPOSITORY https://github.com/mducle/brillem.git
    GIT_TAG 059b839221cafe3a18b92ec001bf66a397d4b14c
)

download(
    PROJ SPINW
    GIT_REPOSITORY https://github.com/mducle/spinw.git
    GIT_TAG 673c7b1241f73f20e733933e430466ca65702ab0
)

if(WIN32)
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v3.5.0/Horace-3.5.0-win64-R2019b.zip
    )
else()
    download(
        PROJ HORACE
        URL https://github.com/pace-neutrons/Horace/releases/download/v3.5.0/Horace-3.5.0-linux-R2019b.tar.gz
    )
endif()
    
add_custom_target(add_euphonic ALL)
if(WIN32)
    add_custom_command(
        TARGET add_euphonic PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${MEUPHONIC_BINARY_DIR}/euphonic_wrapper.py" -Destination "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
    )
else()
    add_custom_command(
        TARGET add_euphonic PRE_BUILD
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
        COMMAND ${BASH_COMMAND} cp "${MEUPHONIC_BINARY_DIR}/euphonic_wrapper.py" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
    )
endif()

add_custom_target(add_brillem ALL)
if(WIN32)
    add_custom_command(
        TARGET add_brillem PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${BRILLEM_BINARY_DIR}/brillem.py" -Destination "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python/brille_wrapper.py"
    )
else()
    add_custom_command(
        TARGET add_brillem PRE_BUILD
        COMMAND ${BASH_COMMAND} cp "${BRILLEM_BINARY_DIR}/brillem.py" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python/brille_wrapper.py"
    )
endif()
add_dependencies(add_brillem add_euphonic)
