cmake_minimum_required(VERSION 3.4)
project(libctf LANGUAGES CXX)

# You can set a specific Matlab version folder here
set(Matlab_ROOT_DIR "c:/Program Files/MATLAB/R2020a")
find_package(Matlab REQUIRED COMPONENTS MAIN_PROGRAM MEX_COMPILER MCC_COMPILER)
get_filename_component(Matlab_LIBRARY_DIR "${Matlab_MEX_LIBRARY}" DIRECTORY)
get_filename_component(Matlab_BIN_DIR "${Matlab_MAIN_PROGRAM}" DIRECTORY)

add_subdirectory(pybind11)

pybind11_add_module(libpymcr type_converter.cpp libpymcr.cpp)
target_include_directories(libpymcr PRIVATE ${Matlab_INCLUDE_DIRS})

matlab_add_mex(
    NAME call_python
    SRC call_python.cpp type_converter.cpp
)
target_include_directories(call_python PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(call_python PUBLIC "${pybind11_SOURCE_DIR}/include")
if(WIN32)
    target_link_libraries(call_python ${PYTHON_LIBRARIES})
endif()
