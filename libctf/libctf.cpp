#include "MatlabCppSharedLib.hpp"
#include "pybind11/pybind11.h"
#include <iostream>

//#include "matpyconv.hpp"
/*
template <typename T> PyObject* matlab_to_python_t (const matlab::data::Array arr, py::handle owner);
template <> PyObject* matlab_to_python_t<char16_t>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<std::basic_string<char16_t>>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::dict>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::list>(const matlab::data::Array input, py::handle owner);
PyObject* matlab_to_python(const matlab::data::Array input, py::handle owner);
py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd=-1);
template <typename T> TypedArray<T> raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims, ssize_t *strides, matlab::data::ArrayFactory &factory);
template <typename T> TypedArray<T> raw_to_matlab_contiguous(T* begin, size_t sz, std::vector<size_t> dims, bool f_contigous, matlab::data::ArrayFactory &factory);
CellArray python_array_to_matlab(void *result, matlab::data::ArrayFactory &factory);
template <typename T> T convert_py_obj (PyObject *obj);
template <typename T> T convert_py_obj (PyObject *obj);
template <> int64_t convert_py_obj (PyObject *obj);
template <> double convert_py_obj (PyObject *obj);
template <> std::complex<double> convert_py_obj (PyObject *obj);
template <typename T> CellArray fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory);
CharArray python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
CellArray listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory);
StructArray python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
*/

// Compile with:
// g++ -g -o libpace$(python3-config --extension-suffix) -shared -fPIC libpace.cpp -I/usr/local/MATLAB/R2020a/extern/include/ -I/home/mdl27/src/pace-python/build_t/_deps/pybind11-src/include/ $(python3-config --includes) -lpthread

#include "pybind11/numpy.h"
//#include "pybind11/iostream.h"
#include <Python.h>
#include <algorithm>
#include <vector>
#include <stdexcept>
#include <cstring>
#include <sstream>
#include <dlfcn.h>

//using namespace pybind11::literals;

//#include "mex.hpp"
//#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include <Python.h>
#include <iostream>
#include <algorithm>
#include <vector>
#include <stdexcept>
#include <cstring>

#define MATLABERROR(errmsg) matlabPtr->feval(u"error", 0, std::vector<matlab::data::Array>({ factory.createScalar(errmsg) }));
#define MYINTEGER 1
#define MYFLOAT 2
#define MYCOMPLEX 4
#define MYOTHER 8

using namespace matlab::data;
//using matlab::mex::ArgumentList;
namespace py = pybind11;

template <typename T> PyObject* matlab_to_python_t (const matlab::data::Array arr, py::handle owner);
template <> PyObject* matlab_to_python_t<char16_t>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<std::basic_string<char16_t>>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::dict>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::list>(const matlab::data::Array input, py::handle owner);
PyObject* matlab_to_python(const matlab::data::Array input, py::handle owner);
//py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd=-1);
template <typename T> TypedArray<T> raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims, ssize_t *strides, matlab::data::ArrayFactory &factory);
template <typename T> TypedArray<T> raw_to_matlab_contiguous(T* begin, size_t sz, std::vector<size_t> dims, bool f_contigous, matlab::data::ArrayFactory &factory);
CellArray python_array_to_matlab(void *result, matlab::data::ArrayFactory &factory);
template <typename T> T convert_py_obj (PyObject *obj);
template <typename T> T convert_py_obj (PyObject *obj);
template <> int64_t convert_py_obj (PyObject *obj);
template <> double convert_py_obj (PyObject *obj);
template <> std::complex<double> convert_py_obj (PyObject *obj);
template <typename T> CellArray fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory);
CharArray python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
CellArray listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory);
StructArray python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);


// -------------------------------------------------------------------------------------------------------
// Code to translate Matlab types to Python types
// -------------------------------------------------------------------------------------------------------

