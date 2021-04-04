# ict2205-crypto-secure-comms

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
  - [Windows](#windows)
    - [Cloning GitHub Repository (using vscode)](#cloning-github-repository-using-vscode)
    - [Installing Python](#installing-python)
    - [Installing Dependencies](#installing-dependencies)
    - [Setting up GNU Make](#setting-up-gnu-make)
- [Running the Project](#running-the-project)
  - [Option 1: Using GNU Make](#option-1-using-gnu-make)
- [Collaborators](#collaborators)

## Setting Up
### Windows
#### Cloning GitHub Repository (using [vscode](https://code.visualstudio.com/))
1. Press: Ctrl + Shift + P
2. Type: 'Clone' and select 'Git: Clone'
3. Paste `https://github.com/ehandywhyy/ict2205-crypto-secure-comms`
4. Enter your GitHub credentials & select a location to save the repository

#### Installing Dependencies
1. Install PyQt5
```bash
> cd \Path\to\ict2205-crypto-secure-comms
> pip install PyQt5
```
2. Install pycryptodome
```bash
> cd \Path\to\ict2205-crypto-secure-comms
> pip install pycryptodome
```
If above doesn't work, uninstall the following and try again.
```bash
> pip uninstall pycrypto
> pip uninstall crypto
> pip uninstall pycryptodome
> pip uninstall pycryptodomex
```
3. Install PyAudio
```bash
> cd \Path\to\ict2205-crypto-secure-comms
> pip install wheel
> pip install PyAudio
```

If above doesn't work, [Install](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) your respective wheel version to `\Path\to\ict2205-crypto-secure-comms`
Checking of python version: `> python`
```bash
> pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

#### Setting up GNU Make (Optional)
1. [Install](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=nchc&download=) Make for Windows
2. Set up environment PATH, if not you will not be unable to run `make`
   1. Right-click on 'This PC' > Properties > Advance System Settings > Environment Variables
   2. Under System Variable, Select PATH
   3. Click on Edit, enter Make location. Usually: `C:\Program Files (x86)\GnuWin32\bin`

## Running the Project
### Option 1: Using GNU Make
1. To run the program
```bash
> cd \Path\to\ict2207-mob-sec-obfuscation
> make
```
2. To clean compiled files (.pyc)
```bash
> make clean
```


## Collaborators
| Name                        | GitHub                                         |
| --------------------------- | ---------------------------------------------- | 
| **Ong Tiong Poh**           | [@Swipaaar](https://github.com/Swipaaar)       |
| **Poh Xiang Bin**           | [@xenbon](https://github.com/xenbon)           |
| **Dylan Yong Kenn Litt**    | [@milosaur](https://github.com/milosaur)       | 
| **Nicholas Poon Keet Hoe**  | [@roodysfun](https://github.com/roodysfun)     |
| **Chua Chiang Sheng, Andy** | [@ehandywhyy](https://github.com/ehandywhyy)   |