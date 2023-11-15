include(ExternalProject)

message(STATUS "Obtaining desired PACE components") 

if(WITH_SPINW)
    if(SPINW_PATH)
        # checks if provided SpinW path is correct and 
        # includes it if it exists
        find_file(SPINW_FOUND
            NAMES "install_spinw.m"
            PATHS "${SPINW_PATH}"
            NO_CACHE
        )
        if(NOT SPINW_FOUND)
            message(FATAL_ERROR "SpinW may not exist at ${SPINW_PATH}")
        endif()
        message(STATUS "SpinW found at: ${SPINW_PATH}")

        ExternalProject_Add(spinw 
            SOURCE_DIR "${SPINW_PATH}"
            DOWNLOAD_COMMAND ""
            CONFIGURE_COMMAND ""
            BUILD_COMMAND "" 
            INSTALL_COMMAND ""
            )
    else()

        #downloads desired SpinW version and includes it in the project
        message(STATUS "Downloading SpinW from https://github.com/${SPINW_REPO}.git @ ${SPINW_VERSION}")
        ExternalProject_Add(spinw
            GIT_REPOSITORY https://github.com/${SPINW_REPO}.git
            GIT_TAG ${SPINW_VERSION}
            GIT_SHALLOW 1
            BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF/SpinW"
            CONFIGURE_COMMAND ""
            BUILD_COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/swfiles <BINARY_DIR>/swfiles
                  COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/external <BINARY_DIR>/external
                  COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/dat_files <BINARY_DIR>/dat_files
            INSTALL_COMMAND ""
            TEST_COMMAND ""
        )
        
    endif()

else()
    message(STATUS "SPINW not included")

endif()

if(WITH_HORACE)
    if(HORACE_PATH)
        #Searches for the horace_version.m file to check whether horace can be found in the provided dir
        #ISSUE: different horace versions may have different dir structure  
        find_file(HORACE_FOUND 
            NAMES "horace_version.m"
            PATHS "${HORACE_PATH}/horace_core/admin"
            NO_CACHE
            )

        if(NOT HORACE_FOUND)
            message(FATAL_ERROR "Horace may not exist at ${HORACE_PATH}") 
        endif()
        message(STATUS "Horace found: ${HORACE_PATH}")

        #includes the located version of Horace in the current project
        ExternalProject_Add(horace 
            SOURCE_DIR ${HORACE_PATH}
            DOWNLOAD_COMMAND "" #empty quotation marks effectively disables the download feature of ExternalProject_Add
            CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/CTF"
            )

    else()

        #downloads desired Horace version suitable for the users OS
        if(WIN32)
            set(HORACE_TYPE "win64")
        else()
            set(HORACE_TYPE "linux")
        endif()

        message(STATUS "Downloading Horace from https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-${HORACE_TYPE}-R2019b.zip")
        ExternalProject_Add(horace
            URL https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-${HORACE_TYPE}-R2019b.zip
            BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            SOURCE_DIR 
            CONFIGURE_COMMAND ""
            BUILD_COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/Horace <BINARY_DIR>/Horace
                   COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/Herbert <BINARY_DIR>/Herbert
            INSTALL_COMMAND ""
            TEST_COMMAND ""
        )
    endif()

else()
    message(STATUS "Horace not included")
endif()

#removes unecessary files to avoid associated errors during build
if(WITH_HORACE AND HORACE_PATH)
    add_custom_command(
        TARGET HORACE POST_BUILD
        COMMENT "@testsigvar"
        COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/CTF/Horace/herbert_core/utilities/classes/@testsigvar"
    )
endif()
