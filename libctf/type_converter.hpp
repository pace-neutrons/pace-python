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

#define MATLABERROR(errmsg) matlabPtr->feval(u"error", 0, std::vector<matlab::data::Array>({ factory.createScalar(errmsg) }));
#define MYINTEGER 1
#define MYFLOAT 2
#define MYCOMPLEX 4
#define MYOTHER 8

using namespace matlab::data;
namespace py = pybind11;

// Functions to convert from Matlab to Python
template <typename T> PyObject* matlab_to_python_t (const matlab::data::Array arr, py::handle owner);
template <> PyObject* matlab_to_python_t<char16_t>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<std::basic_string<char16_t>>(const matlab::data::Array input, py::handle owner);
PyObject* matlab_to_python(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::dict>(const matlab::data::Array input, py::handle owner);
template <> PyObject* matlab_to_python_t<py::list>(const matlab::data::Array input, py::handle owner);

// Functions to convert from Python to Matlab
template <typename T> TypedArray<T> raw_to_matlab(char *raw, size_t sz, std::vector<size_t> dims, ssize_t *strides, matlab::data::ArrayFactory &factory);
template <typename T> TypedArray<T> raw_to_matlab_contiguous(T* begin, size_t sz, std::vector<size_t> dims, bool f_contigous, matlab::data::ArrayFactory &factory);
matlab::data::Array python_array_to_matlab(void *result, matlab::data::ArrayFactory &factory);
template <typename T> T convert_py_obj (PyObject *obj);
template <> int64_t convert_py_obj (PyObject *obj);
template <> double convert_py_obj (PyObject *obj);
template <> std::complex<double> convert_py_obj (PyObject *obj);
template <typename T> TypedArray<T> fill_vec_from_pyobj(std::vector<PyObject*> &objs, matlab::data::ArrayFactory &factory);
CharArray python_string_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);
Array listtuple_to_cell(PyObject *result, matlab::data::ArrayFactory &factory);
StructArray python_dict_to_matlab(PyObject *result, matlab::data::ArrayFactory &factory);

#endif
