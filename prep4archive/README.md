# Prep4Archive Package

## How to compile UnRar lib from source

Via [https://doublecmd.sourceforge.io/forum/viewtopic.php?f=5&t=2267](https://doublecmd.sourceforge.io/forum/viewtopic.php?f=5&t=2267)

How to build `libunrar.so` yourself.

Requirements:
* UNRAR source, find it here: http://www.rarlab.com/rar_add.htm (at 11 nov 2018, current version was unrarsrc-5.6.8.tar.gz)
* terminal window
* root access on your system
* build-essential package installed

As always, updating is recommended before installing anything!

`sudo apt-get update`

Install build-essential package.

`sudo apt-get install build-essential`

Download and extract the UNRAR source archive into a new directory.
Open terminal and navigate to that directory, run the following command to create the libunrar.so file:

`make -f makefile lib`

Wait a few moments for it to finish, you should not get any errors.
Now run the following command to install the libunrar.so file in /usr/lib/

`sudo make install-lib`

You should now have `libunrar.so` in `/usr/lib` 
