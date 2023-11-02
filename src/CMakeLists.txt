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
#TODO: make the following two sections so that they are used if both horace and spinw are downloaded. might not be necessary otherwise
if(NOT HORACE_PATH AND WITH_HORACE)
    if(WIN32)
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/Horace" 
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/Herbert"
            # COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/swfiles" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/swfiles"
            # COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/dat_files" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/dat_files"
            # COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${SPINW_BINARY_DIR}/external" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW/external"
        )
    else()
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/Horace" 
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/Herbert"
            # COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/swfiles" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
            # COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/dat_files" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
            # COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${SPINW_BINARY_DIR}/external" "${CMAKE_CURRENT_BINARY_DIR}/CTF/spinW"
        )
    endif()

    #file(RENAME "${CMAKE_BINARY_DIR}/CTF/worker_v2.m.template" "${CMAKE_BINARY_DIR}/CTF/worker_v2.m")

    set(HORACE_INCLUDE
        -a "${CMAKE_BINARY_DIR}/CTF/Horace"
        -a "${CMAKE_BINARY_DIR}/CTF/Herbert"
        )

elseif(WITH_HORACE AND HORACE_PATH) #TODO: check logic here
    #TODO: test this a bit more
    #message(STATUS "Removing @testsigvar")
    #message(FATAL_ERROR "cmake binary dir is: ${CMAKE_BINARY_DIR}")
    #ISSUE: @testsigvar isn't created until after we try and remove it
    #file(REMOVE_RECURSE "${CMAKE_BINARY_DIR}/CTF/Horace/herbert_core/utilities/classes/@testsigvar")
    set(HORACE_INCLUDE 
        -a "${CMAKE_BINARY_DIR}/CTF/Horace/horace_core"
        -a "${CMAKE_BINARY_DIR}/CTF/Horace/herbert_core"
        )
else() 
    set(HORACE_INCLUDE
        "" 
    )

endif()

file(MAKE_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons")

#TODO: add necessary remove etc. stuff for spinw inline with the aboves previous implementation
if(WITH_SPINW AND SPINW_PATH)
    set(SPINW_INCLUDE
        -a "${SPINW_PATH}" 
        #-a "${CMAKE_BINARY_DIR}/CTF/SpinW"
    )
elseif(WITH_SPINW AND NOT SPINW_PATH)
    #TODO: need to add correct alternative to where spinw is downloaded similar to horace
    set(SPINW_INCLUDE
        -a "${CMAKE_BINARY_DIR}/CTF/SpinW"
    )
else()
    set(SPINW_INCLUDE
        "" 
    )
endif()


add_custom_command(
    TARGET compile_ctf PRE_BUILD
    COMMENT "MCC compiling"
    #COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_MODULE_PATH}/patch_horace.py" "${CMAKE_CURRENT_SOURCE_DIR}/diffs" "${CMAKE_CURRENT_BINARY_DIR}/CTF"
    COMMAND ${Matlab_MCC_COMPILER} -U -W ctf:pace_${Matlab_RELEASE} -d "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons" -v
        #-a "${CMAKE_CURRENT_BINARY_DIR}/CTF"
        ${HORACE_INCLUDE}
        ${SPINW_INCLUDE}
        -a "${CMAKE_CURRENT_SOURCE_DIR}/matlab_overrides"
        "${CMAKE_CURRENT_SOURCE_DIR}/call.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyclasswrapper.m"
        "$<TARGET_FILE_DIR:call_python>/call_python.${Matlab_MEX_EXTENSION}"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyhorace_init.m"
)
add_dependencies(compile_ctf call_python)
