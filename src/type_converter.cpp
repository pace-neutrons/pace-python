#include "type_converter.hpp"

namespace libpymcr {

// -------------------------------------------------------------------------------------------------------
// Code for dynamic CPython class to wrap Matlab object without using PyBind
// -------------------------------------------------------------------------------------------------------
PyObject *matlab_wrapper_str(PyObject *self) {
    return PyUnicode_FromString("An opaque container for a Matlab object");
}

void matlab_wrapper_del(PyObject* pyself) {
    PyObject *error_type, *error_value, *error_traceback;
    PyErr_Fetch(&error_type, &error_value, &error_traceback); // Save the current exception, if any.
    matlab_wrapper* self = (matlab_wrapper*)pyself;
    self->arr_impl_sptr.reset();
    PyErr_Restore(error_type, error_value, error_traceback);  // Restore the saved exception.
}

// Functions to handle Matlab mxArrays
struct mxArray_header_2020a* _get_mxArray(Array arr) {
    matlab::data::impl::ArrayImpl* imp = reinterpret_cast<mArray*>(&arr)->get_ptr();
    struct impl_header_col_major* m0 = reinterpret_cast<struct impl_header_col_major*>(imp);
    struct impl_header_col_major* m1 = reinterpret_cast<struct impl_header_col_major*>(m0->data_ptr);
#if defined __APPLE__
    return reinterpret_cast<struct mxArray_header_2020a*>(m1->data_ptr);
#else
    return reinterpret_cast<struct mxArray_header_2020a*>(m1->mxArray);
#endif
}

// -------------------------------------------------------------------------------------------------------
// Code to translate Matlab types to Python types
// -------------------------------------------------------------------------------------------------------

PyObject* pymat_converter::is_wrapped_np_data(void *addr) {
    // Checks if addressed belongs to a wrapped numpy array
    for (auto it = m_py_cache.begin(); it != m_py_cache.end(); it++) {
        py::detail::PyArray_Proxy *arr = py::detail::array_proxy(it->second);
        if (addr == arr->data)
            return reinterpret_cast<PyObject*>(it->second);
    }
    return nullptr;
}

void* _get_data_pointer(matlab::data::Array arr) {
    if (arr.getMemoryLayout() == matlab::data::MemoryLayout::COLUMN_MAJOR) {
        struct mxArray_header_2020a* mx = _get_mxArray(arr);
        return mx->pr;
    } else {
        matlab::data::impl::ArrayImpl* imp = reinterpret_cast<mArray*>(&arr)->get_ptr();
        struct impl_header_row_major* m = static_cast<struct impl_header_row_major*>(static_cast<void*>(imp));
        return m->buffer;
    }
}

// Wraps a Matlab array in a numpy array without copying (should work with all numeric types)
template <typename T> PyObject* pymat_converter::matlab_to_python_t (matlab::data::Array arr, dt<T>) {
    // First checks if the array is not constructed from numpy data in the first place
    PyObject* wrapper = is_wrapped_np_data(_get_data_pointer(arr));
    if (wrapper != nullptr) {
        // If so, just return the original numpy array, but need to INCREF it as returning new reference
        if (!m_mex_flag) {
            // For case where an np array is created in a mex file, its REFCNT was INC in the cache
            Py_INCREF(wrapper);
        }
        return wrapper;
    }
    std::vector<size_t> strides = {sizeof(T)};
    std::vector<size_t> dims = arr.getDimensions();
    if (arr.getMemoryLayout() == matlab::data::MemoryLayout::COLUMN_MAJOR) {
        for (size_t ii=0; ii<(dims.size()-1); ii++) {
            strides.push_back(dims[ii] * strides[ii]);
        }
    }
    else {
        strides.resize(dims.size(), sizeof(T));
        for (size_t ii=dims.size()-2; ii>=0; ii--) {
            strides[ii] = dims[ii+1] * strides[ii+1];
        }
    }
    // Needs to be const to avoid copying to a new (mutable) array
    const matlab::data::TypedArray<T> arr_t = matlab::data::TypedArray<T>(arr);
    const T &tmp = *arr_t.begin();
    // The API recommends to set a PyCapsule with a custom deleter, which also ensures that PyBind
    // will not copy the data (see: https://github.com/pybind/pybind11/issues/323)
    // https://numpy.org/devdocs/reference/c-api/data_memory.html
    // Since we have our own matlab_wrapper Python object we use that instead of a PyCapsule
    // (which only has a normal pointer) so we can use the shared_ptr directly.
    matlab_wrapper* owner = (matlab_wrapper*) m_py_matlab_wrapper_t->tp_alloc(m_py_matlab_wrapper_t, 0);
    owner->arr_impl_sptr = reinterpret_cast<mArray*>(&arr)->get_pImpl();
    py::array_t<T> retval(dims, strides, (T*)(&tmp), reinterpret_cast<PyObject*>(owner));
    // PyBind auto increfs the base because PyArray_SetBaseObject steals the ref - but we want this
    Py_DECREF(owner);
    return retval.release().ptr();
}
// Specialisations for other types to generate the appropriate Python type
PyObject* pymat_converter::matlab_to_python_t(matlab::data::Array input, dt<char16_t>) {
    const matlab::data::TypedArray<char16_t> str(input);
    return PyUnicode_FromKindAndData(2, (void*)(&(*str.begin())), str.getNumberOfElements());
}
PyObject* pymat_converter::matlab_to_python_t(matlab::data::Array input, dt<std::basic_string<char16_t>>) {
    const matlab::data::TypedArray<matlab::data::MATLABString> str(input);
    if (input.getNumberOfElements() == 1) {
        const std::basic_string<char16_t> cstr(str[0]);
        return PyUnicode_FromKindAndData(2, (void*)cstr.c_str(), cstr.size());
    } else {
        PyObject* retval = PyList_New(0);
        for (auto mstr: str) {
            const std::basic_string<char16_t> cstr(mstr);
            if (PyList_Append(retval, PyUnicode_FromKindAndData(2, (void*)cstr.c_str(), cstr.size()))) {
                throw std::runtime_error("Error constructing python list from string array");
            }
        }
        return retval;
    }
}
PyObject* pymat_converter::matlab_to_python_t(matlab::data::Array input, dt<py::dict>) {
    const matlab::data::StructArray in_struct(input);
    if (input.getNumberOfElements() == 1) {
        PyObject* retval = PyDict_New();
        for (auto ky : in_struct.getFieldNames()) {
            PyObject* pyky = PyUnicode_FromString(std::string(ky).c_str());
            PyObject* pyval = to_python(in_struct[0][ky]);
            if (PyDict_SetItem(retval, pyky, pyval)) {
                throw std::runtime_error("Error constructing python dict from matlab struct");
            }
        }
        return retval;
    } else {
        PyObject* retval = PyList_New(0);
        for (auto struc : in_struct) {
            PyObject* elem = PyDict_New();
            for (auto ky : in_struct.getFieldNames()) {
                PyObject* pyky = PyUnicode_FromString(std::string(ky).c_str());
                PyObject* pyval = to_python(struc[ky]);
                if (PyDict_SetItem(elem, pyky, pyval)) {
                    throw std::runtime_error("Error constructing python dict from matlab struct");
                }
            }
            if (PyList_Append(retval, elem)) {
                throw std::runtime_error("Error constructing python list from struct array");
            }
        }
        return retval;
    }
}
PyObject* pymat_converter::matlab_to_python_t(matlab::data::Array input, dt<py::list>) {
    const matlab::data::CellArray in_cell(input);
    PyObject* retval = PyList_New(0);
    for (auto elem : in_cell) {
        PyObject *val = to_python(elem);
        int success = PyList_Append(retval, val);
        Py_DECREF(val); // Effectively steals the reference to val
        if (success == -1) {
            throw std::runtime_error("Error constructing python list from cell array");
        }
    }
    return retval;
}

PyObject* pymat_converter::matlab_to_python_t(matlab::data::Array input, dt<bool>) {
    const matlab::data::TypedArray<bool> in_arr(input);
    size_t n_elem = in_arr.getNumberOfElements();
    if (n_elem == 1) {
        return PyBool_FromLong(static_cast<long>(in_arr[0]));
    } else {
        PyObject* retval = PyList_New(n_elem);
        size_t idx = 0;
        for (auto elem: in_arr) {
            if(PyList_SetItem(retval, idx++, PyBool_FromLong(static_cast<long>(elem))) == -1) {
                throw std::runtime_error("Error constructing python bool list from array");
            }
        }
        return retval;
    }
}

PyObject* pymat_converter::wrap_matlab_object(matlab::data::Array input) {
    // Wrap a Matlab class in an opaque Python container which contains the underlying shared_ptr
    matlab_wrapper* container = (matlab_wrapper*) m_py_matlab_wrapper_t->tp_alloc(m_py_matlab_wrapper_t, 0);
    container->arr_impl_sptr = reinterpret_cast<mArray*>(&input)->get_pImpl();
    return (PyObject*) container;
}

PyObject* pymat_converter::to_python(matlab::data::Array input) {
    matlab::data::ArrayType type = input.getType();
    switch(type) {
        case matlab::data::ArrayType::DOUBLE:         return matlab_to_python_t(input, dt<double>());
        case matlab::data::ArrayType::SINGLE:         return matlab_to_python_t(input, dt<float>());
        case matlab::data::ArrayType::COMPLEX_SINGLE: return matlab_to_python_t(input, dt<std::complex<float>>());
        case matlab::data::ArrayType::COMPLEX_DOUBLE: return matlab_to_python_t(input, dt<std::complex<double>>());
        case matlab::data::ArrayType::LOGICAL:        return matlab_to_python_t(input, dt<bool>());
        case matlab::data::ArrayType::INT8:           return matlab_to_python_t(input, dt<int8_t>());
        case matlab::data::ArrayType::INT16:          return matlab_to_python_t(input, dt<int16_t>());
        case matlab::data::ArrayType::INT32:          return matlab_to_python_t(input, dt<int32_t>());
        case matlab::data::ArrayType::INT64:          return matlab_to_python_t(input, dt<int64_t>());
        case matlab::data::ArrayType::UINT8:          return matlab_to_python_t(input, dt<uint8_t>());
        case matlab::data::ArrayType::UINT16:         return matlab_to_python_t(input, dt<uint16_t>());
        case matlab::data::ArrayType::UINT32:         return matlab_to_python_t(input, dt<uint32_t>());
        case matlab::data::ArrayType::UINT64:         return matlab_to_python_t(input, dt<uint64_t>());
        case matlab::data::ArrayType::CHAR:           return matlab_to_python_t(input, dt<char16_t>());
        case matlab::data::ArrayType::MATLAB_STRING:  return matlab_to_python_t(input, dt<std::basic_string<char16_t>>());
        case matlab::data::ArrayType::STRUCT:         return matlab_to_python_t(input, dt<py::dict>());
        case matlab::data::ArrayType::CELL:           return matlab_to_python_t(input, dt<py::list>());
        case matlab::data::ArrayType::ENUM:
            throw std::runtime_error("Matlab enums not supported in Python");
        case matlab::data::ArrayType::SPARSE_LOGICAL:
        case matlab::data::ArrayType::SPARSE_DOUBLE:
        case matlab::data::ArrayType::SPARSE_COMPLEX_DOUBLE:
            throw std::runtime_error("Matlab sparse matrices not supported in Python");
        case matlab::data::ArrayType::VALUE_OBJECT:
        case matlab::data::ArrayType::HANDLE_OBJECT_REF:
            return wrap_matlab_object(input);
        default:
           throw std::runtime_error("Unrecognised input type");
    }
}

// -------------------------------------------------------------------------------------------------------
// Code to translate Python types to Matlab types
// -------------------------------------------------------------------------------------------------------

template <typename T> Array pymat_converter::raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims,
                                                           ssize_t *strides, int f_or_c_continuous,
                                                           matlab::data::ArrayFactory &factory, PyObject* obj) {
    if (f_or_c_continuous == 0) {
        // Slower copy methods - follow data strides for non-contiguous arrays
        buffer_ptr_t<T> buf = factory.createBuffer<T>(sz);
        T* ptr = buf.get();
        std::vector<size_t> stride;
        std::vector<size_t> k = {dims[0]};
        for (size_t i=1; i<dims.size(); i++)
            k.push_back(k[i-1] * dims[i]);      // Cumulative product of dimensions
        for (size_t i=0; i<dims.size(); i++) {
            if (strides[i] > -1)
                stride.push_back(static_cast<size_t>(strides[i]));
            else
                throw std::runtime_error("Invalid stride in numpy array");
        }
        for (size_t i=0; i<sz; i++) {
            size_t offset = 0, idx = i, vi;
            // This computes the N-Dim indices (i0,i1,i2,...) and multiplies it by the strides
            // The algorithm is taken from the ind2sub.m function in Matlab
            for (size_t d=dims.size(); d>0; d--) {
                vi = idx % k[d-1];
                offset += ((idx - vi) / k[d-1]) * stride[d];
                idx = vi;
            }
            offset += vi * stride[0];
            ptr[i] = *((T*)(raw + offset));
        }
        return factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::COLUMN_MAJOR);
    } else {
        // Fast method: wrap or block memory copy for contigous C- or Fortran-style arrays
        matlab::data::Array rv;
        T* begin = reinterpret_cast<T*>(raw);
        // Default to try to wrap existing data without copying. We can do this with createArrayFromBuffer
        // but (see: https://www.mathworks.com/matlabcentral/answers/514456) this causes an issue
        // when Matlab tries to delete the buffer. So we have to use a hack (see release_buffer() below)
        buffer_ptr_t<T> buf = buffer_ptr_t<T>(begin, [](void* ptr){});
        if (m_numpy_conv_flag == NumpyConversion::COPY || sz < 1000) {
            // But if user specify to copy or for small arrays, then use the prescribed API with createBuffer()
            buf = factory.createBuffer<T>(sz);
            memcpy(buf.get(), begin, sz * sizeof(T));
        }
        if (f_or_c_continuous == -1 || dims.size() == 1) {
            rv = factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::COLUMN_MAJOR);
        } else {
            rv = factory.createArrayFromBuffer(dims, std::move(buf), MemoryLayout::ROW_MAJOR);
        }
        if (m_numpy_conv_flag == NumpyConversion::WRAP && sz >= 1000) {
            // For wrapped arrays, we store a shared-data copy in a cache in this object to prevent Matlab
            // from deleting it before we are ready to release the buffer.
            if (m_mex_flag) {
                // This flag indicates the conversion was called from the call_python mex file.
                // In this case the Python obj will be DECREF when exiting the mex so we must INCREF here
                Py_INCREF(obj);
            }
            m_py_cache.push_back(std::make_pair(rv, obj));
        }
        return rv;
    }
}

