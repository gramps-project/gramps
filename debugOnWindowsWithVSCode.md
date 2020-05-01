#Install msys2
- https://pygobject.readthedocs.io/en/latest/getting_started.html
  - https://www.msys2.org/
  - x64 starten
    - pacman -Suy
    - pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-python-pip mingw-w64-x86_64-icu mingw-w64-x86_64-python-icu mingw-w64-python-bsddb3 mingw-w64-x86_64-python-bsddb3 mingw-w64-x86_64-python-pylint mingw-w64-x86_64-libexif mingw-w64-x86_64-gexiv2 mingw-w64-x86_64-osm-gps-map pkg-config zsh mingw-w64-x86_64-geocode-glib
    - test:
      - gtk3-demo
  - further binary packages can be found here:
    - https://packages.msys2.org

- use zsh! https://www.tfzx.net/article/2750894.html

# Life Line Chart
- pacman -S mingw-w64-x86_64-python-dateutil mingw-w64-x86_64-python-numpy mingw-w64-x86_64-python-pillow
- pip install svgwrite svgpathtools

# VSCode

- modify settings.json
```

    "python.jediEnabled": false,
    "python.pythonPath": "C:\\...\\msys2\\mingw64\\bin\\python.exe",
    "terminal.integrated.shell.windows": "C:\\...\\gramps\\msys2\\usr\\bin\\zsh.exe", 
    "terminal.integrated.shellArgs.windows": [
        "-l",
        "-i",
    ],
    "terminal.integrated.env.windows": { 
        "CHERE_INVOKING": "1",
        "MSYSTEM": "MINGW64",
        //"MSYS2_PATH_TYPE": "inherit",
    },
    "python.linting.pylintEnabled": false,
    "python.testing.autoTestDiscoverOnSaveEnabled": false,
    "python.testing.promptToConfigure": false,
    "python.testing.pytestPath": "IGNOREME",
```