import os
import shutil
import sys
import resources
from mainwindow import UiMainWindow
from PyQt5 import QtWidgets

def main():
    if os.path.exists("__pycache__/"):
            shutil.rmtree("__pycache__/")
    
    
    # Launching the GUI
    app = QtWidgets.QApplication(sys.argv)
    # app.aboutToQuit.connect(lambda: Obfuscation.clear())
    mainwindow = UiMainWindow()
    mainwindow.setWindowTitle("Someone name this app plz")
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
