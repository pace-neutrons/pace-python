include(Download)
include(ExternalProject)

message(STATUS "Obtaining desired PACE components") 

if(WITH_SPINW)
    if(SPINW_PATH)
        find_file(SPINW_FOUND
            NAMES "install_spinw.m"
            PATHS "${SPINW_PATH}"
            NO_CACHE
        )

        if(NOT SPINW_FOUND)
            message(FATAL_ERROR "SpinW may not exist at ${SPINW_PATH}") #TODO: write a better message
        endif()
        message(STATUS "SpinW found at: ${SPINW_PATH}")
        ExternalProject_Add(SpinW 
            SOURCE_DIR "${SPINW_PATH}"
            #INSTALL_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            DOWNLOAD_COMMAND ""
            CONFIGURE_COMMAND ""
            BUILD_COMMAND "" 
            INSTALL_COMMAND ""
            #CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/CTF/SpinW"
            )
    else()
        message(STATUS "Downloading SpinW from https://github.com/${SPINW_REPO}.git @ ${SPINW_VERSION}")
        ExternalProject_Add(SpinW
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
        
        # download(
        #     PROJ SPINW
        #     GIT_REPOSITORY https://github.com/${SPINW_REPO}.git
        #     GIT_TAG ${SPINW_VERSION}
        #     GIT_SHALLOW 1
        #     SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF" 
        #)
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
            message(FATAL_ERROR "Horace may not exist at ${HORACE_PATH}") #TODO: write a better message
        endif()
        message(STATUS "Horace found: ${HORACE_PATH}")
        ExternalProject_Add(HORACE 
            SOURCE_DIR ${HORACE_PATH}
            #INSTALL_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            DOWNLOAD_COMMAND "" #empty quotation marks effectively disables the download feature of ExternalProject_Add
            CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/CTF"
            #COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/CTF/Horace/herbert_core/utilities/classes/@testsigvar"
            #INSTALL_COMMAND ""
            )

    else()
        message(STATUS "Downloading Horace from https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-win64-R2019b.zip")
        if(WIN32)
            download(
                PROJ HORACE
                URL https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-win64-R2019b.zip
                BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            )
        else()
            download(
                PROJ HORACE
                URL https://github.com/pace-neutrons/Horace/releases/download/v${HORACE_VERSION}/Horace-${HORACE_VERSION}-linux-R2019b.tar.gz
                BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            )
        endif()
    endif()

else()
    message(STATUS "Horace not included")
endif()

if(WITH_HORACE AND HORACE_PATH)
    add_custom_command(
        TARGET HORACE POST_BUILD
        COMMENT "@testsigvar"
        COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/CTF/Horace/herbert_core/utilities/classes/@testsigvar"
    )
endif()
