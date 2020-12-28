include(ExternalProject)

message(STATUS "Using Meuphonic and Brillem in ExternalProject")

ExternalProject_Add(meuphonic
    GIT_REPOSITORY https://github.com/mducle/horace-euphonic-interface.git
    GIT_TAG eb2f29705feb895b188944f5758f1ead850e4c97
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ""
)

ExternalProject_Add(brillem
    GIT_REPOSITORY https://github.com/mducle/brillem.git
    GIT_TAG 059b839221cafe3a18b92ec001bf66a397d4b14c
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ""
)

ExternalProject_Add(spinw_brille
    GIT_REPOSITORY https://github.com/mducle/spinw.git
    GIT_TAG 673c7b1241f73f20e733933e430466ca65702ab0
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ""
)

ExternalProject_Get_property(meuphonic SOURCE_DIR)
add_custom_target(add_euphonic ALL)
if(WIN32)
    add_custom_command(
        TARGET add_euphonic PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/euphonic_wrapper.py" -Destination "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
    )
else()
    add_custom_command(
        TARGET add_euphonic PRE_BUILD
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/euphonic_wrapper.py" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
    )
endif()
add_dependencies(add_euphonic meuphonic)

ExternalProject_Get_property(brillem SOURCE_DIR)
add_custom_target(add_brillem ALL)
if(WIN32)
    add_custom_command(
        TARGET add_brillem PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/brillem.py" -Destination "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace/brille_wrapper.py"
    )
else()
    add_custom_command(
        TARGET add_brillem PRE_BUILD
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/brillem.py" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace/brille_wrapper.py"
    )
endif()
add_dependencies(add_brillem brillem)

ExternalProject_Get_property(spinw_brille SOURCE_DIR)
add_custom_target(add_spinw_brille ALL)
if(WIN32)
    add_custom_command(
        TARGET add_spinw_brille PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/swfiles/sw_readparam.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp"
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/swfiles/@spinw/brille_init.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/swfiles/@spinw/spinwave.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${SOURCE_DIR}/swfiles/@spinw/spinw.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
    )
else()
    add_custom_command(
        TARGET add_spinw_brille PRE_BUILD
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp"
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/swfiles/sw_readparam.m" "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp"
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/swfiles/@spinw/brille_init.m" "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/swfiles/@spinw/spinwave.m" "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
        COMMAND ${BASH_COMMAND} cp "${SOURCE_DIR}/swfiles/@spinw/spinw.m" "${CMAKE_CURRENT_BINARY_DIR}/src/sw_tmp/sw"
    )
endif()
add_dependencies(add_spinw_brille spinw_brille)
