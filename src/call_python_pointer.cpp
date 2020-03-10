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
            const double addr_in = inputs[0][0];
            void *address = (void*)((int64_t)(std::round(addr_in)));
            std::cout << "Input address = " << addr_in << "\n";
            std::cout << "Hex address = " << std::hex << address << "\n";
            if (!Py_IsInitialized())
                throw std::runtime_error("Python not initialized.");
            // Note we are **assuming** that this is a valid memory address. 
            // If not, we'll get a segmentation fault / access violation and there is no way to catch this.
            PyObject *pyfun = (PyObject*)address;
            PyGILState_STATE gstate = PyGILState_Ensure();
            if (Py_REFCNT(pyfun) < 1) {
                PyGILState_Release(gstate);
                throw std::runtime_error("Python object memory location is not valid.");
            } else if (PyCallable_Check(pyfun)) {
                PyObject *result = PyObject_CallObject(pyfun, nullptr);
                if (result == NULL) {
                    PyErr_Print();
                    PyGILState_Release(gstate);
                    throw std::runtime_error("Python function threw an error.");
                }
                else 
                    Py_DECREF(result);
            } else {
                PyGILState_Release(gstate);
                throw std::invalid_argument("Python function is not callable.");
            }
            PyGILState_Release(gstate);
/*          // This does not work because PyBind11 only allows cast of void* to PyCapsule
            py::gil_scoped_acquire acquire;
            py::object pyfun = py::cast(address);
            py::object pybuiltins = py::module::import("builtins");
            py::object pytype = pybuiltins.attr("type");
            std::cout << "PyObject type is ";
            py::print(py::str(pytype(pyfun)));
            std::cout << "\n";
            pyfun();
            py::gil_scoped_release release;
*/
        }

};
