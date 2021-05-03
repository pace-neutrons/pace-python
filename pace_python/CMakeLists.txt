add_custom_target(copy_python ALL)
if(WIN32)
    add_custom_command(
        TARGET copy_python PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item -Path "${CMAKE_CURRENT_SOURCE_DIR}/*py" -Destination "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
    )
else()
    add_custom_command(
        TARGET copy_python PRE_BUILD
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python"
        COMMAND ${BASH_COMMAND} cp "${CMAKE_CURRENT_SOURCE_DIR}/*py" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python/"
        #COMMAND ${BASH_COMMAND} cp -r "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_python/*" "${CMAKE_CURRENT_SOURCE_DIR}/"
    )
endif()
