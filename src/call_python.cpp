#include "mex.hpp"
#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include <Python.h>
#include <iostream>
#include <stdexcept>

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


class MexFunction : public matlab::mex::Function {

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            std::shared_ptr<matlab::engine::MATLABEngine> matlabPtr = getEngine();
            matlab::data::ArrayFactory factory;
            if (inputs.size() < 1 ||
                inputs[0].getType() != matlab::data::ArrayType::CHAR) {
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("First input must a string key to a Python function.") }));
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
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Cannot import Python pyHorace module.") }));
            }
            py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
            // PyBind11 does not have bindings for the C API PyDict_GetItem* methods
            PyObject *fnItem = PyDict_GetItemString(fnDict.ptr(), key.toAscii().c_str());
            if (fnItem == NULL) {
                PyGILState_Release(gstate);
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Unknown python function key.") }));
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
                    matlabPtr->feval(u"error", 0, 
                        std::vector<matlab::data::Array>({ factory.createScalar(e) })); 
                }
                if (result == NULL) { 
                    PyErr_Print(); 
                    PyGILState_Release(gstate);
                    matlabPtr->feval(u"error", 0, 
                        std::vector<matlab::data::Array>({ factory.createScalar("Python function threw an error.") })); 
                } 
                else {
                    auto npy_api = py::detail::npy_api::get();
                    bool is_arr = npy_api.PyArray_Check_(result);
                    if (!is_arr) {
                        Py_DECREF(result);
                        PyGILState_Release(gstate);
                        matlabPtr->feval(u"error", 0, 
                            std::vector<matlab::data::Array>({ factory.createScalar("Python function did not return an array.") })); 
                    }
                    // Cast the result to the PyArray C struct and its corresponding dtype struct
                    py::detail::PyArray_Proxy *arr = py::detail::array_proxy((void*)result);
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
                            outputs[0] = factory.createArray<double>(dims, (double*)begin, (double*)end);
                        else if(dtype->elsize == sizeof(float))
                            outputs[0] = factory.createArray<float>(dims, (float*)begin, (float*)end);
                    }
                    else if (dtype->kind == 'c') {  // Complex array
                        if (dtype->elsize == sizeof(std::complex<double>))
                            outputs[0] = factory.createArray<std::complex<double>>(dims, (std::complex<double>*)begin, (std::complex<double>*)end);
                        else if(dtype->elsize == sizeof(std::complex<float>))
                            outputs[0] = factory.createArray<std::complex<float>>(dims, (std::complex<float>*)begin, (std::complex<float>*)end);
                    }
                    else {
                        Py_DECREF(result);
                        PyGILState_Release(gstate);
                        matlabPtr->feval(u"error", 0, 
                            std::vector<matlab::data::Array>({ factory.createScalar("Python function returned a non-floating point array.") })); 
                    }
                    Py_DECREF(result); 
                }
            } else { 
                PyGILState_Release(gstate);
                matlabPtr->feval(u"error", 0,
                                 std::vector<matlab::data::Array>({ factory.createScalar("Python function is not callable.") }));
            }

            PyGILState_Release(gstate);  // GIL}
        }

};
