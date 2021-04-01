import sys
from config import *
import threading
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from worker import Worker
from keydialog import KeyDialog
import time

class UiMainWindow(QtWidgets.QStackedWidget):

    def __init__(self):
        # call the inherited classes __init__ method
        super(UiMainWindow, self).__init__()
        # Obfuscation.clear()

        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/mainwindow.ui", self)

        # set gui window size
        self.setMinimumSize(QtCore.QSize(500, 820))
        self.setMaximumSize(QtCore.QSize(500, 820))

        # keydialog = KeyDialog()

        #     if keydialog.getKeyInfo() 

        # # initialise gui functions
        # self.import_apk_button.clicked.connect(lambda: self.importApkDialog())
        # self.obf_package_button.setEnabled(False)
        # self.obf_smali_button.setEnabled(False)
        # self.export_apk_button.setEnabled(False)
        # self.printLogs(SYSTEM, "Begin the program by decompiling your APK.")

        # self.threadpool = QtCore.QThreadPool()

    # def thread_complete(self, function, url, name):
    #     if function == "importApk":
    #         self.timer.stop()

    # def startImportThread(self, function, url, name):
    #     # Pass the function to execute
    #     if function == "importApk":
    #         worker = Worker(Obfuscation.importFile, url)  # Any other args, kwargs are passed to the run function
    #         worker.signals.finished.connect(lambda function=function, url=url, name=name: self.thread_complete(function, url, name))

    #     # Execute
    #     self.threadpool.start(worker)

    # def startExportThread(self, function, url, name, key):
    #     if function == "exportApk":
    #         worker = Worker(Obfuscation.exportApk, url, name, key)  # Any other args, kwargs are passed to the run function
    #         worker.signals.finished.connect(lambda function=function, url=url, name=name: self.thread_complete(function, url, name))

    #     self.threadpool.start(worker)

    # def recurring_timer(self):
    #     self.printLogs(LOADER, ".")

    def isSignalConnected(self, obj, name):
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False