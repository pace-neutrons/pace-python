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

            PyGILState_STATE gstate = PyGILState_Ensure(); // GIL{

            if (!Py_IsInitialized())
                throw std::runtime_error("Python not initialized.");

            // Imports the wrapper module and check its global dictionary for the function we want
            py::module pyHoraceFn;
            try {
                pyHoraceFn = py::module::import("pace_neutrons.FunctionWrapper");
            } 
            catch (...) {
                PyGILState_Release(gstate);
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Cannot import Python pace_neutrons module.") }));
            }
            py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
            
            try {
                if (PyDict_DelItemString(fnDict.ptr(), key.toAscii().c_str()) != 0)
                    throw std::runtime_error("Cannot delete key from functions dict.");
            }
            catch (...) {
                PyGILState_Release(gstate);
                matlabPtr->feval(u"error", 0,
                    std::vector<matlab::data::Array>({ factory.createScalar("Cannot delete key from functions dict.") }));
            }

            PyGILState_Release(gstate);  // GIL}

        }

};