// Wraps a Matlab array in a numpy array without copying (should work with all numeric types)
template <typename T> PyObject* matlab_to_python_t (const matlab::data::Array arr, py::handle owner) {
    std::vector<size_t> strides = {sizeof(T)};
    std::vector<size_t> dims = arr.getDimensions();
    if (arr.getMemoryLayout() == matlab::data::MemoryLayout::COLUMN_MAJOR) {
        for (size_t ii=0; ii<(dims.size()-1); ii++) {
            strides.push_back(dims[ii] * strides[ii]);
        }
    }
    else {
        strides.resize(dims.size(), sizeof(T));
        for (size_t ii=dims.size()-2; ii>=0; ii--) {
            strides[ii] = dims[ii+1] * strides[ii+1];
        }
    }
    // Needs to be const to avoid copying to a new (mutable) array
    const matlab::data::TypedArray<T> arr_t = matlab::data::TypedArray<T>(arr);
    // We need to pass a dummy python `base` object to own the reference otherwise PyBind will copy the data
    // See: https://github.com/pybind/pybind11/issues/323
    const T &tmp = *arr_t.begin();
    py::array_t<T> retval(dims, strides, (T*)(&tmp), owner);
    PyObject* rv = retval.ptr();
    Py_INCREF(rv);
    return rv;
}
// Specialisations for other types to generate the appropriate Python type
template <> PyObject* matlab_to_python_t<char16_t>(const matlab::data::Array input, py::handle owner) {
    const matlab::data::TypedArray<char16_t> str(input);
    return PyUnicode_FromKindAndData(2, (void*)(&(*str.begin())), str.getNumberOfElements());
}
template <> PyObject* matlab_to_python_t<std::basic_string<char16_t>>(const matlab::data::Array input, py::handle owner) {
    const matlab::data::TypedArray<matlab::data::MATLABString> str(input);
    if (input.getNumberOfElements() == 1) {
        const std::basic_string<char16_t> cstr(str[0]);
        return PyUnicode_FromKindAndData(2, (void*)cstr.c_str(), cstr.size());
    } else {
        PyObject* retval = PyList_New(0);
        for (auto mstr: str) {
            const std::basic_string<char16_t> cstr(mstr);
            if (PyList_Append(retval, PyUnicode_FromKindAndData(2, (void*)cstr.c_str(), cstr.size()))) {
                throw std::runtime_error("Error constructing python list from string array");
            }
        }
        return retval;
    }
}
PyObject* matlab_to_python(const matlab::data::Array input, py::handle owner); 
template <> PyObject* matlab_to_python_t<py::dict>(const matlab::data::Array input, py::handle owner) {
    const matlab::data::StructArray in_struct(input);
    if (input.getNumberOfElements() == 1) {
        PyObject* retval = PyDict_New();
        for (auto ky : in_struct.getFieldNames()) {
            PyObject* pyky = PyUnicode_FromString(std::string(ky).c_str());
            PyObject* pyval = matlab_to_python(in_struct[0][ky], owner);
            if (PyDict_SetItem(retval, pyky, pyval)) {
                throw std::runtime_error("Error constructing python dict from matlab struct");
            }
        }
        return retval;
    } else {
        PyObject* retval = PyList_New(0);
        for (auto struc : in_struct) {
            PyObject* elem = PyDict_New();
            for (auto ky : in_struct.getFieldNames()) {
                PyObject* pyky = PyUnicode_FromString(std::string(ky).c_str());
                PyObject* pyval = matlab_to_python(struc[ky], owner);
                if (PyDict_SetItem(elem, pyky, pyval)) {
                    throw std::runtime_error("Error constructing python dict from matlab struct");
                }
            }
            if (PyList_Append(retval, elem)) {
                throw std::runtime_error("Error constructing python list from struct array");
            }
        }
        return retval;
    }
}
template <> PyObject* matlab_to_python_t<py::list>(const matlab::data::Array input, py::handle owner) {
    const matlab::data::CellArray in_cell(input);
    PyObject* retval = PyList_New(0);
    for (auto elem : in_cell) {
        PyObject *val = matlab_to_python(elem, owner);
        if (PyList_Append(retval, val)) {
            throw std::runtime_error("Error constructing python list from cell array");
        }
    }
    return retval;
}

PyObject* matlab_to_python(const matlab::data::Array input, py::handle owner) {
    matlab::data::ArrayType type = input.getType();
    switch(type) {
        case matlab::data::ArrayType::DOUBLE:         return matlab_to_python_t<double>(input, owner);
        case matlab::data::ArrayType::SINGLE:         return matlab_to_python_t<float>(input, owner);
        case matlab::data::ArrayType::COMPLEX_SINGLE: return matlab_to_python_t<std::complex<float>>(input, owner);
        case matlab::data::ArrayType::COMPLEX_DOUBLE: return matlab_to_python_t<std::complex<double>>(input, owner);
        case matlab::data::ArrayType::LOGICAL:        return matlab_to_python_t<bool>(input, owner);
        case matlab::data::ArrayType::INT8:           return matlab_to_python_t<int8_t>(input, owner);
        case matlab::data::ArrayType::INT16:          return matlab_to_python_t<int16_t>(input, owner);
        case matlab::data::ArrayType::INT32:          return matlab_to_python_t<int32_t>(input, owner);
        case matlab::data::ArrayType::UINT8:          return matlab_to_python_t<uint8_t>(input, owner);
        case matlab::data::ArrayType::UINT16:         return matlab_to_python_t<uint16_t>(input, owner);
        case matlab::data::ArrayType::UINT32:         return matlab_to_python_t<uint32_t>(input, owner);
        case matlab::data::ArrayType::CHAR:           return matlab_to_python_t<char16_t>(input, owner);
        case matlab::data::ArrayType::MATLAB_STRING:  return matlab_to_python_t<std::basic_string<char16_t>>(input, owner);
        case matlab::data::ArrayType::STRUCT:         return matlab_to_python_t<py::dict>(input, owner);
        case matlab::data::ArrayType::CELL:           return matlab_to_python_t<py::list>(input, owner);
        default:
           throw std::runtime_error("Unrecognised input type");
    }
}

