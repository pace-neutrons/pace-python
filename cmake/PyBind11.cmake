include(ExternalProject)

if(USE_SYSTEM_PYBIND11)
  message(STATUS "Using system Pybind11")
else()
  message(STATUS "Using Pybind11 in ExternalProject")

  # Download and unpack Pybind11 at configure time
  configure_file(${CMAKE_SOURCE_DIR}/cmake/PyBind11.in ${CMAKE_BINARY_DIR}/extern-pybind11/CMakeLists.txt)

  # The OLD behavior for this policy is to ignore the visibility properties
  # for static libraries, object libraries, and executables without exports.
  cmake_policy(SET CMP0063 "OLD")

  execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" . WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/extern-pybind11 )
  execute_process(COMMAND ${CMAKE_COMMAND} --build . WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/extern-pybind11 )

  set(PyBind11_DIR "${CMAKE_BINARY_DIR}/extern-pybind11/pybind11-prefix/src/pybind11/" CACHE PATH "")
endif()