bool pymat_converter::release_buffer(matlab::data::Array arr) {
    // Hack to safely release a buffer for a no-copy Matlab array converted from numpy
    if (m_numpy_conv_flag == NumpyConversion::COPY) {
        return true;
    }
    if (arr.getMemoryLayout() == matlab::data::MemoryLayout::ROW_MAJOR) {
        // It seems that ROW_MAJOR (C-style) arrays use a new C++ based type which supports custom deleter,
        // So we don't need to hack these types of arrays
        return true;
    }
    // For Column-major arrays, which are wrappers around a mxArray type, we have to use a hack
    // where we create a small buffer using createBuffer() and overwrite the mxArray->pr pointer
    // to point to this instead of the numpy array. Then when this array is deleted Matlab will
    // free the newly created buffer instead of the numpy array which causes a heap memory error
    matlab::data::ArrayFactory factory;
    struct mxArray_header_2020a* mx = _get_mxArray(arr);
    long rc = (mx->refcount == nullptr) ? 1 : *(mx->refcount);
    if (mx->refcount == nullptr || *(mx->refcount) == 1) {
        buffer_ptr_t<double> buf = factory.createBuffer<double>(1);
        // Hack - switch the memory for a Matlab created buffer
        mx->pr = reinterpret_cast<void*>(buf.release());
        return true;
    } else {
        return false;
    }
}