/*
py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd=-1) {
    // Note that this function must be called when we have the GIL
    size_t narg = inputs.size() + lastInd;
    py::tuple retval(narg);
    for (size_t idx = 1; idx <= narg; idx++) {
        retval[idx - 1] = matlab_to_python(inputs[idx], owner);
    }
    return retval;
}
*/

// -------------------------------------------------------------------------------------------------------
// Code to translate Python types to Matlab types
// -------------------------------------------------------------------------------------------------------

// Slower copy methods - follow data strides for non-contiguous arrays
template <typename T> TypedArray<T> raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims, ssize_t *strides, matlab::data::ArrayFactory &factory) {
    buffer_ptr_t<T> buf = factory.createBuffer<T>(sz);
    T* ptr = buf.get();
    std::vector<size_t> stride;
    std::vector<size_t> k = {dims[0]};
    for (size_t i=1; i<dims.size(); i++)
        k.push_back(k[i-1] * dims[i]);      // Cumulative product of dimensions
    for (size_t i=0; i<dims.size(); i++) {
        if (strides[i] > -1) 
            stride.push_back(static_cast<size_t>(strides[i]));
        else
            throw std::runtime_error("Invalid stride in numpy array");
    }
    for (size_t i=0; i<sz; i++) {
        size_t offset = 0, idx = i, vi;
        // This computes the N-Dim indices (i0,i1,i2,...) and multiplies it by the strides
        // The algorithm is taken from the ind2sub.m function in Matlab
        for (size_t d=dims.size(); d>0; d--) {
            vi = idx % k[d-1];
            offset += ((idx - vi) / k[d-1]) * stride[d];
            idx = vi;
        }
        offset += vi * stride[0];
        ptr[i] = *((T*)(raw + offset));
    }
    return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::COLUMN_MAJOR);
}

// Fast method block memory copy for contigous C- or Fortran-style arrays
template <typename T> TypedArray<T> raw_to_matlab_contiguous(T* begin, size_t sz, std::vector<size_t> dims, bool f_contigous, matlab::data::ArrayFactory &factory) {
    buffer_ptr_t<T> buf = factory.createBuffer<T>(sz);
    memcpy(buf.get(), begin, sz * sizeof(T));
    if (f_contigous) {
        return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::COLUMN_MAJOR);
    } else {
        return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::ROW_MAJOR);
    }
}

