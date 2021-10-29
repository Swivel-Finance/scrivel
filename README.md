```
                             ____
                            / . .\
        SCRIpted swiVEL     \  ---<
                             \  /
                      _______/ /
                -=:___________/    (luk at de snaek)    
```

# scrivel
Scripting the Swivel Finance Protocol with Python

### psa
We suggest you create a virtual environment for this and every python project. 

#### assure you have python available
This is a python project, i'm just going to assume you have a python available. If not, do that first.
Scrivel expects at least a Python version of 3.7.3

#### assure you have pip available
`which pip`. Depending on your system it may be aliased with ...3 so, `which pip3`. If not present install it.

#### with virtualenv
Once you have pip available use `pip install --upgrade virtualenv` (sudo it if you must...).

Now you are free to place the virtual environment for this project anywhere you want. This author uses a `~/python/` top level directory
to house all virtualenvs (which this author makes for each python project).

    virtualenv -p python3 ~/python/scrivel

With the env made, source it.

    source ~/python/scrivel/bin/activate

Now you can move to installing things...

## installation
Clone the repo, activate your virtual env then

    pip install -r requirements.txt

### before you run the examples
Each of the files in `/scrivel/examples` needs its `shebang` modified to point to the python executable you created with virtualenv.
For example if you followed the path above
    
    #!/home/<your_user_name>/python/scrivel/bin/python

If not, just make it match wherever you put it.

Also, you'll need to modify some constants located in `/scrivel/constants/__init__.py`, specifically:

* HTTP_PROVIDER
* WS_PROVIDER
* PUB_KEY

## run the examples
The example files can then be run by (assuming you are in the repo root dir)

    python scrivel/examples/<foo>_example.py

# todo
The rest of this readme...
