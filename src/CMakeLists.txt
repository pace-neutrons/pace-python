mcr_add_mex(
    NAME call_python
    SRC call_python.cpp load_matlab.cpp
)
set_property(TARGET call_python PROPERTY LINK_LIBRARIES "")

add_custom_target(compile_ctf ALL)
add_custom_target(patch_ctf ALL)
add_custom_target(copy_mex ALL)

#add dependencies on external projects to compile_ctf
if(WITH_HORACE)
    add_dependencies(compile_ctf patch_ctf)
endif()

if(WITH_SPINW)
    add_dependencies(compile_ctf spinw)
endif()


if(NOT HORACE_PATH AND WITH_HORACE)
    #Sets what files related to Horace should be included in the compiled ctf.
    set(HORACE_INCLUDE
        -a "${CMAKE_BINARY_DIR}/CTF/Horace"
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
    set(SPINW_INCLUDE
        -a "${CMAKE_BINARY_DIR}/CTF/SpinW"
    )
else()
    set(SPINW_INCLUDE
        ""
    )
endif()

# Runs appropriate scripts to tidy up files in CTF folder
if(WIN32)
    add_custom_command(
        TARGET patch_ctf PRE_BUILD
        COMMAND ${POWERSHELL_COMMAND} "${CMAKE_MODULE_PATH}/remove_nonctf.ps1" "${CMAKE_BINARY_DIR}/CTF"
    )
else()
    add_custom_command(
        TARGET patch_ctf PRE_BUILD
        COMMAND ${BASH_COMMAND} "${CMAKE_MODULE_PATH}/remove_nonctf.sh" "${CMAKE_BINARY_DIR}/CTF"
    )
endif()

if(NOT HORACE_PATH AND WITH_HORACE)
    add_custom_command(
        TARGET patch_ctf PRE_BUILD
        COMMENT "Patching CTF"
        COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_MODULE_PATH}/patch_horace.py" "${CMAKE_CURRENT_SOURCE_DIR}/diffs" "${CMAKE_BINARY_DIR}/CTF"
    )
  if(WIN32)
    add_custom_command(
        TARGET copy_mex
        COMMENT "Copying mex to CTF"
        COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_BINARY_DIR}/bin/Release/call_python.mexw64" "${CMAKE_BINARY_DIR}/CTF"
    )
  else()
    add_custom_command(
        TARGET copy_mex
        COMMENT "Copying mex to CTF"
        COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_BINARY_DIR}/bin/call_python.${Matlab_MEX_EXTENSION}" "${CMAKE_BINARY_DIR}/CTF"
    )
  endif()
endif()
add_dependencies(patch_ctf horace)
add_dependencies(copy_mex call_python)

add_custom_command(
    TARGET compile_ctf PRE_BUILD
    COMMENT "MCC compiling"
    COMMAND ${Matlab_MCC_COMPILER} -U -W ctf:pace_${Matlab_RELEASE} -d "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/pace_neutrons" -v
        ${HORACE_INCLUDE}
        ${SPINW_INCLUDE}
        -a "${CMAKE_CURRENT_SOURCE_DIR}/matlab_overrides"
        "${CMAKE_CURRENT_SOURCE_DIR}/call.m"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyclasswrapper.m"
        "$<TARGET_FILE_DIR:call_python>/call_python.${Matlab_MEX_EXTENSION}"
        "${CMAKE_CURRENT_SOURCE_DIR}/pyhorace_init.m"
)
add_dependencies(compile_ctf call_python)
