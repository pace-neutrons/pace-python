#include "mex.hpp"
#include "mexAdapter.hpp"
#include "type_converter.hpp"

using namespace matlab::data;
using matlab::mex::ArgumentList;
namespace py = pybind11;

#define MATLABERROR(errmsg) matlabPtr->feval(u"error", 0, std::vector<matlab::data::Array>({ factory.createScalar(errmsg) }));

// -------------------------------------------------------------------------------------------------------
// Mex class to run Python function referenced in a global dictionary
// -------------------------------------------------------------------------------------------------------

class MexFunction : public matlab::mex::Function {

    protected:
        py::tuple convMat2np(ArgumentList inputs, py::handle owner, size_t lastInd, libpymcr::pymat_converter* converter) {
            // Note that this function must be called when we have the GIL
            size_t narg = inputs.size() + lastInd;
            py::tuple retval(narg);
            for (size_t idx = 1; idx <= narg; idx++) {
                retval[idx - 1] = converter->to_python(inputs[idx]);
            }
            return retval;
        }

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            std::shared_ptr<matlab::engine::MATLABEngine> matlabPtr = getEngine();
            matlab::data::ArrayFactory factory;
            if (inputs.size() < 1 || inputs[0].getNumberOfElements() != 2 ||
                inputs[0].getType() != matlab::data::ArrayType::UINT64) { // Matlab only supports 64-bit
                    MATLABERROR("First input must be pointers to a Python function and converter.");
            }
            uintptr_t key = inputs[0][0];
            uintptr_t conv_addr = inputs[0][1];

            PyGILState_STATE gstate = PyGILState_Ensure();  // GIL{

            libpymcr::pymat_converter* converter = reinterpret_cast<libpymcr::pymat_converter*>(conv_addr);
            PyObject* fn_ptr = reinterpret_cast<PyObject*>(key);

            if (PyCallable_Check(fn_ptr)) {
                PyObject *result;
                size_t endIdx = inputs.size() - 1;
                try {
                    try {
                        const matlab::data::StructArray in_struct(inputs[endIdx]);
                        const matlab::data::Array v = in_struct[0][matlab::data::MATLABFieldIdentifier("pyHorace_pyKwArgs")];
                        PyObject *kwargs = converter->to_python(inputs[endIdx]);
                        PyDict_DelItemString(kwargs, "pyHorace_pyKwArgs");
                        py::tuple arr_in = convMat2np(inputs, fn_ptr, -2, converter);
                        result = PyObject_Call(fn_ptr, arr_in.ptr(), kwargs);
                    } catch (...) {
                        py::tuple arr_in = convMat2np(inputs, fn_ptr, -1, converter);
                        result = PyObject_CallObject(fn_ptr, arr_in.ptr());
                    }
                } catch (char *e) {
                }
                if (result == NULL) {
                    PyErr_Print();
                    PyGILState_Release(gstate);
                    MATLABERROR("Python function threw an error.");
                }
                else {
                    try {
                        outputs[0] = converter->to_matlab(result, Py_REFCNT(result)==1);
                    } catch (char *e) {
                        Py_DECREF(result);
                        PyGILState_Release(gstate);
                        MATLABERROR(e);
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