matlab::data::Array pymat_converter::python_array_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory) {
    // Cast the result to the PyArray C struct and its corresponding dtype struct
    py::detail::PyArray_Proxy *arr = py::detail::array_proxy(result);
    py::detail::PyArrayDescr_Proxy *dtype = py::detail::array_descriptor_proxy(arr->descr);
    if (arr->nd == 0) {            // 0-dimensional array - return a scalar
        if (dtype->kind == 'f') {
            if (dtype->elsize == sizeof(double)) return factory.createScalar(*((double*)(arr->data)));
            else if (dtype->elsize == sizeof(float)) return factory.createScalar(*((float*)(arr->data)));
        } else if (dtype->kind == 'c') {
            if (dtype->elsize == sizeof(std::complex<double>)) return factory.createScalar(*((std::complex<double>*)(arr->data)));
            else if (dtype->elsize == sizeof(std::complex<float>)) return factory.createScalar(*((std::complex<float>*)(arr->data)));
        }
    }
    if (dtype->elsize == 0) {
        throw std::runtime_error("Cannot convert heterogeneous numpy arrays to Matlab");
    }
    std::vector<size_t> dims;
    size_t numel = 1;
    for (size_t id = 0; id < arr->nd; id++) {
        dims.push_back(arr->dimensions[id]);
        numel = numel * dims[id];
    }
    // If we have 1D vector, force it to be a row vector to be consistent with Matlab
    if (dims.size() == 1) {
        dims.insert(dims.begin(), 1); }
    int fc_cont = 0;
    if (py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_F_CONTIGUOUS_))
        fc_cont = -1;
    else if (py::detail::check_flags(result, py::detail::npy_api::NPY_ARRAY_C_CONTIGUOUS_))
        fc_cont = 1;

    char *d = arr->data;
    ssize_t *strd = arr->strides;
    switch(dtype->type_num) {
        case py::detail::npy_api::NPY_DOUBLE_:    return raw_to_matlab<double>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_FLOAT_:     return raw_to_matlab<float>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_CDOUBLE_:   return raw_to_matlab<std::complex<double>>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_CFLOAT_:    return raw_to_matlab<std::complex<float>>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_BOOL_:      return raw_to_matlab<bool>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_INT8_:      return raw_to_matlab<int8_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_INT16_:     return raw_to_matlab<int16_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_INT32_:     return raw_to_matlab<int32_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_INT64_:     return raw_to_matlab<int64_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_UINT8_:     return raw_to_matlab<uint8_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_UINT16_:    return raw_to_matlab<uint16_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_UINT32_:    return raw_to_matlab<uint32_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_UINT64_:    return raw_to_matlab<uint64_t>(d, numel, dims, strd, fc_cont, factory, result);
        case py::detail::npy_api::NPY_LONGDOUBLE_:
        case py::detail::npy_api::NPY_CLONGDOUBLE_:
            throw std::runtime_error("Long double type not supported by Matlab. Cannot convert numpy array");
        case py::detail::npy_api::NPY_STRING_:
        case py::detail::npy_api::NPY_UNICODE_:
            throw std::runtime_error("Cannot convert numpy string array to Matlab");
        case py::detail::npy_api::NPY_OBJECT_:
            throw std::runtime_error("Cannot convert numpy object array to Matlab");
        default:
            throw std::runtime_error("Cannot convert unsupported numpy array dtype");
    }
}

