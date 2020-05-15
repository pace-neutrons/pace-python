#!/bin/bash

gcc -shared -o fe_sqw_c.so -fPIC fe_sqw.c
g++ -shared -o fe_sqw_cpp.so -fPIC fe_sqw.cpp
gfortran -shared -o fe_sqw_f.so -fPIC fe_sqw.f90
