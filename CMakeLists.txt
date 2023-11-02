cmake_minimum_required (VERSION 3.12)

project("pace-python" VERSION "0.1.0")

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_MACOSX_RPATH TRUE)

set(CMAKE_CXX_STANDARD 11)
set(CXX_STANDARD_REQUIRED 11)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(MINIMUM_PYBIND11_VERSION 2.10.1)
set(FETCH_PYBIND11_REPO https://github.com/pybind/pybind11)

option(WITH_HORACE "Include Horace" ON)
option(WITH_SPINW "Include SpinW" ON)

set(HORACE_VERSION 3.6.3 CACHE STRING "Sets the Horace release version number to download")
set(SPINW_VERSION e3e57aae432f6737aff81d31ccda6e7dce741cef CACHE STRING "Sets the SpinW version (git tag/branch/hash) to download")

set(HORACE_PATH "" CACHE PATH "Sets the path of external Horace. If unset, downloads the version set with HORACE_VERSION")
set(SPINW_PATH "" CACHE PATH "Sets the path of external Horace. If unset, downloads the version set with SPINW_VERSION")

set(SPINW_REPO "mducle/spinw" CACHE STRING "Sets the git repo used to download SpinW")


# The latest VS needs an extra library VCRUNTIME140_1.dll which is not in 
# the anaconda redistributable module (yet) - so disable it.
# https://developercommunity.visualstudio.com/content/problem/852548/vcruntime140-1dll-is-missing.html
if(WIN32)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -d2FH4-")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -d2FH4-")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -d2:-FH4-")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -d2:-FH4-")
endif(WIN32)

if(WIN32)
    find_package(POWERSHELL REQUIRED)
else()
    find_package(BASH REQUIRED)
endif()

if (PYTHON_EXECUTABLE)
  # Ensure the provided Python interpreter is used
  set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
endif()
find_package(Python3 COMPONENTS Interpreter Development)

# Use system pybind11 if it exists
find_package(pybind11 ${MINIMUM_PYBIND11_VERSION} QUIET)
if (pybind11_FOUND)
  message(STATUS "pybind11 >= ${MINIMUM_PYBIND11_VERSION} found")
else()
  include(FetchContent)
  if (EXISTS "${FETCHCONTENT_BASE_DIR}/pybind11-src")
    set(pybind11_POPULATED ON)
    set(pybind11_SOURCE_DIR "${FETCHCONTENT_BASE_DIR}/pybind11-src")
    set(pybind11_BINARY_DIR "${FETCHCONTENT_BASE_DIR}/pybind11-build")
    message("Found pre-fetched pybind11")
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
  else()
    message(STATUS "Fetching pybind11 v${MINIMUM_PYBIND11_VERSION} from ${FETCH_PYBIND11_REPO}")
    FetchContent_Declare(pybind11 GIT_REPOSITORY ${FETCH_PYBIND11_REPO} GIT_TAG v${MINIMUM_PYBIND11_VERSION} GIT_SHALLOW 1)
    FetchContent_GetProperties(pybind11)
    if(NOT pybind11_POPULATED)
      FetchContent_Populate(pybind11)
      add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
    endif()
  endif()
  set(pybind11_FOUND ON)
endif()
if (NOT PYTHON_INCLUDE_DIRS)
  set(PYTHON_INCLUDE_DIRS ${Python3_INCLUDE_DIRS})
endif()
if (NOT PYTHON_LIBRARIES)
  set(PYTHON_LIBRARIES ${Python3_LIBRARIES})
endif()

# You can set a specific Matlab version folder here
#set(Matlab_ROOT_DIR "c:/Program Files/MATLAB/R2020a")
find_package(Matlab REQUIRED COMPONENTS MCC_COMPILER)
include(src/matlab.cmake)

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
#add_subdirectory(pace_neutrons)
