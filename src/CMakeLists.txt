mcr_add_mex(
    NAME call_python
    SRC call_python.cpp type_converter.cpp load_matlab.cpp
)
target_include_directories(call_python PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(call_python PUBLIC "${pybind11_SOURCE_DIR}/include")
set_property(TARGET call_python PROPERTY LINK_LIBRARIES "")
if(NOT ${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
    target_link_libraries(call_python ${PYTHON_LIBRARIES})
endif()

add_custom_target(compile_ctf ALL)
if(WIN32)
    add_custom_command(
        TARGET compile_ctf PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${HORACE_BINARY_DIR}/Horace" "${CMAKE_CURRENT_BINARY_DIR}/CTF/Horace"
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${HORACE_BINARY_DIR}/Herbert" "${CMAKE_CURRENT_BINARY_DIR}/CTF/Herbert"
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/swfiles" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles"
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/dat_files" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/dat_files"
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/external" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/external"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item -Force "${HORACE_BINARY_DIR}/worker_v2.m.template" -Destination "${CMAKE_CURRENT_BINARY_DIR}/CTF/worker_v2.m"
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons"
    )
else()
    add_custom_command(
        TARGET compile_ctf PRE_BUILD
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${HORACE_BINARY_DIR}/Horace" "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${HORACE_BINARY_DIR}/Herbert" "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/swfiles" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/dat_files" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/external" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
        COMMAND ${BASH_COMMAND} cp -f "${HORACE_BINARY_DIR}/worker_v2.m.template" "${CMAKE_CURRENT_BINARY_DIR}/CTF/worker_v2.m"
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons"
    )
endif()

add_custom_command(
    TARGET compile_ctf PRE_BUILD
    COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_MODULE_PATH}/patch_horace.py" "${CMAKE_CURRENT_SOURCE_DIR}/diffs" "${CMAKE_CURRENT_BINARY_DIR}/CTF"
    COMMAND ${Matlab_MCC_COMPILER} -W ctf:pace_${Matlab_RELEASE} -U -d "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons" -v
        -a "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        -a "${CMAKE_CURRENT_SOURCE_DIR}/matlab_overrides"
        "${CMAKE_CURRENT_SOURCE_DIR}/call.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyclasswrapper.m"
        "$<TARGET_FILE_DIR:call_python>/call_python.${Matlab_MEX_EXTENSION}"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyhorace_init.m"
)
add_dependencies(compile_ctf call_python)
