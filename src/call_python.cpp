#include "mex.hpp"
#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include <Python.h>
#include <iostream>
#include <sstream>
#include <cmath>
#include <stdexcept>

using namespace matlab::data;
using matlab::mex::ArgumentList;
namespace py = pybind11;

py::tuple convMat2np(ArgumentList inputs, py::handle owner) {
    // Note that this function must be called when we have the GIL
    size_t narg = inputs.size() - 1;

    py::tuple retval(narg);
    for (size_t idx = 1; idx <= narg; idx++) {
        std::vector<size_t> dims = inputs[idx].getDimensions();

        if (inputs[idx].getType() == matlab::data::ArrayType::DOUBLE) {
            std::vector<size_t> strides = {8};
            if (inputs[idx].getMemoryLayout() == matlab::data::MemoryLayout::COLUMN_MAJOR) {
                for (size_t ii=0; ii<(dims.size()-1); ii++) {
                    strides.push_back(dims[ii] * strides[ii]);
                }
            }
            else {
                strides.resize(dims.size(), 8);
                for (size_t ii=dims.size()-2; ii>=0; ii--) {
                    strides[ii] = dims[ii+1] * strides[ii+1];
                }
            }
            // Needs to be const to avoid copying to a new (mutable) array
            const matlab::data::TypedArray<double> arr = matlab::data::TypedArray<double>(inputs[idx]);
            // We need to pass a dummy python `base` object to own the reference otherwise PyBind will copy the data
            // See: https://github.com/pybind/pybind11/issues/323
            retval[idx - 1] = py::array_t<double>(dims, strides, (double*)(&(*arr.begin())), owner);
        }
        else if (inputs[idx].getType() == matlab::data::ArrayType::COMPLEX_DOUBLE) {
            std::vector<size_t> strides = {16};
            if (inputs[idx].getMemoryLayout() == matlab::data::MemoryLayout::COLUMN_MAJOR) {
                for (size_t ii=0; ii<(dims.size()-1); ii++) {
                    strides.push_back(dims[ii] * strides[ii]);
                }
            }
            else {
                strides.resize(dims.size(), 16);
                for (size_t ii=dims.size()-2; ii>=0; ii--) {
                    strides[ii] = dims[ii+1] * strides[ii+1];
                }
            }
            const matlab::data::TypedArray<std::complex<double>> arr = matlab::data::TypedArray<std::complex<double>>(inputs[idx]);
            retval[idx - 1] = py::array_t<std::complex<double>>(dims, strides, (std::complex<double>*)(&(*arr.begin())), owner);
        }
    	else {
            throw std::runtime_error("Unrecognised input type");
	    }
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
                    std::vector<matlab::data::Array>({ factory.createScalar("First input must a string key to index into a Python function.") }));
            }
            matlab::data::CharArray key = inputs[0];

            py::gil_scoped_acquire acquire;  // GIL{

            if (!Py_IsInitialized())
                throw std::runtime_error("Python not initialized.");

            // Imports the wrapper module and check its global dictionary for the function we want
            py::module pyHoraceFn;
            try {
                pyHoraceFn = py::module::import("pyHorace.FunctionWrapper");
            } 
            catch (...) {
                py::gil_scoped_release release;
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Cannot import Python pyHorace module.") }));
            }
            py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
            // PyBind11 does not have bindings for the C API PyDict_GetItem* methods
            PyObject *fnItem = PyDict_GetItemString(fnDict.ptr(), key.toAscii().c_str());
            if (fnItem == NULL) {
                py::gil_scoped_release release;
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Unknown python function key.") }));
            }

            if (PyCallable_Check(fnItem)) {
                py::tuple arr_in = convMat2np(inputs, fnItem);
                PyObject *result = PyObject_CallObject(fnItem, arr_in.ptr());
                if (result == NULL) {
                    PyErr_Print();
                    py::gil_scoped_release release;
                    matlabPtr->feval(u"error", 0,
                        std::vector<matlab::data::Array>({ factory.createScalar("Python function threw an error.") }));
                }
                else 
                    Py_DECREF(result);
            } else {
                py::gil_scoped_release release;
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Python function is not callable.") }));
            } 

            py::gil_scoped_release release;  // GIL}

        }

};
