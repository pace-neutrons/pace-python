# You can set a specific Matlab version folder here
#set(Matlab_ROOT_DIR "d:/MATLAB/Matlab Runtime/v910")
#set(MATLAB_FIND_DEBUG 1)
find_package(Matlab REQUIRED COMPONENTS MCC_COMPILER)

if (NOT Matlab_INCLUDE_DIRS)
  # Could not find (or completely find) MATLAB or MCR
  if (Matlab_ROOT_DIR)
    file(GLOB_RECURSE _mlarrayhpp_tmp "${Matlab_ROOT_DIR}/*MatlabDataArray.hpp")
    if (_mlarrayhpp_tmp)
      get_filename_component(Matlab_DATAARRAY_INCLUDE "${_mlarrayhpp_tmp}" REALPATH)
      get_filename_component(Matlab_INCLUDE_DIRS "${Matlab_DATAARRAY_INCLUDE}" DIRECTORY)
      # Set root dir to be two up from this (should be <MLROOT>/extern/include)
      get_filename_component(Matlab_ROOT_DIR "${Matlab_INCLUDE_DIRS}" DIRECTORY)
      get_filename_component(Matlab_ROOT_DIR "${Matlab_ROOT_DIR}" DIRECTORY)
    else()
      message(FATAL_ERROR "MATLAB/MCR not found, cannot compile libpymcr.")
    endif()
  else()
    message(FATAL_ERROR "MATLAB/MCR not found, cannot compile libpymcr.")
  endif()
endif()

message(STATUS "Matlab_ROOT_DIR=${Matlab_ROOT_DIR}")
message(STATUS "Matlab_INCLUDE_DIRS=${Matlab_INCLUDE_DIRS}")

# On MacOS github runners it can sometimes fail to find the right libraries
if (NOT Matlab_HAS_CPP_API)
  if (NOT Matlab_ENGINE_LIBRARY)
    file(GLOB_RECURSE Matlab_ENGINE_LIBRARY "${Matlab_ROOT_DIR}/extern/bin/*/libMatlabEngine*")
  endif()
  if (NOT Matlab_DATAARRAY_LIBRARY)
    file(GLOB_RECURSE Matlab_DATAARRAY_LIBRARY "${Matlab_ROOT_DIR}/extern/bin/*/libMatlabDataArray*")
  endif()
  if (Matlab_ENGINE_LIBRARY AND Matlab_DATAARRAY_LIBRARY)
    set(Matlab_HAS_CPP_API 1)
    list(APPEND Matlab_LIBRARIES ${Matlab_ENGINE_LIBRARY})
    list(APPEND Matlab_LIBRARIES ${Matlab_DATAARRAY_LIBRARY})
  endif()
endif()

# Gets the version string from the xml file if it is not defined
if (NOT Matlab_VERSION_STRING OR Matlab_VERSION_STRING STREQUAL "unknown")
  if(EXISTS "${Matlab_ROOT_DIR}/VersionInfo.xml")
    file(STRINGS "${Matlab_ROOT_DIR}/VersionInfo.xml" versioninfo_string NEWLINE_CONSUME)
    if(versioninfo_string)
      string(REGEX MATCH "<version>(.*)</version>"
             version_reg_match
             ${versioninfo_string})
      if(CMAKE_MATCH_1 MATCHES "(([0-9]+)\\.([0-9]+))[\\.0-9]*")
        set(Matlab_VERSION_STRING "${CMAKE_MATCH_1}")
        message(STATUS "Matlab_VERSION_STRING = ${Matlab_VERSION_STRING}")
      endif()
    endif()
  endif()
endif()

# # Prints all variables
# get_cmake_property(_variableNames VARIABLES)
# list (SORT _variableNames)
# foreach (_variableName ${_variableNames})
#   message(STATUS "${_variableName}=${${_variableName}}")
# endforeach()
 
