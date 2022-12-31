#ifndef LIBCTF_H
#define LIBCTF_H

#include <MatlabCppSharedLib.hpp>
#include <map>
#include <sstream>
#include <fstream>
#include "type_converter.hpp"

typedef std::basic_streambuf<char16_t> StreamBuffer;
typedef std::basic_stringbuf<char16_t> StringBuffer;

namespace libpymcr {

    struct mxArray_header_2020a { // 96 bytes long
        std::int64_t *refcount;  // Pointer to the number of shared copies
        void *unknown1;          // Seems to be zero
        std::int64_t ClassID;    // https://mathworks.com/help/matlab/apiref/mxclassid.html
        std::int64_t flags;      // ???
        union {
            std::int64_t M;      // Row size for 2D matrices, or
            std::int64_t *dims;  // Pointer to dims array for nD > 2 arrays
        } Mdims;
        union {
            std::int64_t N;      // Column size for 2D matrices, or
            std::int64_t ndims;  // Number of dimemsions for nD > 2 arrays
        } Nndim;
        void *unknown_addr1;     // Something related to structs and cells
        void *pr;                // Pointer to the data
        void *unknown_addr2;     // Something related to structs or sparse
        void *unknown_addr3;     // Something related to sparse
        void *unknown2;          // Seems to be zero
        void *unknown3;          // Seems to be zero
    };

    struct impl_header_col_major {
        void *ad1;               // Class address?
        std::int64_t *unity;     // Seems to be always 1
        void *data_ptr;          // Pointer to another struct that points to a mxArray
        std::int64_t *flags;     // Some kind of flags?
        std::int64_t *dims;      // Pointer to dimensions array
        void *unknown1;
        void *unknown2;
        void *unknown3;
        void *unknown4;
        void *mxArray;           // Pointer to mxArray in the *data_ptr struct
    };

    class matlab_env {
    protected:
        // Properties
        std::shared_ptr<matlab::cpplib::MATLABApplication> _app;
        std::unique_ptr<matlab::cpplib::MATLABLibrary> _lib;
        std::shared_ptr<StringBuffer> _m_output = std::make_shared<StringBuffer>();
        std::shared_ptr<StringBuffer> _m_error = std::make_shared<StringBuffer>();
        std::shared_ptr<StreamBuffer> _m_output_buf = std::static_pointer_cast<StreamBuffer>(_m_output);
        std::shared_ptr<StreamBuffer> _m_error_buf = std::static_pointer_cast<StreamBuffer>(_m_error);
        PyObject* _parent = PyCapsule_New(this, "MatlabEnvironment", nullptr);
        std::vector<char*> _cache_indices;
        std::map<std::string, matlab::data::Array> _cached_arrays;
        std::vector<matlab::data::Array> _input_cache;
        // Methods
        template <typename T> TypedArray<T> _to_matlab_nocopy(T* begin, std::vector<size_t> dims,
                                                              bool f_contigous, matlab::data::ArrayFactory &factory);
        void _release_buffer(matlab::data::Array arr);
        matlab::data::Array _numpy_array_to_matlab(void *result, matlab::data::ArrayFactory &factory);
        matlab::data::Array _wrap_python_function(PyObject *input);
        matlab::data::Array _convert_to_matlab(PyObject *input);
        size_t _parse_inputs(std::vector<matlab::data::Array>& m_args, py::args py_args, py::kwargs& py_kwargs);
        char* _get_next_cached_id();
        PyObject* _matlab_to_python(matlab::data::Array input);
    public:
        py::tuple feval(const std::u16string &funcname, py::args args, py::kwargs& kwargs);
        py::tuple call(py::args args, py::kwargs& kwargs);
        matlab_env(const std::u16string ctfname, std::string matlabroot);
        ~matlab_env();
    };

    class matlab_wrapper_cpp {
    protected:
        matlab::data::Array _m;
        friend class pacecpp;

    public:
        matlab_wrapper_cpp(matlab::data::Array input) : _m(input) {}
    };


}  // namespace libpymcr

#endif // LIBCTF_H
