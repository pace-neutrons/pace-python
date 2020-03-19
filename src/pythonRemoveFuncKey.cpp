#include "mex.hpp"
#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"
#include <Python.h>
#include <iostream>
#include <sstream>
#include <cmath>
#include <stdexcept>

using namespace matlab::data;
using matlab::mex::ArgumentList;
namespace py = pybind11;

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
            
            try {
                if (PyDict_DelItemString(fnDict.ptr(), key.toAscii().c_str()) != 0)
                    throw std::runtime_error("Cannot delete key from functions dict.");
            }
            catch (...) {
                py::gil_scoped_release release;
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Cannot delete key from functions dict.") }));
            }

            py::gil_scoped_release release;  // GIL}

        }

};
