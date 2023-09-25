#include "matlab_mex.hpp"
#include "type_converter.hpp"

using namespace matlab::data;
using matlab::mex::ArgumentList;
namespace py = pybind11;

// -------------------------------------------------------------------------------------------------------
// Mex class to run Python function referenced in a global dictionary
// -------------------------------------------------------------------------------------------------------

class MexFunction : public matlab::mex::Function {

    protected:
        libpymcr::pymat_converter *_converter = nullptr;
        py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd) {
            // Note that this function must be called when we have the GIL
            size_t narg = inputs.size() + lastInd;
            py::tuple retval(narg);
            for (size_t idx = 1; idx <= narg; idx++) {
                retval[idx - 1] = _converter->to_python(inputs[idx]);
            }
            return retval;
        }

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            matlab::data::ArrayFactory factory;
            if (inputs.size() < 1 || inputs[0].getType() != matlab::data::ArrayType::CHAR) {
                throw std::runtime_error("Input must be reference to a Python function.");
            }
            matlab::data::CharArray key = inputs[0];

            PyGILState_STATE gstate = PyGILState_Ensure();  // GIL{

            if (_converter == nullptr) {
                _converter = new libpymcr::pymat_converter(libpymcr::pymat_converter::NumpyConversion::WRAP);
            }

            py::module pyHoraceFn = py::module::import("libpymcr");
            py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
            PyObject *fn_ptr = PyDict_GetItemString(fnDict.ptr(), key.toAscii().c_str());

            if (PyCallable_Check(fn_ptr)) {
                PyObject *result;
                size_t endIdx = inputs.size() - 1;
                try {
                    try {
                        const matlab::data::StructArray in_struct(inputs[endIdx]);
                        const matlab::data::Array v = in_struct[0][matlab::data::MATLABFieldIdentifier("pyHorace_pyKwArgs")];
                        PyObject *kwargs = _converter->to_python(inputs[endIdx]);
                        PyDict_DelItemString(kwargs, "pyHorace_pyKwArgs");
                        py::tuple arr_in = convMat2np(inputs, fn_ptr, -2);
                        result = PyObject_Call(fn_ptr, arr_in.ptr(), kwargs);
                    } catch (...) {
                        py::tuple arr_in = convMat2np(inputs, fn_ptr, -1);
                        result = PyObject_CallObject(fn_ptr, arr_in.ptr());
                    }
                } catch (...) {
                }
                if (result == NULL) {
                    PyErr_Print();
                    PyGILState_Release(gstate);
                    throw std::runtime_error("Python function threw an error.");
                }
                else {
                    try {
                        outputs[0] = _converter->to_matlab(result, Py_REFCNT(result)==1);
                    } catch (char *e) {
                        Py_DECREF(result);
                        PyGILState_Release(gstate);
                        throw std::runtime_error(e);
                    }
                    Py_DECREF(result);
                }
            } else {
                PyGILState_Release(gstate);
                throw std::runtime_error("Python function is not callable.");
            }

            PyGILState_Release(gstate);  // GIL}
        }

};
