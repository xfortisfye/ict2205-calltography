import sys
from config import *
import threading
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from worker import Worker
from keydialog import KeyDialog
import time

class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        # call the inherited classes __init__ method
        super(UiMainWindow, self).__init__()
        # Obfuscation.clear()

        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/mainwindow.ui", self)

        # set gui window size
        self.setMinimumSize(QtCore.QSize(500, 800))
        self.setMaximumSize(QtCore.QSize(500, 800))
        
        self.startMainPg(self.sw_page)




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

    def setInitNick(self):
        if not self.init_input_nick.text():
            pass
        else: 
            self.input_nickname.setText(self.init_input_nick.text())
            self.current_nickname.setText(self.init_input_nick.text())
            self.stopMainPg(self.sw_page)

    def setNickname(self):
        if not self.input_nickname.text():
            pass
        else: 
            self.current_nickname.setText(self.input_nickname.text())

    def startMainPg(self, sw_page):
        self.init_set_nick_button.clicked.connect(lambda: self.setInitNick())
        self.changePage(sw_page, 0)

    def stopMainPg(self, sw_page):
        self.init_set_nick_button.clicked.disconnect()
        self.startContactPg(self.sw_page)

    def startContactPg(self, sw_page):
        self.set_nickname_button.clicked.connect(lambda: self.setNickname())
        self.start_call_button.clicked.connect(lambda: self.startCallPg(sw_page))
        # self.refresh_button.clicked.connect(lambda: self.())
        self.changePage(sw_page, 1)

    def stopContactPg(self):
        self.set_nickname_button.clicked.disconnect()
        self.start_call_button.clicked.disconnect()
        self.refresh_button.clicked.disconnect()

    def startCallPg(self, sw_page):
        self.accept_call_button.clicked.connect(lambda: self.startChatPg(sw_page))
        self.reject_call_button.clicked.connect(lambda: self.stopCallPg(sw_page))
        self.changePage(sw_page, 2)

    def stopCallPg(self, sw_page):
        self.accept_call_button.clicked.disconnect()
        self.reject_call_button.clicked.disconnect()
        self.startContactPg(sw_page)

    def startChatPg(self, sw_page):
        self.end_call_button.clicked.connect(lambda: self.stopChatPg(sw_page))
        # self.send_msg_button.clicked.connect(lambda: self.stopChatPg(sw_page))
        self.changePage(sw_page, 3)

    def stopChatPg(self, sw_page):
        self.end_call_button.clicked.disconnect()
        # self.send_msg_button.clicked.disconnect()
        self.startContactPg(sw_page)

    def isSignalConnected(self, obj, name):
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False

    def changePage(self, sw_page, i):
        self.sw_page.setCurrentIndex(i)