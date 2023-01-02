#include "libpymcr.hpp"

// Imported Matlab functions
#ifdef _WIN32
#include <libloaderapi.h>
#else
#include <dlfcn.h>
#endif

// Global declaration of libraries
void *_LIBDATAARRAY, *_LIBENGINE, *_LIBCPPSHARED;
std::string _MLVERSTR;

void *_loadlib(std::string path, const char* libname, std::string mlver="") {
#if defined _WIN32
    void* lib = (void*)LoadLibrary((path + "/win64/" + libname + mlver + ".dll").c_str());
#elif defined __APPLE__
    void* lib = dlopen((path + "/glnxa64/" + libname + mlver + ".dylib").c_str(), RTLD_LAZY);
#else
    if (mlver.length() > 0)
        mlver = "." + mlver;
    void* lib = dlopen((path + "/glnxa64/" + libname + ".so" + mlver).c_str(), RTLD_LAZY);
#endif
    if (!lib) {
        throw std::runtime_error(std::string("Cannot load ") + libname);
    }
    return lib;
}
void *_resolve(void* lib, const char* sym) {
#ifdef _WIN32
    return (void*)GetProcAddress((HMODULE)lib, sym);
#else
    return dlsym(lib, sym);
#endif
}
std::string _getMLversion(std::string mlroot) {
    if (_MLVERSTR.length()==0) {
        std::ifstream verfile(mlroot + "/VersionInfo.xml", std::ifstream::in);
        std::ostringstream verstr;
        verstr << verfile.rdbuf();
        std::string vs = verstr.str();
        vs.replace(0, vs.find("version>")+8, "");
        vs.replace(vs.find(".", 3), vs.length(), "");
#ifdef _WIN32
        vs.replace(vs.find("."), 1, "_");
#endif
        _MLVERSTR = vs;
    }
    return _MLVERSTR;
}
void _loadlibraries(std::string matlabroot) {
    if (!_LIBCPPSHARED) {
        _LIBDATAARRAY = _loadlib(matlabroot + "/extern/bin/", "libMatlabDataArray");
        _LIBCPPSHARED = _loadlib(matlabroot + "/runtime/", "libMatlabCppSharedLib", _getMLversion(matlabroot));
    }
}
void _checklibs() {
    if (!_LIBDATAARRAY || !_LIBCPPSHARED) {
        throw std::runtime_error("Matlab libraries must be initialised first.");
    }
}
// Utils
void util_destroy_utf8(char* utf8) { _checklibs(); return ((void(*)(char*))_resolve(_LIBCPPSHARED, "util_destroy_utf8"))(utf8); }
void util_destroy_utf16(char16_t* utf16) { _checklibs(); return ((void(*)(char16_t*))_resolve(_LIBCPPSHARED, "util_destroy_utf16"))(utf16); }
void util_utf8_to_utf16(const char* utf8, char16_t** utf16, size_t* errType) {
    _checklibs(); return ((void(*)(const char*, char16_t**, size_t*))_resolve(_LIBCPPSHARED, "util_utf8_to_utf16"))(utf8, utf16, errType); }
void util_utf16_to_utf8(const char16_t* utf16, char** utf8, size_t* errType) {
    _checklibs(); return ((void(*)(const char16_t*, char**, size_t*))_resolve(_LIBCPPSHARED, "util_utf16_to_utf8"))(utf16, utf8, errType); }
// CPP_SHARED_LIB
void runtime_create_session(char16_t** options, size_t size) {
    _checklibs(); return ((void(*)(char16_t**, size_t))_resolve(_LIBCPPSHARED, "runtime_create_session"))(options, size); }
void runtime_terminate_session() { _checklibs(); return ((void(*)())_resolve(_LIBCPPSHARED, "runtime_terminate_session"))(); }
uint64_t create_mvm_instance_async(const char16_t* name) {
    _checklibs(); return ((uint64_t(*)(const char16_t*))_resolve(_LIBCPPSHARED, "create_mvm_instance_async"))(name); }
uint64_t create_mvm_instance(const char16_t* name, bool* errFlag) {
    _checklibs(); return ((uint64_t(*)(const char16_t*, bool*))_resolve(_LIBCPPSHARED, "create_mvm_instance"))(name, errFlag); }
