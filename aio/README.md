The files in this directory are used to build the Windows AIO (All In One) installer.

To build AIO for the master branch :

1. install msys2
* download msys2 from <https://www.msys2.org/> .
* install with default options. 
* run "MSYS2 MINGW64"
* upgrade system : ` pacman -Syuu --noconfirm `  (twice if first run close msys2).

2. download sources from github :

```
pacman -S git --noconfirm
git clone https://github.com/gramps-project/gramps.git
```

3. build AIO :

```
cd gramps/aio
./build.sh
```

result is in gramps/aio/mingw64/src