CellArray python_array_to_matlab(void *result, matlab::data::ArrayFactory &factory) {
    // Cast the result to the PyArray C struct and its corresponding dtype struct
    py::detail::PyArray_Proxy *arr = py::detail::array_proxy(result);
    py::detail::PyArrayDescr_Proxy *dtype = py::detail::array_descriptor_proxy(arr->descr);
    if (arr->nd == 0) {            // 0-dimensional array - return a scalar
        if (dtype->kind == 'f') {
            if (dtype->elsize == sizeof(double)) return factory.createCellArray({1, 1}, factory.createScalar(*((double*)(arr->data))));
            else if (dtype->elsize == sizeof(float)) return factory.createCellArray({1, 1}, factory.createScalar(*((float*)(arr->data))));
        } else if (dtype->kind == 'c') {
            if (dtype->elsize == sizeof(std::complex<double>)) return factory.createCellArray({1, 1}, factory.createScalar(*((std::complex<double>*)(arr->data))));
            else if (dtype->elsize == sizeof(std::complex<float>)) return factory.createCellArray({1, 1}, factory.createScalar(*((std::complex<float>*)(arr->data))));
        }
    }
    std::vector<size_t> dims;
    size_t numel = 1;
    for (size_t id = 0; id < arr->nd; id++) {
        dims.push_back(arr->dimensions[id]);
        numel = numel * dims[id];
    }
    int f_or_c_contiguous = 0;
    if (py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_F_CONTIGUOUS_))
        f_or_c_contiguous = -1;
    else if (py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_C_CONTIGUOUS_))
        f_or_c_contiguous = 1;

    char *begin = arr->data;
    if (dtype->kind == 'f') {       // Floating point array
        if (dtype->elsize == sizeof(double)) {
            if (f_or_c_contiguous)
                return factory.createCellArray({1, 1}, raw_to_matlab_contiguous((double*)begin, numel, dims, f_or_c_contiguous==-1, factory));
            else
                return factory.createCellArray({1, 1}, raw_to_matlab<double>(begin, numel, dims, arr->strides, factory));
        }
        else if(dtype->elsize == sizeof(float)) {
            if (f_or_c_contiguous)
                return factory.createCellArray({1, 1}, raw_to_matlab_contiguous((float*)begin, numel, dims, f_or_c_contiguous==-1, factory));
            else
                return factory.createCellArray({1, 1}, raw_to_matlab<float>(begin, numel, dims, arr->strides, factory));
        }
    }
    else if (dtype->kind == 'c') {  // Complex array
        if (dtype->elsize == sizeof(std::complex<double>)) {
            if (f_or_c_contiguous)
                return factory.createCellArray({1, 1}, raw_to_matlab_contiguous((std::complex<double>*)begin, numel, dims, f_or_c_contiguous==-1, factory));
            else
                return factory.createCellArray({1, 1}, raw_to_matlab<std::complex<double>>(begin, numel, dims, arr->strides, factory));
        }
        else if(dtype->elsize == sizeof(std::complex<float>)) {
            if (f_or_c_contiguous)
                return factory.createCellArray({1, 1}, raw_to_matlab_contiguous((std::complex<float>*)begin, numel, dims, f_or_c_contiguous==-1, factory));
            else
                return factory.createCellArray({1, 1}, raw_to_matlab<std::complex<float>>(begin, numel, dims, arr->strides, factory));
        }
    }
    else
        throw std::runtime_error("Python function returned a non-floating point array.");
}

template <typename T> T convert_py_obj (PyObject *obj) {
    throw std::runtime_error("Unrecognised Python type"); }
template <> int64_t convert_py_obj (PyObject *obj) {
    return PyLong_AsLong(obj); }
template <> double convert_py_obj (PyObject *obj) {
    return PyFloat_AsDouble(obj); }
template <> std::complex<double> convert_py_obj (PyObject *obj) {
    return std::complex<double>(PyComplex_RealAsDouble(obj), PyComplex_ImagAsDouble(obj)); }

template <typename T> CellArray fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory) {
    std::vector<T> vec;
    vec.resize(objs.size());
    std::transform (objs.begin(), objs.end(), vec.begin(), convert_py_obj<T>);
    return factory.createCellArray({1, 1}, factory.createArray<T>({1, vec.size()}, (T*)(&(*vec.begin())), (T*)(&(*vec.end()))));
}

CharArray python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory) {
    Py_ssize_t str_sz;
    const char *str = PyUnicode_AsUTF8AndSize(result, &str_sz);
    if (!str) {
        PyErr_Print();
        throw std::runtime_error("Cannot create string from pyobject");
    }
    return factory.createCharArray(std::string(str, str_sz));
}

CellArray listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory);
StructArray python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory) {
    Py_ssize_t pos = 0;
    PyObject *key, *val;
    std::vector<std::string> keys;
    std::vector<PyObject*> vals;
    while (PyDict_Next(result, &pos, &key, &val)) {
        Py_ssize_t str_sz;
        const char *str = PyUnicode_AsUTF8AndSize(key, &str_sz);
        if (!str) {
            throw std::runtime_error("Can only convert python dict with string keys to Matlab struct");
        }
        keys.push_back(std::string(str, str_sz));
        vals.push_back(val);
    }
    StructArray retval = factory.createStructArray({1,1}, keys);
    auto npy_api = py::detail::npy_api::get();
    for (size_t ii=0; ii<keys.size(); ii++) {
        bool is_arr = npy_api.PyArray_Check_(vals[ii]);
        if (is_arr) {
            retval[0][keys[ii]] = python_array_to_matlab((void*)vals[ii], factory);
        } else if (PyTuple_Check(vals[ii]) || PyList_Check(vals[ii])) {
            retval[0][keys[ii]] = listtuple_to_cell(vals[ii], factory);
        } else if (PyUnicode_Check(vals[ii])) {
            retval[0][keys[ii]] = python_string_to_matlab(vals[ii], factory);
        } else if (vals[ii] == Py_None) {
            retval[0][keys[ii]] = factory.createArray<double>({0});
        } else if (PyLong_Check(vals[ii])) {
            retval[0][keys[ii]] = factory.createScalar<int64_t>(PyLong_AsLong(vals[ii]));
        } else if (PyFloat_Check(vals[ii])) {
            retval[0][keys[ii]] = factory.createScalar<double>(PyFloat_AsDouble(vals[ii]));
        } else if (PyComplex_Check(vals[ii])) {
            retval[0][keys[ii]] = factory.createScalar(std::complex<double>(PyComplex_RealAsDouble(vals[ii]), PyComplex_ImagAsDouble(vals[ii])));
        } else {
            throw std::runtime_error("Unknown dict item type from Python function.");
        }
    }
    return retval;
}