template <typename T> T convert_py_obj (PyObject *obj) {
    throw std::runtime_error("Unrecognised Python type"); }
template <> int64_t convert_py_obj (PyObject *obj) {
    return PyLong_AsLong(obj); }
template <> double convert_py_obj (PyObject *obj) {
    return PyFloat_AsDouble(obj); }
template <> std::complex<double> convert_py_obj (PyObject *obj) {
    return std::complex<double>(PyComplex_RealAsDouble(obj), PyComplex_ImagAsDouble(obj)); }

template <typename T> Array pymat_converter::fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory) {
    std::vector<T> vec;
    vec.resize(objs.size());
    std::transform (objs.begin(), objs.end(), vec.begin(), convert_py_obj<T>);
    return factory.createArray<typename std::vector<T>::iterator, T>({1, vec.size()}, vec.begin(), vec.end());
}

CharArray pymat_converter::python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory) {
    Py_ssize_t str_sz;
    const char *str = PyUnicode_AsUTF8AndSize(result, &str_sz);
    if (!str) {
        PyErr_Print();
        throw std::runtime_error("Cannot create string from pyobject");
    }
    return factory.createCharArray(std::string(str, str_sz));
}

StructArray pymat_converter::python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory) {
    Py_ssize_t pos = 0;
    PyObject *key, *val;
    std::vector<std::string> keys;
    std::vector<PyObject*> vals;
    while (PyDict_Next(result, &pos, &key, &val)) {
        Py_ssize_t str_sz;
        const char *str = PyUnicode_AsUTF8AndSize(key, &str_sz);
        if (!str) {
            throw std::runtime_error("Can only convert python dict with string keys to Matlab struct");
        }
        keys.push_back(std::string(str, str_sz));
        vals.push_back(val);
    }
    StructArray retval = factory.createStructArray({1,1}, keys);
    for (size_t ii=0; ii<keys.size(); ii++) {
        retval[0][keys[ii]] = python_to_matlab_single(vals[ii], factory);
    }
    return retval;
}

