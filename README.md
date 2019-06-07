# pySpinW

## WARNING

 - This is a WIP in kinda works.
 - This doesn't seem to play well with conda environments. So you will need to use your systems python 3 (blame MATLAB for that one).

## Install

### Via Docker

Use the Docker file and docker-compose at the moment as it creates a stable environment. It should be the case of 
```
docker-compose build
docker-compose up pySpinW
```
Then go to http://127.0.0.1:8888 . At the moment `notebook.ipynb` is an example notebook.

You can also try `docker-compose up testScript` if you wish to try scripting in Docker. It will execute `docker_script.py`

### Using system python3

Requirements `numpy` and `jupyter` (if you want to run notebooks). Then you can run `host_script.py` with the appropriate `mlPath` for your MATLAB or Matlab Runtime (v96) installation. 
