#ifndef LIBPYMCR_H
#define LIBPYMCR_H

#include <MatlabCppSharedLib.hpp>
#include <sstream>
#include <fstream>
#include "type_converter.hpp"

typedef std::basic_streambuf<char16_t> StreamBuffer;
typedef std::basic_stringbuf<char16_t> StringBuffer;

namespace libpymcr {


    class matlab_env {
    protected:
        // Properties
        std::shared_ptr<matlab::cpplib::MATLABApplication> _app;
        std::unique_ptr<matlab::cpplib::MATLABLibrary> _lib;
        std::shared_ptr<StringBuffer> _m_output = std::make_shared<StringBuffer>();
        std::shared_ptr<StringBuffer> _m_error = std::make_shared<StringBuffer>();
        std::shared_ptr<StreamBuffer> _m_output_buf = std::static_pointer_cast<StreamBuffer>(_m_output);
        std::shared_ptr<StreamBuffer> _m_error_buf = std::static_pointer_cast<StreamBuffer>(_m_error);
        pymat_converter _converter;
        size_t _parse_inputs(std::vector<matlab::data::Array>& m_args, py::args py_args, py::kwargs& py_kwargs);
    public:
        py::tuple feval(const std::u16string &funcname, py::args args, py::kwargs& kwargs);
        py::tuple call(py::args args, py::kwargs& kwargs);
        matlab_env(const std::u16string ctfname, std::string matlabroot);
    };


}  // namespace libpymcr

#endif // LIBPYMCR_H