# Define our own version of matlab_add_mex in order to not link libraries
# and avoid all but the Matlab_INCLUDE_DIRS variables.
# Does not support the MODULE or EXECUTABLE modes (just SHARED)
# Does not support the DOCUMENTATION option
# Forces extensions to be .mexw64, .mexa64 or .mexmaci64 depending on OS
# Forces the option NO_IMPLICIT_LINK_TO_MATLAB_LIBRARIES and ignores LINK_TO
# Forces R2018a mode (so does not support older versions of MATLAB)
# (this is opposite to the default behaviour of matlab_add_mex)
function(mcr_add_mex)
  if(Matlab_VERSION_STRING VERSION_LESS "9.4") 
    message(FATAL_ERROR "[mcr_add_mex] Only Matlab newer than R2018a supported")
  endif()
  if(NOT WIN32)
    if(CMAKE_CXX_COMPILER_LOADED)
      check_cxx_compiler_flag(-pthread HAS_MINUS_PTHREAD)
    elseif(CMAKE_C_COMPILER_LOADED)
      check_c_compiler_flag(-pthread HAS_MINUS_PTHREAD)
    endif()
    if (APPLE)
      set(Matlab_MEX_EXTENSION mexmaci64)
      set(Matlab_ARCH maci64)
    else()
      set(Matlab_MEX_EXTENSION mexa64)
      set(Matlab_ARCH glnxa64)
    endif()
  else()
    set(Matlab_MEX_EXTENSION mexw64)
      set(Matlab_ARCH win64)
  endif()
  set(options EXCLUDE_FROM_ALL)
  set(oneValueArgs NAME OUTPUT_NAME)
  set(multiValueArgs SRC)
  set(prefix _matlab_addmex_prefix)
  cmake_parse_arguments(${prefix} "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )
  if(NOT ${prefix}_NAME)
    message(FATAL_ERROR "[MATLAB] The MEX target name cannot be empty")
  endif()
  if(NOT ${prefix}_OUTPUT_NAME)
    set(${prefix}_OUTPUT_NAME ${${prefix}_NAME})
  endif()
  set(MEX_API_MACRO "MATLAB_DEFAULT_RELEASE=R2018a")
  if (NOT Matlab_EXTERN_LIBRARY_DIR)
    set(Matlab_EXTERN_LIBRARY_DIR ${Matlab_ROOT_DIR}/extern/lib/${Matlab_ARCH})
  endif()
  if(CMAKE_C_COMPILER_LOADED)
    set(MEX_VERSION_FILE "${Matlab_ROOT_DIR}/extern/version/c_mexapi_version.c")
  elseif(CMAKE_CXX_COMPILER_LOADED)
    set(MEX_VERSION_FILE "${Matlab_ROOT_DIR}/extern/version/cpp_mexapi_version.cpp")
  else()
    message(WARNING "[MATLAB] matlab_add_mex requires that at least C or CXX are enabled languages")
  endif()
  set(_option_EXCLUDE_FROM_ALL)
  if(${prefix}_EXCLUDE_FROM_ALL)
    set(_option_EXCLUDE_FROM_ALL "EXCLUDE_FROM_ALL")
  endif()
  add_library(${${prefix}_NAME}
    SHARED
    ${_option_EXCLUDE_FROM_ALL}
    ${${prefix}_SRC}
    #${MEX_VERSION_FILE}
    ${${prefix}_UNPARSED_ARGUMENTS})
  target_include_directories(${${prefix}_NAME} SYSTEM PRIVATE ${Matlab_INCLUDE_DIRS})
  set_target_properties(${${prefix}_NAME}
    PROPERTIES
      PREFIX ""
      OUTPUT_NAME ${${prefix}_OUTPUT_NAME}
      SUFFIX ".${Matlab_MEX_EXTENSION}")
  target_compile_definitions(${${prefix}_NAME} PRIVATE ${MEX_API_MACRO} MATLAB_MEX_FILE)

  # entry point in the mex file + taking care of visibility and symbol clashes.
  if(WIN32)
    if (MSVC)
      set(_link_flags "${_link_flags} /EXPORT:mexFunction")
      #set(_link_flags "${_link_flags} /EXPORT:mexfilerequiredapiversion")
      set_property(TARGET ${${prefix}_NAME} APPEND PROPERTY LINK_FLAGS ${_link_flags})
    endif() # No other compiler currently supported on Windows.
    set_target_properties(${${prefix}_NAME}
      PROPERTIES
        DEFINE_SYMBOL "DLL_EXPORT_SYM=__declspec(dllexport)")
  else()
    #set(_ver_map_files ${Matlab_EXTERN_LIBRARY_DIR}/c_exportsmexfileversion.map)
    if(NOT Matlab_VERSION_STRING VERSION_LESS "9.5") # For 9.5 (R2018b) (and newer?)
      target_compile_options(${${prefix}_NAME} PRIVATE "-fvisibility=default")
    endif()
    if(APPLE)
      if(Matlab_HAS_CPP_API)
        #list(APPEND _ver_map_files ${Matlab_EXTERN_LIBRARY_DIR}/cppMexFunction.map) # This one doesn't exist on Linux
        set(_link_flags "${_link_flags} -Wl,-U,_mexCreateMexFunction -Wl,-U,_mexDestroyMexFunction -Wl,-U,_mexFunctionAdapter")
      endif()
      set(_export_flag_name -exported_symbols_list)
    else() # Linux
      if(HAS_MINUS_PTHREAD)
        target_compile_options(${${prefix}_NAME} PRIVATE "-pthread")
      endif()
      set(_link_flags "${_link_flags} -Wl,--as-needed")
      set(_export_flag_name --version-script)
    endif()
    #foreach(_file ${_ver_map_files})
    #  set(_link_flags "${_link_flags} -Wl,${_export_flag_name},${_file}")
    #endforeach()
    set_target_properties(${${prefix}_NAME}
      PROPERTIES
        DEFINE_SYMBOL "DLL_EXPORT_SYM=__attribute__((visibility(\"default\")))"
        LINK_FLAGS "${_link_flags}"
    )
  endif()
endfunction()