void terminate_mvm_instance(const uint64_t mvmHandle) {
    _checklibs(); return ((void(*)(const uint64_t))_resolve(_LIBCPPSHARED, "terminate_mvm_instance"))(mvmHandle); }
void wait_for_figures_to_close(const uint64_t mvmHandle) {
    _checklibs(); return ((void(*)(const uint64_t))_resolve(_LIBCPPSHARED, "wait_for_figures_to_close"))(mvmHandle); }
void cppsharedlib_destroy_handles(uintptr_t* handles) {
    _checklibs(); return ((void(*)(uintptr_t*))_resolve(_LIBCPPSHARED, "cppsharedlib_destroy_handles"))(handles); }
uintptr_t cppsharedlib_feval_with_completion(const uint64_t matlabHandle, const char* function, size_t nlhs, bool scalar,
                                             matlab::data::impl::ArrayImpl** args, size_t nrhs,
                                             void(*success)(void*, size_t, bool, matlab::data::impl::ArrayImpl**),
                                             void(*exception)(void*, size_t, bool, size_t, const void*),
                                             void* p, void* output, void* error, void(*write)(void*, const char16_t*, size_t),
                                             void(*deleter)(void*)) {
    _checklibs();
    return ((uintptr_t(*)(const uint64_t, const char*, size_t, bool, matlab::data::impl::ArrayImpl**, size_t,
                          void(*)(void*, size_t, bool, matlab::data::impl::ArrayImpl**),
                          void(*)(void*, size_t, bool, size_t, const void*), void*, void*, void*,
                          void(*)(void*, const char16_t*, size_t), void(*)(void*)))_resolve(_LIBCPPSHARED, "cppsharedlib_feval_with_completion"))
                          (matlabHandle, function, nlhs, scalar, args, nrhs, success, exception, p, output, error, write, deleter);
}
bool cppsharedlib_cancel_feval_with_completion(uintptr_t taskHandle, bool allowInteruption) {
    _checklibs(); return ((bool(*)(uintptr_t, bool))_resolve(_LIBCPPSHARED, "cppsharedlib_cancel_feval_with_completion"))(taskHandle, allowInteruption); }
void cppsharedlib_destroy_task_handle(uintptr_t taskHandle) {
    _checklibs(); return ((void(*)(uintptr_t))_resolve(_LIBCPPSHARED, "cppsharedlib_destroy_task_handle"))(taskHandle); }
size_t cppsharedlib_get_stacktrace_number(const uintptr_t frameHandle) {
    _checklibs(); return ((size_t(*)(const uintptr_t))_resolve(_LIBCPPSHARED, "cppsharedlib_get_stacktrace_number"))(frameHandle); }
const char* cppsharedlib_get_stacktrace_message(const uintptr_t frameHandle) {
    _checklibs(); return ((const char*(*)(const uintptr_t))_resolve(_LIBCPPSHARED, "cppsharedlib_get_stacktrace_message"))(frameHandle); }
const char16_t* cppsharedlib_get_stackframe_file(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((const char16_t*(*)(const uintptr_t, size_t))_resolve(_LIBCPPSHARED, "cppsharedlib_get_stackframe_file"))(frameHandle, frameNumber); }
const char* cppsharedlib_get_stackframe_func(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((const char*(*)(const uintptr_t, size_t))_resolve(_LIBCPPSHARED, "cppsharedlib_get_stackframe_func"))(frameHandle, frameNumber); }
uint64_t cppsharedlib_get_stackframe_line(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((uint64_t(*)(const uintptr_t, size_t))_resolve(_LIBCPPSHARED, "cppsharedlib_get_stackframe_line"))(frameHandle, frameNumber); }
int cppsharedlib_run_main(int(*mainfcn)(int, const char**), int argc, const char** argv) {
    _checklibs(); return ((int(*)(int(*)(int, const char**), int, const char**))_resolve(_LIBCPPSHARED, "cppsharedlib_run_main"))(mainfcn, argc, argv); }
// DATA_ARRAY
void* get_function_ptr(int fcn) { _checklibs(); return ((void*(*)(int))_resolve(_LIBDATAARRAY, "get_function_ptr"))(fcn); }