int _list_array_data(PyObject *result, std::vector<double> &data, std::vector<size_t> &dims, bool is_first=false) {
    size_t obj_size = PyTuple_Check(result) ? (size_t)PyTuple_Size(result) : (size_t)PyList_Size(result);
    bool is_tuple = false;
    int dim, dim0;
    if (is_first) {
        dims.push_back(obj_size); }
    for(size_t ii=0; ii<obj_size; ii++) {
        PyObject *item = PyTuple_Check(result) ? PyTuple_GetItem(result, ii) : PyList_GetItem(result, ii);
        if (PyTuple_Check(item) || PyList_Check(item)) {
            if (!is_tuple) {
                // We only want to add dims for the very first iteration of each recursive call.
                // The first call (from listtuple_to_cell) will set is_first to true
                // Subsequent recursive calls will set this to true only on first iteration and
                // also when it in turn has been called by the first iteration of the outer loop.
                if ((dim0 = _list_array_data(item, data, dims, (ii==0) & is_first)) < 0) {
                    return -1; }
            } else {
                if ((dim = _list_array_data(item, data, dims)) < 0 || dim != dim0) {
                    return -1; }
            }
            is_tuple = true;
        } else {
            if (is_tuple) {
                return -1; } // If one item is a tuple, all must be tuple of same length
            if (PyLong_Check(item)) {
                data.push_back(PyLong_AsDouble(item));
            } else if (PyFloat_Check(item)) {
                data.push_back(PyFloat_AsDouble(item));
            } else {
                return -1;
            }
        }
    }
    return (int)obj_size;
}

