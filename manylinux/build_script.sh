#!/bin/bash

git clone https://github.com/pace-neutrons/pace-python
cd pace-python
/opt/python/cp36-cp36m/bin/pip wheel . --no-deps
