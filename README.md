# pySpinW

## WARNING - Work in progress.

### Summary

**pySpinW** (*py-spin-double-u*) is a python implementation of the MATLAB library **SpinW**. It can optimize magnetic structures using mean field theory and calculate spin wave dispersion and spin-spin correlation function for complex crystal and magnetic structures. For details see http://www.spinw.org

### Status

This is currently under development and will progress in stages. 
1) ~~Conversion to a compiled python library.~~ *Currently in testing*
2) Conversion of graphics modules to native python using matplotlib/VTK.
3) Migration of auxiliary code to pure python.
4) Migration of main classes to pure python.
5) Convert the core spinwave code to C++

### Limitations

- Currently graphics are not showing up in the Docker script.
- The ipython interface is a bit clunky, until the ipython-magic is re-written
- Maybe memory duplication, so not ideal for large datasets.


## Install

There are 2 supported methods, Docker for a pre-built environment or a system install

### Using Docker

Use the Docker file and docker-compose as it creates a stable environment. 

```
docker-compose build
```

A jupyter notebook session is started with:
```
docker-compose up pySpinW
```
Where a session is accessible at http://127.0.0.1:8888 . At the moment `notebook.ipynb` is an example notebook.

You can also try scripting with: 
```
docker-compose up testScript
```
It will execute `docker_script.py`

#### Notes

- On Windows/OSX Xming or a similar window manager should be installed. Currently graphics are not working, so this is not a requirement. 

### Using system python3

### Requirements 
`numpy` and `jupyter` (if you want to run notebooks). 

### Usage

- Correct MATLAB library paths have to be set.
- To start a session `mlPath` for your MATLAB or MATLAB Runtime (v96) installation has to be given.

Then you can run `host_script.py` or make your own.

#### Notes

- Using a conda environment crashes the interface, so it's not recommended.

## Pull requests are welcome!  
