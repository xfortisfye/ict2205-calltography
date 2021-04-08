import sys
import resources
from mainwindow import UiMainWindow
from PyQt5 import QtWidgets

def main():
    # Launching the GUI
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: UiMainWindow.shutdown())
    mainwindow = UiMainWindow()
    mainwindow.show()
    sys.exit(app.exec_())    

if __name__ == "__main__":
    main()