std::vector<double> _to_colmajor(std::vector<double> inp, std::vector<size_t> dims) {
    std::vector<double> out(inp.size(), 0.);
    std::vector<size_t> strides = {1};
    size_t sz = dims.size();
    for (size_t i=1; i<sz; i++)
        strides.push_back(strides[i-1] * dims[i-1]);
    for (size_t i=0; i < inp.size(); i++) {
        size_t f_idx = 0, val = i;
        for (size_t d=sz; d>0; d--) {
            // Adapted from np code unravel_index_loop() and ravel_multi_index() in compiled_base.c
            size_t tmp = val / dims[d-1];  // Uses a local to enable single-divide optimisation
            size_t coord = val % dims[d-1];
            val = tmp;
            f_idx += coord * strides[d-1];
        }
        out[f_idx] = inp[i];
    }
    return out;
}

Array pymat_converter::listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory) {
    // Try to see if we have a nested list/tuple of numeric types: construct a Matlab N-D array
    std::vector<size_t> arr_dim;
    std::vector<double> arr_data;
    bool is_tuple = PyTuple_Check(result);
    if (!is_tuple && _list_array_data(result, arr_data, arr_dim, true) > 0) {
        // Only convert nested lists to Matlab arrays, leave tuples as cells
        if (arr_dim.size() > 1) {
            arr_data = _to_colmajor(arr_data, arr_dim);  // Convert to column-major (req by Matlab)
        } else {
            arr_dim.insert(arr_dim.begin(), 1); } // Force row vector for consistency ([1 2 3] is row vector in ml)
        return factory.createArray<typename std::vector<double>::iterator, double>(arr_dim, arr_data.begin(), arr_data.end());
    }
    size_t obj_size = is_tuple ? (size_t)PyTuple_Size(result) : (size_t)PyList_Size(result);
    CellArray cell_out = factory.createCellArray({1, obj_size});
    std::vector<PyObject*> objs;
    int typeflags = is_tuple ? MYOTHER : 0;  // Only create vector from lists not tuples
    for(size_t ii=0; ii<obj_size; ii++) {
        PyObject *item = is_tuple ? PyTuple_GetItem(result, ii) : PyList_GetItem(result, ii);
        cell_out[0][ii] = python_to_matlab_single(item, factory);
        if (PyLong_Check(item)) {
            // Force conversion to double because Matlab defaults to this and many routines will error with int64
            typeflags |= MYFLOAT;
            objs.push_back(PyFloat_FromDouble(PyLong_AsDouble(item)));
        } else if (PyFloat_Check(item)) {
            typeflags |= MYFLOAT;
            objs.push_back(item);
        } else if (PyComplex_Check(item)) {
            typeflags |= MYCOMPLEX;
            objs.push_back(item);
        } else {
            typeflags |= MYOTHER;
        }
    }
    if (typeflags == MYINTEGER) {
        return fill_vec_from_pyobj<int64_t>(objs, factory);
    } else if (typeflags == MYFLOAT) {
        return fill_vec_from_pyobj<double>(objs, factory);
    } else if (typeflags == MYCOMPLEX) {
        return fill_vec_from_pyobj<std::complex<double>>(objs, factory);
    } else {
        // We've got mixed or nonnumeric types - return a cell array of the elements
        return cell_out;
    }
}

