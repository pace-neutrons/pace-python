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

#add dependencies on external projects to compile_ctf
if(WITH_HORACE)
    add_dependencies(compile_ctf horace)
endif()

if(WITH_SPINW)
    add_dependencies(compile_ctf spinw)
endif()


#Runs appropriate scripts to tidy up files in Horace and Herbert
if(NOT HORACE_PATH AND WITH_HORACE)
    if(WIN32)
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/Horace" 
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/Herbert"
        )
    else()
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/Horace" 
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/Herbert"
        )
    endif()

    #ISSUE: what is this?
    #file(RENAME "${CMAKE_BINARY_DIR}/CTF/worker_v2.m.template" "${CMAKE_BINARY_DIR}/CTF/worker_v2.m")

    #Sets what files related to Horace should be included in the compiled ctf. 
    set(HORACE_INCLUDE
        -a "${CMAKE_BINARY_DIR}/CTF/Horace"
        -a "${CMAKE_BINARY_DIR}/CTF/Herbert"
        )

elseif(WITH_HORACE AND HORACE_PATH) 
    #sets files to include in compiled ctf for a provided Horace
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

#Sets the required SpinW directories for use in compiled ctf 
if(WITH_SPINW AND SPINW_PATH)
    set(SPINW_INCLUDE
        -a "${SPINW_PATH}" 
    )
elseif(WITH_SPINW AND NOT SPINW_PATH)
    
    if(WIN32)
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/SpinW/swfiles"
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/SpinW/dat_files"
            COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.ps1" "${CMAKE_BINARY_DIR}/CTF/SpinW/external"
        )
    else()
        add_custom_command(
            TARGET compile_ctf PRE_BUILD
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/SpinW"
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/SpinW"
            COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/copy_and_remove_0.sh" "${CMAKE_BINARY_DIR}/CTF/SpinW"
        )
    endif()
    
    
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
