#include "mex.hpp"
#include "mexAdapter.hpp"
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
using matlab::mex::ArgumentList;
namespace py = pybind11;

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

py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd=-1) {
    // Note that this function must be called when we have the GIL
    size_t narg = inputs.size() + lastInd;
    py::tuple retval(narg);
    for (size_t idx = 1; idx <= narg; idx++) {
        retval[idx - 1] = matlab_to_python(inputs[idx], owner);
    }
    return retval;
}

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

// -------------------------------------------------------------------------------------------------------
// Mex class to run Python function referenced in a global dictionary
// -------------------------------------------------------------------------------------------------------

class MexFunction : public matlab::mex::Function {

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            std::shared_ptr<matlab::engine::MATLABEngine> matlabPtr = getEngine();
            matlab::data::ArrayFactory factory;
            if (inputs.size() < 1 ||
                inputs[0].getType() != matlab::data::ArrayType::CHAR) {
                    MATLABERROR("First input must a string key to a Python function.");
            }
            matlab::data::CharArray key = inputs[0];

            PyGILState_STATE gstate = PyGILState_Ensure();  // GIL{

            if (!Py_IsInitialized())
                throw std::runtime_error("Python not initialized.");

            // Imports the wrapper module and check its global dictionary for the function we want
            py::module pyHoraceFn;
            try {
                pyHoraceFn = py::module::import("pyHorace.FunctionWrapper");
            }
            catch (...) {
                PyGILState_Release(gstate);
                MATLABERROR("Cannot import Python pyHorace module.")
            }
            py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
            // PyBind11 does not have bindings for the C API PyDict_GetItem* methods
            PyObject *fnItem = PyDict_GetItemString(fnDict.ptr(), key.toAscii().c_str());
            if (fnItem == NULL) {
                PyGILState_Release(gstate);
                MATLABERROR("Unknown python function key.");
            }

            // The remainder of this code is an unholy mess of Python C API calls and undocumented internals of PyBind11
            // (not that PyBind is super well documented!) and should be considered _unsafe_
            // It should be refactored to use PyBind properly (perhaps after patching the PyBind headers with PyDict_GetItem*)

            if (PyCallable_Check(fnItem)) {
                PyObject *result;
                size_t endIdx = inputs.size() - 1;
                try {
                    try {
                        const matlab::data::StructArray in_struct(inputs[endIdx]);
                        const matlab::data::Array v = in_struct[0][matlab::data::MATLABFieldIdentifier("pyHorace_pyKwArgs")];
                        PyObject *kwargs = matlab_to_python(inputs[endIdx], fnItem);
                        PyDict_DelItemString(kwargs, "pyHorace_pyKwArgs");
                        py::tuple arr_in = convMat2np(inputs, fnItem, -2);
                        result = PyObject_Call(fnItem, arr_in.ptr(), kwargs);
                    } catch (...) {
                        py::tuple arr_in = convMat2np(inputs, fnItem);
                        result = PyObject_CallObject(fnItem, arr_in.ptr());
                    }
                } catch (char *e) {
                }
                if (result == NULL) {
                    PyErr_Print();
                    PyGILState_Release(gstate);
                    MATLABERROR("Python function threw an error.");
                }
                else {
                    auto npy_api = py::detail::npy_api::get();
                    bool is_arr = npy_api.PyArray_Check_(result);
                    if (is_arr) {
                        try {
                            outputs[0] = python_array_to_matlab((void*)result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else if(PyTuple_Check(result) || PyList_Check(result)) {
                        try {
                            outputs[0] = listtuple_to_cell(result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else if (PyUnicode_Check(result)) {
                        try {
                            outputs[0] = python_string_to_matlab(result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else if (PyDict_Check(result)) {
                        try {
                            outputs[0] = python_dict_to_matlab(result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else if (result != Py_None) {
                        Py_DECREF(result);
                        PyGILState_Release(gstate);
                        MATLABERROR("Unknown return type from Python function.");
                    }
                    Py_DECREF(result);
                }
            } else {
                PyGILState_Release(gstate);
                MATLABERROR("Python function is not callable.");
            }

            PyGILState_Release(gstate);  // GIL}
        }

};