CellArray listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory) {
    size_t obj_size = PyTuple_Check(result) ? (size_t)PyTuple_Size(result) : (size_t)PyList_Size(result);
    CellArray cell_out = factory.createCellArray({1, obj_size});
    auto npy_api = py::detail::npy_api::get();
    std::vector<PyObject*> objs;
    int typeflags = 0;
    for(size_t ii=0; ii<obj_size; ii++) {
        PyObject *item = PyTuple_Check(result) ? PyTuple_GetItem(result, ii) : PyList_GetItem(result, ii);
        bool is_arr = npy_api.PyArray_Check_(item);
        if (is_arr) {
            cell_out[0][ii] = python_array_to_matlab((void*)item, factory);
            typeflags |= MYOTHER;
        } else if (PyTuple_Check(item) || PyList_Check(item)) {
            cell_out[0][ii] = listtuple_to_cell(item, factory);
            typeflags |= MYOTHER;
        } else if (PyUnicode_Check(item)) {
            cell_out[0][ii] = python_string_to_matlab(item, factory);
            typeflags |= MYOTHER;
        } else if (PyDict_Check(item)) {
            cell_out[0][ii] = python_dict_to_matlab(item, factory);
            typeflags |= MYOTHER;
        } else if (item == Py_None) {
            cell_out[0][ii] = factory.createArray<double>({0});
            typeflags |= MYOTHER;
        } else if (PyLong_Check(item)) {
            cell_out[0][ii] = factory.createScalar<int64_t>(PyLong_AsLong(item));
            typeflags |= MYINTEGER;
            objs.push_back(item);
        } else if (PyFloat_Check(item)) {
            cell_out[0][ii] = factory.createScalar<double>(PyFloat_AsDouble(item));
            typeflags |= MYFLOAT;
            objs.push_back(item);
        } else if (PyComplex_Check(item)) {
            cell_out[0][ii] = factory.createScalar(std::complex<double>(PyComplex_RealAsDouble(item), PyComplex_ImagAsDouble(item)));
            typeflags |= MYCOMPLEX;
            objs.push_back(item);
        } else {
            throw std::runtime_error("Unknown return type from Python function.");
        }
    }
    if (typeflags == MYINTEGER) {
        return fill_vec_from_pyobj<int64_t>(objs, factory);
    } else if (typeflags == MYFLOAT) {
        return fill_vec_from_pyobj<double>(objs, factory);
    } else if (typeflags == MYCOMPLEX) {
        return fill_vec_from_pyobj<std::complex<double>>(objs, factory);
    } else {
        // We've got mixed or nonnumeric types - return a cell array of the elements
        return cell_out;
    }
}

// Imported Matlab functions
#include <dlfcn.h>

// Global declaration of libraries
void *_LIBDATAARRAY, *_LIBENGINE, *_LIBCPPSHARED;

void _loadlibraries(std::string matlabroot) {
    if (!_LIBCPPSHARED) {
        _LIBDATAARRAY = dlopen((matlabroot + "/extern/bin/glnxa64/libMatlabDataArray.so").c_str(), RTLD_LAZY);
        if (!_LIBDATAARRAY) { throw std::runtime_error("Cannot load libMatlabDataArray.so"); }
        _LIBENGINE = dlopen((matlabroot +  "/extern/bin/glnxa64/libMatlabEngine.so").c_str(), RTLD_LAZY);
        if (!_LIBENGINE) { throw std::runtime_error("Cannot load libMatlabEngine.so"); }
        _LIBCPPSHARED = dlopen((matlabroot + "/runtime/glnxa64/libMatlabCppSharedLib.so").c_str(), RTLD_LAZY);
        if (!_LIBCPPSHARED) { throw std::runtime_error("Cannot load libMatlabCppSharedLib.so"); }
    }
}
void _checklibs() {
    if (!_LIBDATAARRAY || !_LIBENGINE || !_LIBCPPSHARED) {
        throw std::runtime_error("Matlab libraries must be initialised first.");
    }
}
// Utils
void util_destroy_utf8(char* utf8) {
    _checklibs();
    return ((void(*)(char*))dlsym(_LIBCPPSHARED, "util_destroy_utf8"))(utf8);
    //void (*f)(char*) = (void(*)(char*))dlsym(_LIBCPPSHARED, "util_destroy_utf8");
    //if (!f) { throw std::runtime_error("Cannot find util_destroy_utf8"); }
    //return f(utf8);
}
void util_destroy_utf16(char16_t* utf16) { _checklibs(); return ((void(*)(char16_t*))dlsym(_LIBCPPSHARED, "util_destroy_utf16"))(utf16); }
void util_utf8_to_utf16(const char* utf8, char16_t** utf16, size_t* errType) {
    _checklibs(); return ((void(*)(const char*, char16_t**, size_t*))dlsym(_LIBCPPSHARED, "util_utf8_to_utf16"))(utf8, utf16, errType); }
