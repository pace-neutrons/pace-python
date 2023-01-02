#ifndef TYPECONVERTER_H
#define TYPECONVERTER_H

#include <MatlabDataArray/TypedArray.hpp>
#include <MatlabDataArray/ArrayFactory.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Python.h>
#include <iostream>
#include <algorithm>
#include <vector>
#include <stdexcept>
#include <cstring>
#include <map>

#define MATLABERROR(errmsg) matlabPtr->feval(u"error", 0, std::vector<matlab::data::Array>({ factory.createScalar(errmsg) }));
#define MYINTEGER 1
#define MYFLOAT 2
#define MYCOMPLEX 4
#define MYOTHER 8

using namespace matlab::data;
namespace py = pybind11;

namespace libpymcr {

    // Headers for hacking a mxArray
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
 
    /* Header for a (new-style) row-major array for reference (not used here)
    struct impl_header_row_major {
        void *unk_addr1;
        std::int64_t unk_i1;     // seems to be some kind of flags?
        std::int64_t *dims;      // Pointer to dimensions array
        void *unk_addr2;
        void *unk_addr3;
        std::int64_t n_elem;     // Number of elements in array
        void *unk_addr4;
        void *deleter;           // Pointer to deleter function
        std::int64_t junk[5];    // 40 bytes of junk (doesn't look like pointers)
        void *unk_addr5;
        void *buffer;            // Pointer to buffer (data)
        std::int64_t flags;      // More flags?
    }; */

    // Headers for a CPython class to wrap Matlab objects which we construct dynamically without Pybind11
    typedef struct {
        PyObject_HEAD
        matlab::data::Array* matlab_array_ptr;
        std::map<std::string, matlab::data::Array>* cache;
        char* name;
    } matlab_wrapper;

    PyObject *matlab_wrapper_new(PyTypeObject *subtype, PyObject *args, PyObject *kwds);
    PyObject *matlab_wrapper_str(PyObject *self);
    void matlab_wrapper_del(PyObject *self);

    static PyType_Slot matlab_wrapper_slots[] = {
        {Py_tp_new, (void*)matlab_wrapper_new},
        {Py_tp_str, (void*)matlab_wrapper_str},
        {Py_tp_finalize, (void*)matlab_wrapper_del},
        {0, 0}
    };

    static PyType_Spec spec_matlab_wrapper = {
        "libpymcr.matlab_wrapper",                // tp_name
        sizeof(matlab_wrapper),                   // tp_basicsize
        0,                                        // tp_itemsize
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_FINALIZE,
        matlab_wrapper_slots
    };

    // Now define the converter classes, first from Matlab to Python, then vice versa
    class pymat_converter {
    public:
        enum class NumpyConversion { COPY, WRAP };
    protected:
        PyObject* m_parent = PyCapsule_New(this, "MatlabConverter", nullptr);
        std::vector<char*> m_mat_cache_indices;
        std::map<std::string, matlab::data::Array> m_mat_cache;
        NumpyConversion m_numpy_conv_flag;
        std::vector< std::pair<matlab::data::Array, void*> > m_py_cache;
        PyTypeObject* m_py_matlab_wrapper_t;
        // Methods to convert from Matlab to Python
        char* get_next_cached_id();
        PyObject* is_wrapped_np_data(void* addr);
        template <typename T> PyObject* matlab_to_python_t (matlab::data::Array arr, py::handle owner);
        template <> PyObject* matlab_to_python_t<char16_t>(matlab::data::Array input, py::handle owner);
        template <> PyObject* matlab_to_python_t<std::basic_string<char16_t>>(matlab::data::Array input, py::handle owner);
        template <> PyObject* matlab_to_python_t<py::dict>(matlab::data::Array input, py::handle owner);
        template <> PyObject* matlab_to_python_t<py::list>(matlab::data::Array input, py::handle owner);
        PyObject* matlab_to_python(matlab::data::Array input, py::handle owner);
        PyObject* wrap_matlab_object(matlab::data::Array input);
        // Methods to convert from Python to Matlab
        template <typename T> Array raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims,
                                                  ssize_t *strides, matlab::data::ArrayFactory &factory);
        template <typename T> Array raw_to_matlab_contiguous(T* begin, size_t sz, std::vector<size_t> dims,
                                                             bool fstyle, matlab::data::ArrayFactory &factory, void* o);
        bool release_buffer(matlab::data::Array arr);
        matlab::data::Array python_array_to_matlab(void *result, matlab::data::ArrayFactory &factory);
        template <typename T> Array fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory);
        CharArray python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
        Array listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory);
        StructArray python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
        matlab::data::Array wrap_python_function(PyObject *input);
        matlab::data::Array python_to_matlab_single(PyObject *input, matlab::data::ArrayFactory &factory);
    public:
        void clear_py_cache();
        pymat_converter(NumpyConversion np_behaviour=NumpyConversion::COPY);
        ~pymat_converter();
        matlab::data::Array to_matlab(PyObject *input);
        PyObject* to_python(matlab::data::Array input);
    };

} // namespace libpymcr

#endif
