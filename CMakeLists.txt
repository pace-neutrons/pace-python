cmake_minimum_required (VERSION 3.12)

project("pace-python" VERSION "0.1.0")

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_MACOSX_RPATH TRUE)

set(CMAKE_CXX_STANDARD 11)
set(CXX_STANDARD_REQUIRED 11)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(MINIMUM_PYBIND11_VERSION 2.5.0)
set(FETCH_PYBIND11_REPO https://github.com/pybind/pybind11)

if(WIN32)
    find_package(POWERSHELL REQUIRED)
else()
    find_package(BASH REQUIRED)
endif()

find_package(Python3 COMPONENTS Interpreter Development)
if(Python3_FOUND)
  set(PYTHONINTERP_FOUND ON)
  set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})
  set(PYTHON_VERSION_STRING "${Python3_VERSION}")
  set(PYTHON_VERSION_MAJOR ${Python3_VERSION_MAJOR})
  set(PYTHON_VERSION_MINOR ${Python3_VERSION_MINOR})
  set(PYTHON_VERSION_PATCH ${Python3_VERSION_PATCH})
endif()

# Use system pybind11 if it exists
find_package(pybind11 ${MINIMUM_PYBIND11_VERSION} QUIET)
if (pybind11_FOUND)
  message(STATUS "pybind11 >= ${MINIMUM_PYBIND11_VERSION} found")
else()
  include(FetchContent)
  message(STATUS "Fetching pybind11 v${MINIMUM_PYBIND11_VERSION} from ${FETCH_PYBIND11_REPO}")
  FetchContent_Declare(pybind11 GIT_REPOSITORY ${FETCH_PYBIND11_REPO} GIT_TAG v${MINIMUM_PYBIND11_VERSION} GIT_SHALLOW 1)
  FetchContent_GetProperties(pybind11)
  if(NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
  endif()
  set(pybind11_FOUND ON)
endif()

# You can set a specific Matlab version folder here
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

include(PACE)

add_subdirectory(src)
add_subdirectory(pace_python)