void util_utf16_to_utf8(const char16_t* utf16, char** utf8, size_t* errType) {
    _checklibs(); return ((void(*)(const char16_t*, char**, size_t*))dlsym(_LIBCPPSHARED, "util_utf16_to_utf8"))(utf16, utf8, errType); }
// CPP_SHARED_LIB
void runtime_create_session(char16_t** options, size_t size) {
    _checklibs(); return ((void(*)(char16_t**, size_t))dlsym(_LIBCPPSHARED, "runtime_create_session"))(options, size); }
void runtime_terminate_session() { _checklibs(); return ((void(*)())dlsym(_LIBCPPSHARED, "runtime_terminate_session"))(); }
uint64_t create_mvm_instance_async(const char16_t* name) {
    _checklibs(); return ((uint64_t(*)(const char16_t*))dlsym(_LIBCPPSHARED, "create_mvm_instance_async"))(name); }
uint64_t create_mvm_instance(const char16_t* name, bool* errFlag) {
    _checklibs(); return ((uint64_t(*)(const char16_t*, bool*))dlsym(_LIBCPPSHARED, "create_mvm_instance"))(name, errFlag); }
void terminate_mvm_instance(const uint64_t mvmHandle) {
    _checklibs(); return ((void(*)(const uint64_t))dlsym(_LIBCPPSHARED, "terminate_mvm_instance"))(mvmHandle); }
void wait_for_figures_to_close(const uint64_t mvmHandle) {
    _checklibs(); return ((void(*)(const uint64_t))dlsym(_LIBCPPSHARED, "wait_for_figures_to_close"))(mvmHandle); }
void cppsharedlib_destroy_handles(uintptr_t* handles) {
    _checklibs(); return ((void(*)(uintptr_t*))dlsym(_LIBCPPSHARED, "cppsharedlib_destroy_handles"))(handles); }
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
                          void(*)(void*, const char16_t*, size_t), void(*)(void*)))dlsym(_LIBCPPSHARED, "cppsharedlib_feval_with_completion"))
                          (matlabHandle, function, nlhs, scalar, args, nrhs, success, exception, p, output, error, write, deleter);
}
bool cppsharedlib_cancel_feval_with_completion(uintptr_t taskHandle, bool allowInteruption) {
    _checklibs(); return ((bool(*)(uintptr_t, bool))dlsym(_LIBCPPSHARED, "cppsharedlib_cancel_feval_with_completion"))(taskHandle, allowInteruption); }
void cppsharedlib_destroy_task_handle(uintptr_t taskHandle) {
    _checklibs(); return ((void(*)(uintptr_t))dlsym(_LIBCPPSHARED, "cppsharedlib_destroy_task_handle"))(taskHandle); }
size_t cppsharedlib_get_stacktrace_number(const uintptr_t frameHandle) {
    _checklibs(); return ((size_t(*)(const uintptr_t))dlsym(_LIBCPPSHARED, "cppsharedlib_get_stacktrace_number"))(frameHandle); }
const char* cppsharedlib_get_stacktrace_message(const uintptr_t frameHandle) {
    _checklibs(); return ((const char*(*)(const uintptr_t))dlsym(_LIBCPPSHARED, "cppsharedlib_get_stacktrace_message"))(frameHandle); }
const char16_t* cppsharedlib_get_stackframe_file(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((const char16_t*(*)(const uintptr_t, size_t))dlsym(_LIBCPPSHARED, "cppsharedlib_get_stackframe_file"))(frameHandle, frameNumber); }
const char* cppsharedlib_get_stackframe_func(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((const char*(*)(const uintptr_t, size_t))dlsym(_LIBCPPSHARED, "cppsharedlib_get_stackframe_func"))(frameHandle, frameNumber); }
uint64_t cppsharedlib_get_stackframe_line(const uintptr_t frameHandle, size_t frameNumber) {
    _checklibs(); return ((uint64_t(*)(const uintptr_t, size_t))dlsym(_LIBCPPSHARED, "cppsharedlib_get_stackframe_line"))(frameHandle, frameNumber); }
