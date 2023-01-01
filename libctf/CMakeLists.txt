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
