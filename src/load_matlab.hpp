#ifndef LOAD_MATLAB_HPP
#define LOAD_MATLAB_HPP

#ifdef _WIN32
#ifndef __wtypes_h__
#include <wtypes.h>
#endif
#ifndef __WINDEF_
#include <windef.h>
#endif
#endif

// Imported Matlab functions
#ifdef _WIN32
#include <libloaderapi.h>
#else
#include <dlfcn.h>
#endif

#include "type_converter.hpp"
#include <fstream>

void *_loadlib(std::string path, const char* libname, std::string mlver="");
void *_resolve(void* lib, const char* sym);
std::string _getMLversion(std::string mlroot);
void _loadlibraries(std::string matlabroot);

void* mexGetFunctionImpl();
void mexDestroyFunctionImpl(void* impl);

#endif
