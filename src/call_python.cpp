#include "mex.hpp"
#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include <Python.h>
#include <iostream>
#include <algorithm>
#include <vector>
#include <stdexcept>

#define MATLABERROR(errmsg) matlabPtr->feval(u"error", 0, std::vector<matlab::data::Array>({ factory.createScalar(errmsg) }));
#define MYINTEGER 1
#define MYFLOAT 2
#define MYCOMPLEX 4
#define MYOTHER 8

using namespace matlab::data;
using matlab::mex::ArgumentList;
namespace py = pybind11;

template <typename T> py::array_t<T>
wrap_matlab(matlab::data::Array arr, py::handle owner) {
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
    return py::array_t<T>(dims, strides, (T*)(&(*arr_t.begin())), owner);
}


py::tuple convMat2np(ArgumentList inputs, py::handle owner) {
    // Note that this function must be called when we have the GIL
    size_t narg = inputs.size() - 1;

    py::tuple retval(narg);
    for (size_t idx = 1; idx <= narg; idx++) {
        if (inputs[idx].getType() == matlab::data::ArrayType::DOUBLE)
            retval[idx - 1] = wrap_matlab<double>(inputs[idx], owner);
        else if (inputs[idx].getType() == matlab::data::ArrayType::SINGLE)
            retval[idx - 1] = wrap_matlab<float>(inputs[idx], owner);
        else if (inputs[idx].getType() == matlab::data::ArrayType::COMPLEX_SINGLE)
            retval[idx - 1] = wrap_matlab<std::complex<float>>(inputs[idx], owner);
        else if (inputs[idx].getType() == matlab::data::ArrayType::COMPLEX_DOUBLE)
            retval[idx - 1] = wrap_matlab<std::complex<double>>(inputs[idx], owner);
        else
            throw std::runtime_error("Unrecognised input type");
    }

    return retval;
}

CellArray cast_py_to_matlab_array(void *result, matlab::data::ArrayFactory &factory) {
    // Cast the result to the PyArray C struct and its corresponding dtype struct
    py::detail::PyArray_Proxy *arr = py::detail::array_proxy(result);
    py::detail::PyArrayDescr_Proxy *dtype = py::detail::array_descriptor_proxy(arr->descr);
    std::vector<size_t> dims;
    size_t numel = 1;
    for (size_t id = 0; id < arr->nd; id++) {
        dims.push_back(arr->dimensions[id]);
        numel = numel * dims[id];
    }
    char *begin = arr->data;
    char *end = begin + (numel * dtype->elsize);  // dangerous pointer arithmetic?
    if (dtype->kind == 'f') {       // Floating point array
        if (dtype->elsize == sizeof(double))
            return factory.createCellArray({1, 1}, factory.createArray<double>(dims, (double*)begin, (double*)end));
        else if(dtype->elsize == sizeof(float))
            return factory.createCellArray({1, 1}, factory.createArray<float>(dims, (float*)begin, (float*)end));
    }
    else if (dtype->kind == 'c') {  // Complex array
        if (dtype->elsize == sizeof(std::complex<double>))
            return factory.createCellArray({1, 1}, factory.createArray<std::complex<double>>(dims, (std::complex<double>*)begin, (std::complex<double>*)end));
        else if(dtype->elsize == sizeof(std::complex<float>))
            return factory.createCellArray({1, 1}, factory.createArray<std::complex<float>>(dims, (std::complex<float>*)begin, (std::complex<float>*)end));
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

CellArray cast_listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory) {
    size_t obj_size = PyTuple_Check(result) ? (size_t)PyTuple_Size(result) : (size_t)PyList_Size(result);
    CellArray cell_out = factory.createCellArray({1, obj_size});
    auto npy_api = py::detail::npy_api::get();
    std::vector<PyObject*> objs;
    int typeflags = 0;
    for(size_t ii=0; ii<obj_size; ii++) {
        PyObject *item = PyTuple_Check(result) ? PyTuple_GetItem(result, ii) : PyList_GetItem(result, ii);
        bool is_arr = npy_api.PyArray_Check_(item);
        if (is_arr) {
            cell_out[0][ii] = cast_py_to_matlab_array((void*)item, factory);
            typeflags |= MYOTHER;
        } else if (PyTuple_Check(item) || PyList_Check(item)) {
            cell_out[0][ii] = cast_listtuple_to_cell(item, factory);
            typeflags |= MYOTHER;
        } else if (PyLong_Check(item)) {
            typeflags |= MYINTEGER;
            objs.push_back(item);
        } else if (PyFloat_Check(item)) {
            typeflags |= MYFLOAT;
            objs.push_back(item);
        } else if (PyComplex_Check(item)) {
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
        return cell_out;
    }
}

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
                try {
                    py::tuple arr_in = convMat2np(inputs, fnItem);
                    result = PyObject_CallObject(fnItem, arr_in.ptr());
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
                            outputs[0] = cast_py_to_matlab_array((void*)result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else if(PyTuple_Check(result) || PyList_Check(result)) {
                        try {
                            outputs[0] = cast_listtuple_to_cell(result, factory);
                        } catch (char *e) {
                            Py_DECREF(result);
                            PyGILState_Release(gstate);
                            MATLABERROR(e);
                        }
                    }
                    else {
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
