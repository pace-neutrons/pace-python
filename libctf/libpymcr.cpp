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


namespace {
    void _destroy_array(PyObject *capsule) {
        // Deleter function for matlab array outputs which are wrapped as numpy arrays
        const char* name = PyCapsule_GetName(capsule);
        if(std::strncmp(name, "mw", 2) == 0) {
            void* addr = PyCapsule_GetPointer(capsule, name);
            static_cast<std::map<std::string, matlab::data::Array>*>(addr)->erase(std::string(name));
        }
    }
}

namespace libpymcr {


    template <typename T> TypedArray<T> matlab_env::_to_matlab_nocopy(T* begin, std::vector<size_t> dims, bool f_contigous, matlab::data::ArrayFactory &factory) {
        // Creates a Matlab Array from POD without copying using createArrayFromBuffer(), but as
        // noted here: https://www.mathworks.com/matlabcentral/answers/514456 this causes an issue
        // when Matlab tries to delete the buffer. Now it seems that ROW_MAJOR (C-style) arrays use
        // a new type which supports custom deleter, but COLUMN_MAJOR (Fortran-style) arrays are
        // just wrappers around the old mxArray type which has its own (static) deleter.
        buffer_ptr_t<T> buf = buffer_ptr_t<T>(begin, [](void* ptr){});
        if (f_contigous || dims.size() == 1) {
            return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::COLUMN_MAJOR);
        } else {
            return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::ROW_MAJOR);
        }
    }

    void matlab_env::_release_buffer(matlab::data::Array arr) {
        // Hack to safely release a buffer for a no-copy Matlab array converted from numpy
        if (arr.getMemoryLayout() == matlab::data::MemoryLayout::ROW_MAJOR) {
            // Row-major arrays use a new format (not a wrapped mxArray) which accepts a custom deleter
            // so we don't need to hack it
            return;
        }
        // For Column-major arrays, which are wrappers around a mxArray type, we have to use a hack
        // where we create a small buffer using createBuffer() and overwrite the mxArray->pr pointer
        // to point to this instead of the numpy array. Then when this array is deleted Matlab will
        // free the newly created buffer instead of the numpy array and cause a heap memory error
        matlab::data::ArrayFactory factory;
        matlab::data::impl::ArrayImpl* imp = matlab::data::detail::Access::getImpl<matlab::data::impl::ArrayImpl>(arr);
        struct impl_header_col_major* m0 = static_cast<struct impl_header_col_major*>(static_cast<void*>(imp));
        struct impl_header_col_major* m1 = static_cast<struct impl_header_col_major*>(m0->data_ptr);
        struct mxArray_header_2020a* mx = static_cast<struct mxArray_header_2020a*>(m1->mxArray);
        buffer_ptr_t<double> buf = factory.createBuffer<double>(1);
        // Hack - switch the memory for a Matlab created buffer
        mx->pr = static_cast<void*>(buf.release());
    }

    matlab::data::Array matlab_env::_numpy_array_to_matlab(void *result, matlab::data::ArrayFactory &factory) {
        // Cast the result to the PyArray C struct and its corresponding dtype struct
        py::detail::PyArray_Proxy *arr = py::detail::array_proxy(result);
        py::detail::PyArrayDescr_Proxy *dtype = py::detail::array_descriptor_proxy(arr->descr);

        if (arr->nd > 0 &&
            (py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_F_CONTIGUOUS_) ||
             py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_C_CONTIGUOUS_)) ) {
            bool f_contigous = py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_F_CONTIGUOUS_);
            std::vector<size_t> dims;
            for (size_t id = 0; id < arr->nd; id++) {
                dims.push_back(arr->dimensions[id]);
            }
            matlab::data::Array rv;
            if (dtype->kind == 'f')         // Floating point array
                rv = _to_matlab_nocopy((double*)arr->data, dims, f_contigous, factory);
            else if (dtype->kind == 'c')    // Complex array
                rv = _to_matlab_nocopy((std::complex<double>*)arr->data, dims, f_contigous, factory);
            else
                throw std::runtime_error("Non-floating point numpy array inputs not allowed.");
            _input_cache.push_back(rv);     // Make a shared data copy
            return rv;
        } else {
            return python_array_to_matlab(result, factory);
        }
    }

    matlab::data::Array matlab_env::_wrap_python_function(PyObject *input) {
        // Wraps a Python function so it can be called using a mex function
        throw std::runtime_error("Not implemented");
    }

    matlab::data::Array matlab_env::_convert_to_matlab(PyObject *input) {
        matlab::data::ArrayFactory factory;
        matlab::data::Array output;
        auto npy_api = py::detail::npy_api::get();
        bool is_arr = npy_api.PyArray_Check_(input);
        if (is_arr) {
            output = _numpy_array_to_matlab((void*)input, factory);
        } else if (PyTuple_Check(input) || PyList_Check(input)) {
            output = listtuple_to_cell(input, factory);
        } else if (PyUnicode_Check(input)) {
            output = python_string_to_matlab(input, factory);
        } else if (PyDict_Check(input)) {
            output = python_dict_to_matlab(input, factory);
        } else if (PyLong_Check(input)) {
            output = factory.createScalar<int64_t>(PyLong_AsLong(input));
        } else if (PyFloat_Check(input)) {
            output = factory.createScalar<double>(PyFloat_AsDouble(input));
        } else if (PyComplex_Check(input)) {
            output = factory.createScalar(std::complex<double>(PyComplex_RealAsDouble(input), PyComplex_ImagAsDouble(input)));
        } else if (input == Py_None) {
            output = factory.createArray<double>({0});
        } else if (PyCallable_Check(input)) {
            output = _wrap_python_function(input);
        } else if (PyObject_TypeCheck(input, _py_matlab_wrapper_t)) {
            output = ((matlab_wrapper*)input)->matlab_array;
        } else {
            throw std::runtime_error("Unrecognised Python type");
        }
        return output;
    }

    size_t matlab_env::_parse_inputs(std::vector<matlab::data::Array>& m_args,
                         py::args py_args,
                         py::kwargs& py_kwargs) {
        matlab::data::ArrayFactory factory;
        size_t nargout = 1;
        for (auto item: py_args) {
            m_args.push_back(_convert_to_matlab(item.ptr()));
        }
        for (auto item: py_kwargs) {
            std::string key(py::str(item.first));
            if (key.find("nargout") == 0) {
                nargout = item.second.cast<size_t>();
            } else {
                m_args.push_back(factory.createCharArray(std::string(py::str(item.first))));
                m_args.push_back(_convert_to_matlab(item.second.ptr()));
            }
        }
        return nargout;
    }

    char* matlab_env::_get_next_cached_id() {
        // We need to cache Matlab created Arrays in this class as we wrap numpy arrays around its data
        // and need to ensure that the matlab::data::Arrays are not deleted before the numpy arrays
        char* next = new char[10]();  // Enough for 1e8 variables
        std::strcpy(next, std::string("mw" + std::to_string(_cache_indices.size())).c_str());
        _cache_indices.push_back(next);
        return _cache_indices.back();
    }

    PyObject* matlab_env::_matlab_to_python(matlab::data::Array input) {
        matlab::data::ArrayType type = input.getType();
        PyObject *rv;
        if (type == matlab::data::ArrayType::CHAR || type == matlab::data::ArrayType::MATLAB_STRING) {
            // For strings we construct new PyObjects by copying, no need to cache
            rv = matlab_to_python(input, _parent);
        } else if (type == matlab::data::ArrayType::VALUE_OBJECT || type == matlab::data::ArrayType::HANDLE_OBJECT_REF) {
            // Wrap a Matlab class in an opaque Python container
            matlab_wrapper* container = PyObject_New(matlab_wrapper, _py_matlab_wrapper_t);
            container->matlab_array = input;
            rv = (PyObject*) container;
        } else {
            char* id = _get_next_cached_id();
            _cached_arrays[std::string(id)] = input;
            // We create a PyCapsule with its deleter knowning how to delete the Matlab array whose
            // data we are wrapping in a numpy array so it is not deleted while the numpy one exists
            // https://numpy.org/devdocs/reference/c-api/data_memory.html
            PyObject *owner = PyCapsule_New(static_cast<void*>(&_cached_arrays), id, _destroy_array);
            rv = matlab_to_python(input, owner);
            // PyBind auto increfs the base because PyArray_SetBaseObject steals the ref - but we want this
            Py_DECREF(owner);
        }
        return rv;
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
                PyTuple_SetItem(retval.ptr(), idx, _matlab_to_python(outputs[idx]));
            }
        }
        PyGILState_Release(gstate);  // GIL}
        // Now clear temporary Matlab arrays created from Numpy array data inputs
        for (size_t ii = 0; ii < _input_cache.size(); ii++) {
            _release_buffer(_input_cache[ii]);
        }
        _input_cache.clear();
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
        _py_matlab_wrapper_t = (PyTypeObject*) PyType_FromSpec(&spec_matlab_wrapper);
    }

    matlab_env::~matlab_env() {
        // Renames the cache indices to invalidate them to ensure we don't double free
        for (size_t ii=0; ii<_cache_indices.size(); ii++) {
            strcpy(_cache_indices[ii], std::string("x" + std::to_string(ii)).c_str());
        }
    }

}


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

