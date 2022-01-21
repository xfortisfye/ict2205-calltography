# ict2205-calltography

## Setting Up
### Windows
#### Install Dependencies
1. Install PyQt5
```bash
> cd \Path\to\ict2205-calltography
> pip install PyQt5
```
2. Install pycryptodome
```bash
> cd \Path\to\ict2205-calltography
> pip install pycryptodome
```
If above doesn't work, uninstall the following and try again.
```bash
> pip uninstall pycrypto
> pip uninstall crypto
> pip uninstall pycryptodome
> pip uninstall pycryptodomex
```
3. Install cryptography
```bash
> cd \Path\to\ict2205-calltography
> pip install cryptography
```
4. Install PyAudio
```bash
> cd \Path\to\ict2205-calltography
> pip install wheel
> pip install PyAudio
```
If above doesn't work, [Install](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) your respective wheel version to `\Path\to\ict2205-calltography`
Checking of python version: `> python`
```bash
> pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```
5. Install [codecs](https://files3.codecguide.com/K-Lite_Codec_Pack_1610_Full.exe)

#### Setting up GNU Make (Optional)
1. [Install](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=nchc&download=) Make for Windows
2. Set up [environment path](https://github.com/xfortisfye/303-see-other/blob/main/env-path.md). Usually value is `C:\Program Files (x86)\GnuWin32\bin`

## Running the Project
### Option 1: Using Python
1. Run server.py (currently is set to localhost)
```bash
> cd \Path\to\ict2205-calltography
> py server.py
```
2. Run main.py
```bash
> cd \Path\to\ict2205-calltography
> py main.py
```

### Option 2: Using GNU Make (For main.py only)
1. To run the program
```bash
> cd \Path\to\ict2205-calltography
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
| **Chua Chiang Sheng, Andy** | [@xfortisfye](https://github.com/xfortisfye)   |
