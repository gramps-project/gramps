The files in this directory are used to build the Gramps Windows AIO (All In One) installer.

# Build AIO for the master branch

1. Install MSYS2
    1. Download MSYS2 from <https://www.msys2.org/>.
    2. Install with the default options.
    3. From the Start menu, run "MSYS2 UCRT64".
    4. Upgrade system
     
        ```bash
        pacman -Syuu --noconfirm
        ```
        Run this command a second time, if the first run automatically closes MSYS2.

2. Install Git, if not already installed
    
    ```bash
    pacman -S git --noconfirm
    ```

3. Download Gramps sources from github :

    ```bash
    git clone https://github.com/gramps-project/gramps.git
    ```

4. Build AIO :

    ```bash
    cd gramps/aio
    ./build.sh
    ```
To capture the full output of the build, use `./build.sh >& build_log.txt`

The resulting AIO installer is in the directory `gramps/aio/ucrt64/src/GrampsAIO-[appversion]-[appbuild]-[hash]_win64.exe`

The python virtual environment created during build (`c:\msys64\tmp\grampspythonenv\bin\python.exe` by default) can then be configured in Visual Studio Code and used to debug etc.

To delete the python virtual environment at the end of the build, call ```./build.sh true```. This can be useful when testing the build script.

# Useful Tips
Tips for developing Gramps on Windows with Visual Studio code.

All tips assume that you have built AIO. All commands should be run from the root directory of the Gramps source tree, unless stated otherwise.

1. Add an MSYS2 terminal option to Visual Studio Code

    This allows you to create an MSYS2 terminal within VSCode

    1. In Visual Studio Code, press Ctrl+Shift+P.
    2. Search for Preferences: Open Settings (JSON) and select it.
    3. Add the following text
        ```json
        "terminal.integrated.profiles.windows": {
            "MSYS2 UCRT64": {
                "path": "C:\\msys64\\usr\\bin\\bash.exe",
                "args": [
                    "--login",
                    "-i"
                ],
                "env": {
                    "MSYSTEM": "URCT64",
                    "CHERE_INVOKING": "1"
                }
            }
        }
        ```
        Note: If the `terminal.integrated.profiles.windows` attribute already exists, you will need to manually merge the above entry.
2. Activate python
    
    Gramps requires several python packages to run. The easiest way to ge the correct configuration is to reuse the python venv created when building AIO. To activate the python venv created during the AIO build process, run

    ```bash 
    source /tmp/grampspythonenv/bin/activate
    ```

    Tip: You can usually build AIO once and use this venv repeatedly. There is no need to build every time you change the code. This does not apply if you switch between gramps versions e.g. master to gramps60 or are changing gramps dependencies.
3. Run `mypy` locally
    1. Install mypy and type-requests: `python3 -m pip install mypy types-requests`
    2. Run mypy: `mypy`
4. Run `black` locally
    1. Install black to check all files: `python3 -m pip install black`
    2. Run black to _check_ files: `black . --check`
    3. Run black to _fix_ files: `black .`
5. Run unit tests locally
    1. Run all unit tests

        ```bash
        LANGUAGE= LANG=en_US.utf-8 GRAMPS_RESOURCES=. python -m unittest discover -p '*_test.py'
        ```
    2. Run an individual unit test

        In this example, only the `gramps.plugins.test.reports_test.TestDynamic` tests are run

        ```bash
        LANGUAGE= LANG=en_US.utf-8 GRAMPS_RESOURCES=. python -m unittest gramps.plugins.test.reports_test.TestDynamic
        ```
    
    Note: a small number of unit tests are skipped when run on Windows

