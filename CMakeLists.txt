cmake_minimum_required (VERSION 3.1)

project("hugo" VERSION "0.1.0")

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_MACOSX_RPATH TRUE)

set(CMAKE_CXX_STANDARD 11)
set(CXX_STANDARD_REQUIRED 11)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

if(WIN32)
    find_package(PowerShell REQUIRED)
else()
    find_package(BASH REQUIRED)
endif()

#set(Matlab_ROOT_DIR "c:/Program Files/MATLAB/R2019b")
find_package(Matlab REQUIRED COMPONENTS MAIN_PROGRAM MEX_COMPILER MCC_COMPILER)
get_filename_component(Matlab_LIBRARY_DIR "${Matlab_MEX_LIBRARY}" DIRECTORY)
get_filename_component(Matlab_BIN_DIR "${Matlab_MAIN_PROGRAM}" DIRECTORY)

# Get the Matlab release from the VersionInfo.xml file
file(READ "${Matlab_ROOT_DIR}/VersionInfo.xml" _release_info)
string(REGEX REPLACE
    ".*<release>(R[0-9]+[ab])</release>.*"
    "\\1"
    Matlab_RELEASE
    "${_release_info}"
)
matlab_get_version_from_release_name(${Matlab_RELEASE} Matlab_VERSION)

# MATLAB 9.4 (R2018a) and newer have a new C++ API
# This API pulls additional required libraries.
if(NOT ${Matlab_VERSION} VERSION_LESS "9.4")
    set(Matlab_HAS_CPP_API 1)
endif()

include(PyBind11)
add_subdirectory(${PyBind11_DIR} ${PyBind11_DIR})

include(PACE)

add_subdirectory(src)
add_subdirectory(pace_python)
