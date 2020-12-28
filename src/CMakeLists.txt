matlab_add_mex(
    NAME call_python
    SRC call_python.cpp
)
target_include_directories(call_python PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(call_python PUBLIC "${PyBind11_DIR}/include")
target_link_libraries(call_python ${PYTHON_LIBRARIES})

matlab_add_mex(
    NAME pythonRemoveFuncKey
    SRC pythonRemoveFuncKey.cpp
)
target_include_directories(pythonRemoveFuncKey PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(pythonRemoveFuncKey PUBLIC "${PyBind11_DIR}/include")
target_link_libraries(pythonRemoveFuncKey ${PYTHON_LIBRARIES})

matlab_add_mex(
    NAME get_address
    SRC get_address.cpp
)

pybind11_add_module(call_matlab 
                    call_matlab.cpp)
target_include_directories(call_matlab PUBLIC ${Matlab_INCLUDE_DIRS})
target_link_libraries(call_matlab PRIVATE ${Matlab_MEX_LIBRARY} ${Matlab_MX_LIBRARY})
#if(Matlab_HAS_CPP_API)
#    target_include_directories(call_matlab PUBLIC ${Matlab_ENGINE_LIBRARY} ${Matlab_DATAARRAY_LIBRARY})
#    target_link_libraries(call_matlab PRIVATE ${Matlab_ENGINE_LIBRARY} ${Matlab_DATAARRAY_LIBRARY})
#endif()

add_custom_target(compile_ctf ALL)
if(WIN32)
    add_custom_command(
        TARGET compile_ctf PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/prep_horace_mcc.ps1" ${CMAKE_CURRENT_SOURCE_DIR} "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${CMAKE_CURRENT_BINARY_DIR}/sw_tmp/*.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${CMAKE_CURRENT_BINARY_DIR}/sw_tmp/sw/*.m" -Destination "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles/@spinw"
        COMMAND ${POWERSHELL_COMMAND} New-Item -ItemType Directory -Force -Path "${CMAKE_CURRENT_BINARY_DIR}/CTF/+brille"
        COMMAND ${POWERSHELL_COMMAND} Copy-Item "${CMAKE_CURRENT_SOURCE_DIR}/+brille/*" -Destination "${CMAKE_CURRENT_BINARY_DIR}/CTF/+brille"
    )
else()
    add_custom_command(
        TARGET compile_ctf PRE_BUILD
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/prep_horace_mcc.sh" ${CMAKE_CURRENT_SOURCE_DIR} "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace"
        COMMAND ${BASH_COMMAND} cp "${CMAKE_CURRENT_BINARY_DIR}/sw_tmp/*.m" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles"
        COMMAND ${BASH_COMMAND} cp "${CMAKE_CURRENT_BINARY_DIR}/sw_tmp/sw/*.m" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles/@spinw"
        COMMAND ${BASH_COMMAND} mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/CTF/+brille"
        COMMAND ${BASH_COMMAND} cp "${CMAKE_CURRENT_SOURCE_DIR}/+brille/*" "${CMAKE_CURRENT_BINARY_DIR}/CTF/+brille"
    )
endif()

add_custom_command(
    TARGET compile_ctf PRE_BUILD
    COMMAND ${Matlab_MCC_COMPILER} -W python:horace -d "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pyHorace" -v -N
        -a "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        "${CMAKE_CURRENT_SOURCE_DIR}/call.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/call_method.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/thinwrapper.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/wrap_obj.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/has_thin_members.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/recfind.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/getArgOut.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/get_method_refs.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/set_global.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/waitforgui.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/pythonFunctionWrapper.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/call_python_m.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyclasswrapper.m"
        "$<TARGET_FILE_DIR:call_python>/call_python.${Matlab_MEX_EXTENSION}"
        "$<TARGET_FILE_DIR:pythonRemoveFuncKey>/pythonRemoveFuncKey.${Matlab_MEX_EXTENSION}"
        "$<TARGET_FILE_DIR:get_address>/get_address.${Matlab_MEX_EXTENSION}"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyhorace_init.m"
)
add_dependencies(compile_ctf call_python pythonRemoveFuncKey get_address)