int cppsharedlib_run_main(int(*mainfcn)(int, const char**), int argc, const char** argv) {
    _checklibs(); return ((int(*)(int(*)(int, const char**), int, const char**))dlsym(_LIBCPPSHARED, "cppsharedlib_run_main"))(mainfcn, argc, argv); }
// ENGINE
void cpp_engine_create_session() { _checklibs(); return ((void(*)())dlsym(_LIBENGINE, "cpp_engine_create_session"))(); }
uint64_t cpp_engine_create_out_of_process_matlab(char16_t** options, size_t size, bool* errFlag) {
    _checklibs(); return ((uint64_t(*)(char16_t**, size_t, bool*))dlsym(_LIBENGINE, "cpp_engine_create_out_of_process_matlab"))(options, size, errFlag); }
uint64_t cpp_engine_attach_shared_matlab(const char16_t* name, bool* errFlag) {
    _checklibs(); return ((uint64_t(*)(const char16_t*, bool*))dlsym(_LIBENGINE, "cpp_engine_attach_shared_matlab"))(name, errFlag); }
size_t cpp_engine_find_shared_matlab(char16_t*** names) {
    _checklibs(); return ((size_t(*)(char16_t***))dlsym(_LIBENGINE, "cpp_engine_find_shared_matlab"))(names); }
void cpp_engine_destroy_names(char16_t** names, size_t size) {
    _checklibs(); return ((void(*)(char16_t**, size_t))dlsym(_LIBENGINE, "cpp_engine_destroy_names"))(names, size); }
void cpp_engine_destroy_handles(uintptr_t* handles) {
    _checklibs(); return ((void(*)(uintptr_t*))dlsym(_LIBENGINE, "cpp_engine_destroy_handles"))(handles); }
uintptr_t cpp_engine_feval_with_completion(const uint64_t matlabHandle, const char* function, size_t nlhs, bool scalar,
                                           matlab::data::impl::ArrayImpl** args, size_t nrhs,
                                           void(*success)(void*, size_t, bool, matlab::data::impl::ArrayImpl**),
                                           void(*exception)(void*, size_t, bool, size_t, const void*),
                                           void* p, void* output, void* error,
                                           void(*write)(void*, const char16_t*, size_t), void(*deleter)(void*)) {
    _checklibs();
    return ((uintptr_t(*)(const uint64_t, const char*, size_t, bool, matlab::data::impl::ArrayImpl**, size_t,
                          void(*)(void*, size_t, bool, matlab::data::impl::ArrayImpl**),
                          void(*)(void*, size_t, bool, size_t, const void*), void*, void*, void*,
                          void(*)(void*, const char16_t*, size_t), void(*)(void*)))dlsym(_LIBENGINE, "cpp_engine_feval_with_completion"))
                          (matlabHandle, function, nlhs, scalar, args, nrhs, success, exception, p, output, error, write, deleter);
}
void cpp_engine_eval_with_completion(const uint64_t matlabHandle, const char16_t* statement, void(*success)(void*), void(*exception)(void*, size_t, const void*),
                                     void* p, void* output, void* error, void(*write)(void*, const char16_t*, size_t), void(*deleter)(void*), uintptr_t** handles) {
    _checklibs();
    return ((void(*)(const uint64_t, const char16_t*, void(*)(void*), void(*)(void*, size_t, const void*), void*, void*, void*,
                     void(*)(void*, const char16_t*, size_t), void(*)(void*), uintptr_t**))dlsym(_LIBENGINE, "cpp_engine_eval_with_completion"))
                     (matlabHandle, statement, success, exception, p, output, error, write, deleter, handles);
}
bool cpp_engine_cancel_feval_with_completion(uintptr_t taskHandle, bool allowInteruption) {
    _checklibs(); return ((bool(*)(uintptr_t, bool))dlsym(_LIBENGINE, "cpp_engine_cancel_feval_with_completion"))(taskHandle, allowInteruption); }
void cpp_engine_destroy_task_handle(uintptr_t taskHandle) {
    _checklibs(); return ((void(*)(uintptr_t))dlsym(_LIBENGINE, "cpp_engine_destroy_task_handle"))(taskHandle); }
void cpp_engine_terminate_out_of_process_matlab(const uint64_t matlabHandle) {
    _checklibs(); return ((void(*)(const uintptr_t))dlsym(_LIBENGINE, "cpp_engine_terminate_out_of_process_matlab"))(matlabHandle); }
void cpp_engine_terminate_session() {
    _checklibs(); return ((void(*)())dlsym(_LIBENGINE, "cpp_engine_terminate_session"))(); }
