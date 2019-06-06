# pySpinW

## WARNING

 - This is a WIP in kinda works, except for graphics (blame MATLAB)
 - This doesn't seem to play well with conda environments. So you will need a python 3 on your system (also blame MATLAB for that one!).

## Install

### Via Docker

Use the Docker file and docker-compose at the moment as it creates a stable environment. It should be the case of 
```
docker-compose build
```
And then 
```
docker-compose up pySpinW
```
And going to http://127.0.0.1:8888
At the moment `testrun.ipynb` is an example notebook

### Using system python3

Requirements `numpy`. And then you can run `test.py` with the appropriate `mlPath` for your MATLAB or Matlab Runtime (v96) installation. 