matlab::data::Array pymat_converter::wrap_python_function(PyObject *input, matlab::data::ArrayFactory &factory) {
    // Wraps a Python function so it can be called using a mex function
    matlab::data::Array rv;
    std::string addrstr = std::to_string(reinterpret_cast<uintptr_t>(input));
    rv = factory.createStructArray({1, 1}, std::vector<std::string>({"libpymcr_func_ptr"}));
    py::module pyHoraceFn = py::module::import("libpymcr");
    py::dict fnDict = pyHoraceFn.attr("_globalFunctionDict");
    PyDict_SetItemString(fnDict.ptr(), addrstr.c_str(), input);
    rv[0][std::string("libpymcr_func_ptr")] = factory.createCharArray(addrstr.c_str());
    return rv;
}

matlab::data::Array pymat_converter::python_to_matlab_single(PyObject *input, matlab::data::ArrayFactory &factory) {
    matlab::data::Array output;
    auto npy_api = py::detail::npy_api::get();
    bool is_arr = npy_api.PyArray_Check_(input);
    if (is_arr) {
        output = python_array_to_matlab(input, factory);
    } else if (PyTuple_Check(input) || PyList_Check(input)) {
        output = listtuple_to_cell(input, factory);
    } else if (PyUnicode_Check(input)) {
        output = python_string_to_matlab(input, factory);
    } else if (PyDict_Check(input)) {
        output = python_dict_to_matlab(input, factory);
    } else if (PyBool_Check(input)) {  // Must be before long (True and False also evaluate to integers)
        output = factory.createScalar<double>(static_cast<double>(PyObject_IsTrue(input)));
    } else if (PyLong_Check(input)) {
        // Force conversion to double because Matlab defaults to this and many routines error with int64
        output = factory.createScalar<double>(PyLong_AsDouble(input));
    } else if (PyFloat_Check(input)) {
        output = factory.createScalar<double>(PyFloat_AsDouble(input));
    } else if (PyComplex_Check(input)) {
        output = factory.createScalar(std::complex<double>(PyComplex_RealAsDouble(input), PyComplex_ImagAsDouble(input)));
    } else if (input == Py_None) {
        output = factory.createArray<double>({0,0});
    } else if (PyCallable_Check(input)) {
        output = wrap_python_function(input, factory);
    } else if (PyObject_TypeCheck(input, m_py_matlab_wrapper_t)) {
        output = mArray(reinterpret_cast<matlab_wrapper*>(input)->arr_impl_sptr);
    } else {
        throw std::runtime_error("This Python type cannot be converted to Matlab");
    }
    return output;
}

void pymat_converter::clear_py_cache() {
    if (m_numpy_conv_flag == NumpyConversion::COPY) {
        return;
    }
    for (auto it = m_py_cache.begin(); it != m_py_cache.end();) {
        if (release_buffer(it->first)) {
            it = m_py_cache.erase(it);
        } else {
            it++;
        }
    }
}

matlab::data::Array pymat_converter::to_matlab(PyObject *input, bool mex_flag) {
    matlab::data::ArrayFactory factory;
    m_mex_flag = mex_flag;
    return python_to_matlab_single(input, factory);
}

pymat_converter::pymat_converter(NumpyConversion np_behaviour) : m_numpy_conv_flag(np_behaviour) {
    m_py_matlab_wrapper_t = (PyTypeObject*) PyType_FromSpec(&spec_matlab_wrapper);
}

pymat_converter::~pymat_converter() {
    clear_py_cache();
}

} // namespace libpymcr
