//#include "mex.h"
#include "pybind11/pybind11.h"
#include <iostream>

namespace py = pybind11;

void call_matlab(std::string command) {
    //mexEvalString(command.c_str());
    //mexCallMATLAB(0, NULL, 0, NULL, command.c_str());
    std::cout << command << std::endl;
}

PYBIND11_MODULE(call_matlab, m) {
    m.def("call_matlab", &call_matlab, "A function to call matlab with an arbitrary string",
          py::arg("command"));
}
