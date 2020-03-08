#include "mex.hpp"
#include "mexAdapter.hpp"
#include "pybind11/pybind11.h"

namespace py = pybind11;

using matlab::mex::ArgumentList;
class MexFunction : public matlab::mex::Function {

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
        }
};

void call_matlab(uint64_t engine_addr, std::string command) {
    std::shared_ptr<matlab::engine::MATLABEngine> matlab_ptr = std::make_shared<matlab::engine::MATLABEngine>((void*)engine_addr);
    matlab_ptr->eval(matlab::engine::convertUTF8StringToUTF16String(command));
}

PYBIND11_MODULE(call_matlab, m) {
    m.def("call_matlab", &call_matlab, "A function to call matlab with an arbitrary string",
          py::arg("engine"), py::arg("command"));
}
