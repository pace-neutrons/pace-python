include(Download)
include(ExternalProject)

message(STATUS "Obtaining desired PACE components") 

if(WITH_SPINW)
    if(SPINW_PATH)
        #TODO: Set ExternalProject_Add up correctly for SpinW
        #ISSUE: Currently does not actualy have anyway to check if SpinW is in the dir specified
        message(STATUS "Including existing SpinW")
        ExternalProject_Add(SpinW 
            SOURCE_DIR "${SPINW_PATH}"
            #INSTALL_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            DOWNLOAD_COMMAND ""
            CONFIGURE_COMMAND ""
            BUILD_COMMAND "" 
            INSTALL_COMMAND ""
            #CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/CTF/SpinW"
            )
        #message(FATAL_ERROR "Successfully included ${SPINW_PATH}") #check this
    else()
        message(STATUS "Downloading SpinW")
        ExternalProject_Add(SpinW
            GIT_REPOSITORY https://github.com/${SPINW_REPO}.git
            GIT_TAG ${SPINW_VERSION}
            GIT_SHALLOW 1
            BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF/SpinW"
            CONFIGURE_COMMAND ""
            BUILD_COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/swfiles <SOURCE_DIR>/external <SOURCE_DIR>/dat_files <BINARY_DIR> 
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
endif()

if(WITH_HORACE)
    if(HORACE_PATH)
        message(STATUS "Including existing Horace")
        ExternalProject_Add(HORACE 
            SOURCE_DIR ${HORACE_PATH}
            #INSTALL_DIR "${CMAKE_CURRENT_BINARY_DIR}/CTF"
            DOWNLOAD_COMMAND "" #empty quotation marks effectively disables the download feature of ExternalProject_Add
            CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/CTF"
            #INSTALL_COMMAND ""
            )

        #message(FATAL_ERROR "Successfully included external Horace")
    else()
        message(STATUS "Downloading Horace")
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
endif()