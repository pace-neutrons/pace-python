# Original code: https://github.com/floridoo/cmake_external/blob/master/cmake/Download.cmake
###########################################################################
#   Copyright 2017 Florian Reiterer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###########################################################################

# Modified with code from: https://github.com/Crascit/DownloadProject/blob/master/DownloadProject.cmake
# Distributed under the OSI-approved MIT License.  See accompanying
# file LICENSE or https://github.com/Crascit/DownloadProject for details.

set(download_template [=[
cmake_minimum_required(VERSION 2.8.2)
project(@DL_ARGS_PROJ@-download NONE)
include(ExternalProject)
ExternalProject_Add(@DL_ARGS_PROJ@-download
    @DL_ARGS_UNPARSED_ARGUMENTS@
    BINARY_DIR "@DL_ARGS_SOURCE_DIR@"
    SOURCE_DIR "@DL_ARGS_BINARY_DIR@"
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ""
    TEST_COMMAND ""
)
]=])

function(download)
    set(options QUIET)
    set(oneValueArgs
        PROJ
        PREFIX
        DOWNLOAD_DIR
        SOURCE_DIR
        BINARY_DIR
        # Prevent the following from being passed through
        CONFIGURE_COMMAND
        BUILD_COMMAND
        INSTALL_COMMAND
        TEST_COMMAND
    )
    set(multiValueArgs "")
    cmake_parse_arguments(DL_ARGS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if (DL_ARGS_QUIET)
        set(OUTPUT_QUIET "OUTPUT_QUIET")
    else()
        unset(OUTPUT_QUIET)
        message(STATUS "Downloading/updating ${DL_ARGS_PROJ}")
    endif()
    if (NOT DL_ARGS_PREFIX)
        set(DL_ARGS_PREFIX "${CMAKE_BINARY_DIR}")
    else()
        get_filename_component(DL_ARGS_PREFIX "${DL_ARGS_PREFIX}" ABSOLUTE
                               BASE_DIR "${CMAKE_CURRENT_BINARY_DIR}")
    endif()
    if (NOT DL_ARGS_DOWNLOAD_DIR)
        set(DL_ARGS_DOWNLOAD_DIR "${DL_ARGS_PREFIX}/${DL_ARGS_PROJ}-download")
    endif()
    if (NOT DL_ARGS_SOURCE_DIR)
        set(DL_ARGS_SOURCE_DIR "${DL_ARGS_PREFIX}/${DL_ARGS_PROJ}-src")
    endif()
    if (NOT DL_ARGS_BINARY_DIR)
        set(DL_ARGS_BINARY_DIR "${DL_ARGS_PREFIX}/${DL_ARGS_PROJ}-build")
    endif()
    set(${DL_ARGS_PROJ}_SOURCE_DIR "${DL_ARGS_SOURCE_DIR}" PARENT_SCOPE)
    set(${DL_ARGS_PROJ}_BINARY_DIR "${DL_ARGS_BINARY_DIR}" PARENT_SCOPE)
    # CLion workaround
    file(REMOVE "${DL_ARGS_DOWNLOAD_DIR}/CMakeCache.txt")

    string(CONFIGURE "${download_template}" cmake_lists @ONLY)
    file(WRITE "${DL_ARGS_DOWNLOAD_DIR}/CMakeLists.txt" "${cmake_lists}")
    execute_process(COMMAND ${CMAKE_COMMAND} 
                        -G "${CMAKE_GENERATOR}"
                        -D "CMAKE_MAKE_PROGRAM:FILE=${CMAKE_MAKE_PROGRAM}"
                        .
                    RESULT_VARIABLE result
                    WORKING_DIRECTORY "${DL_ARGS_DOWNLOAD_DIR}"
    )
    if(result)
        message(FATAL_ERROR "CMake step for ${DL_ARGS_PROJ} failed: ${result}")
    endif()
    execute_process(COMMAND ${CMAKE_COMMAND} --build .
                    RESULT_VARIABLE result
                    WORKING_DIRECTORY "${DL_ARGS_DOWNLOAD_DIR}"
    )
    if(result)
        message(FATAL_ERROR "Build step for ${name} failed: ${result}")
    endif()
endfunction()