namespace libpymcr {

    size_t matlab_env::_parse_inputs(std::vector<matlab::data::Array>& m_args,
                         py::args py_args,
                         py::kwargs& py_kwargs) {
        matlab::data::ArrayFactory factory;
        size_t nargout = 1;
        for (auto item: py_args) {
            m_args.push_back(_converter.to_matlab(item.ptr()));
        }
        for (auto item: py_kwargs) {
            std::string key(py::str(item.first));
            if (key.find("nargout") == 0) {
                nargout = item.second.cast<size_t>();
            } else {
                m_args.push_back(factory.createCharArray(std::string(py::str(item.first))));
                m_args.push_back(_converter.to_matlab(item.second.ptr()));
            }
        }
        return nargout;
    }

    py::tuple matlab_env::feval(const std::u16string &funcname, py::args args, py::kwargs& kwargs) {
        // Calls Matlab function
        const size_t nlhs = 0;
        // Clears the streams
        _m_output.get()->str(std::basic_string<char16_t>());
        _m_error.get()->str(std::basic_string<char16_t>());
        // Determines and converts the number of inputs
        std::vector<matlab::data::Array> outputs;
        std::vector<matlab::data::Array> m_args;
        size_t nargout = _parse_inputs(m_args, args, kwargs);
        if (nargout == 1) {
            if (m_args.size() == 1) {
                outputs.push_back(_lib->feval(funcname, m_args[0], _m_output_buf, _m_error_buf));
            } else {
                outputs.push_back(_lib->feval(funcname, m_args, _m_output_buf, _m_error_buf));
            }
        } else {
            outputs = _lib->feval(funcname, nargout, m_args, _m_output_buf, _m_error_buf);
        }
        PyGILState_STATE gstate = PyGILState_Ensure(); // GIL{
        // Prints outputs and errors
        if(_m_output.get()->in_avail() > 0) {
            py::print(_m_output.get()->str(), py::arg("flush")=true); }
        if(_m_error.get()->in_avail() > 0) {
            py::print(_m_error.get()->str(), py::arg("file")=py::module::import("sys").attr("stderr"), py::arg("flush")=true); }
        // Converts outputs to Python types
        size_t n_out = outputs.size();
        py::tuple retval(n_out);
        for (size_t idx = 0; idx < n_out; idx++) {
            if (outputs[idx].getNumberOfElements() == 0) {
                retval[idx] = py::none();
            } else {
                // Call the CPython function directly because we _want_ to steal a ref to the output
                PyTuple_SetItem(retval.ptr(), idx, _converter.to_python(outputs[idx]));
            }
        }
        PyGILState_Release(gstate);  // GIL}
        // Now clear temporary Matlab arrays created from Numpy array data inputs
        _converter.clear_py_cache();
        return retval;
    }

    py::tuple matlab_env::call(py::args args, py::kwargs& kwargs) {
        // Note this function only works with libpace.ctf
        return feval(u"call", args, kwargs);
    }

    // Constructor
    matlab_env::matlab_env(const std::u16string ctfname, std::string matlabroot) {
        _loadlibraries(matlabroot);
    	    auto mode = matlab::cpplib::MATLABApplicationMode::IN_PROCESS;
    	    // Specify MATLAB startup options
    #ifdef __linux__
    	    std::vector<std::u16string> options = {u"-nodisplay"};
    #else
    	    std::vector<std::u16string> options = {u""};
    #endif
        _app = matlab::cpplib::initMATLABApplication(mode, options);
        _lib = matlab::cpplib::initMATLABLibrary(_app, ctfname);
        _converter = pymat_converter(pymat_converter::NumpyConversion::WRAP);
    }


} // namespace libpymcr


PYBIND11_MODULE(libpymcr, m) {
    py::class_<libpymcr::matlab_env>(m, "matlab")
        .def(py::init<const std::u16string, std::string>(),
             py::arg("ctfname")=u"libpace.ctf", py::arg("matlabroot")="/usr/local/MATLAB/R2020a/")
        .def("feval", &libpymcr::matlab_env::feval)
        .def("call", &libpymcr::matlab_env::call);
}


// Run in Python with:
//>>> p = libpace.pace()
//>>> p.call('call', 'help')