void* cpp_engine_get_function_ptr(int fcn) {
    _checklibs(); return ((void*(*)(int))dlsym(_LIBENGINE, "cpp_engine_get_function_ptr"))(fcn); }
// DATA_ARRAY
void* get_function_ptr(int fcn) { _checklibs(); return ((void*(*)(int))dlsym(_LIBDATAARRAY, "get_function_ptr"))(fcn); }


// -------------------------

namespace py = pybind11;
typedef std::basic_streambuf<char16_t> StreamBuffer;
typedef std::basic_stringbuf<char16_t> StringBuffer;

namespace libPace {

class pacecpp {
    protected:
    // Properties
    std::shared_ptr<matlab::cpplib::MATLABApplication> _app;
    std::unique_ptr<matlab::cpplib::MATLABLibrary> _lib;
    //matlab::data::ArrayFactory _factory;
    //std::basic_stringstream<char16_t> _outputstream, _errorstream;
    std::shared_ptr<StringBuffer> _m_output = std::make_shared<StringBuffer>();
    std::shared_ptr<StringBuffer> _m_error = std::make_shared<StringBuffer>();
    std::shared_ptr<StreamBuffer> _m_output_buf = std::static_pointer_cast<StreamBuffer>(_m_output);
    std::shared_ptr<StreamBuffer> _m_error_buf = std::static_pointer_cast<StreamBuffer>(_m_error);
    PyObject* _parent = PyList_New(1);

    matlab::data::Array _convert_to_matlab(PyObject *input) {
        matlab::data::ArrayFactory factory;
        matlab::data::Array output;
        auto npy_api = py::detail::npy_api::get();
        bool is_arr = npy_api.PyArray_Check_(input);
        if (is_arr) {
            output = python_array_to_matlab((void*)input, factory);
        } else if (PyTuple_Check(input) || PyList_Check(input)) {
            output = listtuple_to_cell(input, factory);
        } else if (PyUnicode_Check(input)) {
            output = python_string_to_matlab(input, factory);
        } else if (PyDict_Check(input)) {
            output = python_dict_to_matlab(input, factory);
        } else if (input != Py_None) {
            throw std::runtime_error("Unrecognised Python type");
        }
        return output;
    }

    size_t _parse_inputs(std::vector<matlab::data::Array>& m_args,
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

    public:
    // Calls Matlab function
    py::tuple call(const std::u16string &funcname, py::args args, py::kwargs& kwargs) {
        const size_t nlhs = 0;
        // Clears the streams
        //_outputstream.str(std::basic_string<char16_t>());
        //_errorstream.str(std::basic_string<char16_t>());
        // Runs the command and returns the output string
        //std::vector<matlab::data::Array> args = {_factory.createCharArray(arg)};
        //_lib->feval(funcname, nlhs, args, _outputstream_buf, _errorstream_buf);
        //return _outputstream.str();
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
        py::print(_m_output.get()->str(), py::arg("flush")=true);
        py::print(_m_error.get()->str(), py::arg("file")=py::module::import("sys").attr("stderr"), py::arg("flush")=true);
        // Converts outputs to Python types
        size_t n_out = outputs.size();
        py::tuple retval(n_out);
        for (size_t idx = 0; idx < n_out; idx++) {
            if (outputs[idx].getNumberOfElements() == 0) {
                retval[idx] = py::none();
            } else {
                retval[idx] = matlab_to_python(outputs[idx], _parent);
            }
        }
        PyGILState_Release(gstate);  // GIL}
        return retval;
    }

    // Constructor
    //pacecpp(std::string matlabroot = "/usr/local/MATLAB/R2020a/") {
    pacecpp(std::string matlabroot) { 
        _loadlibraries(matlabroot);
	    auto mode = matlab::cpplib::MATLABApplicationMode::IN_PROCESS;
	    // Specify MATLAB startup options
	    std::vector<std::u16string> options = {u"-nodisplay"};
        _app = matlab::cpplib::initMATLABApplication(mode, options);
        _lib = matlab::cpplib::initMATLABLibrary(_app, u"libpace.ctf");
        //_outputstream_buf = std::shared_ptr<StreamBuffer>(_outputstream.rdbuf());
        //_errorstream_buf = std::shared_ptr<StreamBuffer>(_errorstream.rdbuf());
    }
};

PYBIND11_MODULE(libpace, m) {
    py::class_<pacecpp>(m, "pace")
        .def(py::init<std::string>(), py::arg("matlabroot")="/usr/local/MATLAB/R2020a/")
        .def("call", &pacecpp::call);
}

}

// Run in Python with:
//>>> p = libpace.pace()
//>>> p.call('call', 'help')

