import os
import shutil
import sys
from config import *
import threading
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from worker import Worker
import time

class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        # call the inherited classes __init__ method
        super(UiMainWindow, self).__init__()

        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/mainwindow.ui", self)

        # set gui window size
        self.setMinimumSize(QtCore.QSize(450, 700))
        self.setMaximumSize(QtCore.QSize(450, 700))
        self.display_contact_list.setStyleSheet("background-color: white")
        
        self.start_intro_pg()
        firstLaunch = True
        #self.start_recv_call_pg()

        # sample
        self.display_contact_list.addItem("Alice")
        self.display_contact_list.addItem("Bob")

    '''
    Page 0/Intro Page's Functions 
    '''

    def init_intro(self):
        # gen of client's RSA Keys
        # perform authentication with server
        # send authentication okay to server
        
        self.stop_intro_pg()
            

    '''
    Page 1/Contact Page's Functions 
    '''
    def set_nickname(self):
        if self.input_nickname.text():
            # set nickname
            self.display_contact_msg.setText("Hello,")
            self.current_nickname.setText(self.input_nickname.text())
            
            # disable GUI to update server
            self.set_nickname_button.setEnabled(False)
            self.display_contact_list.setEnabled(False)
            self.start_call_button.setEnabled(False)
            self.refresh_button.setEnabled(False)


            # update server the nickname
            print (self.get_nickname())


            # get new contact list from server

            # enable GUI upon completion
            self.set_nickname_button.setEnabled(True)
            self.display_contact_list.setEnabled(True)
            self.start_call_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
        else:
            self.display_contact_msg.setText("No nickname has been set!")

    def get_nickname(self):
        return self.current_nickname.text()

    def init_send_call(self):
        if self.display_contact_list.currentItem() is None:
            # display some error message for not selecting contact
            return False
        else:
            self.send_call_text.setText("You are trying to call...\n" + self.display_contact_list.currentItem().text())
            # start to gen RSA's stuff here and perform authentication
            
            # if succeeded, change to send call page
            self.start_send_call_pg()
            return True
    
    def init_receive_call(self):
        # start to gen RSA's stuff here and perform authentication

        # if succeeded, change to send call page
        self.start_recv_call_pg()

    '''
    Page 2/Send Call Page's Functions 
    '''
    def stop_send_call(self):
            # perform all the actions to process stop call

            self.stop_send_call_pg()
        
    def refresh_contact_list(self):
        self.display_contact_list.clear()

        # retrieve contact list from server
        
        # sample
        self.display_contact_list.addItem("Alice")
        self.display_contact_list.addItem("Bob")
        self.display_contact_list.addItem("Charlie")
        self.display_contact_list.addItem("Delta")

    '''
    Page 3/Receive Call Page's Functions 
    '''

    def init_accept_call(self):
        # perform all the actions to process accept call

        # start generating ecdsa keys


        self.start_chat_pg()

    def init_reject_call(self):
        # perform all the actions to process reject call

        self.stop_recv_call_pg()

    '''
    Page 4/Chat Page's Functions 
    '''
    def init_end_call(self):
        # perform all the actions to process end call during chat

        self.stop_chat_pg()

    def init_send_msg(self):
        if self.input_msg.toPlainText():
           message = self.input_msg.toPlainText()
           self.input_msg.clear()
           # process message

           ####
           self.display_send_msg(message)
           
        else:
            pass

    def display_send_msg(self, message):
        self.display_msg.moveCursor(QtGui.QTextCursor.End)
        self.display_msg.setTextColor(QtCore.Qt.red)
        self.display_msg.setTextBackgroundColor(QtCore.Qt.black)
        self.display_msg.append(self.get_nickname())
        self.display_msg.setTextColor(QtCore.Qt.red)
        self.display_msg.setTextBackgroundColor(QtCore.Qt.white)
        self.display_msg.insertPlainText(message)
        self.display_msg.ensureCursorVisible()

    def display_recv_msg():
        # get receiver name
        self.display_msg.moveCursor(QtGui.QTextCursor.End)
        self.display_msg.setTextColor(QtCore.Qt.red)
        self.display_msg.setTextBackgroundColor(QtCore.Qt.black)
        self.display_msg.append(self.get_nickname()) #adjust receiver's name
        self.display_msg.setTextColor(QtCore.Qt.red)
        self.display_msg.setTextBackgroundColor(QtCore.Qt.white)
        self.display_msg.insertPlainText(message)
        self.display_msg.ensureCursorVisible()

    '''
    Misc Functions
    '''
    def shutdown():
        # perform misc tasks 
        if os.path.exists("__pycache__/"):
            shutil.rmtree("__pycache__/")
    

    '''
    Functions to Start / Stop the different pages
    '''

    def start_intro_pg(self):
        self.init_intro_button.clicked.connect(lambda: self.init_intro())
        self.change_page(0)

    def stop_intro_pg(self):
        self.init_intro_button.clicked.disconnect()
        self.start_contact_pg()

    def start_contact_pg(self):
        self.set_nickname_button.clicked.connect(lambda: self.set_nickname())
        self.start_call_button.clicked.connect(lambda: self.init_send_call())
        self.refresh_button.clicked.connect(lambda: self.refresh_contact_list())
        self.change_page(1)

    def stop_contact_pg(self):
        self.set_nickname_button.clicked.disconnect()
        self.start_call_button.clicked.disconnect()
        self.refresh_button.clicked.disconnect()

    def start_send_call_pg(self):
        self.stop_call_button.clicked.connect(lambda: self.stop_send_call())
        self.change_page(2)
    
    def stop_send_call_pg(self):
        self.stop_call_button.clicked.disconnect()
        self.start_contact_pg()

    def start_recv_call_pg(self):
        self.accept_call_button.clicked.connect(lambda: self.init_accept_call())
        self.reject_call_button.clicked.connect(lambda: self.init_reject_call())
        self.recv_call_text.setText(self.get_nickname() + "\n is calling...") # change to Alice name
        self.change_page(3)

    def stop_recv_call_pg(self):
        self.accept_call_button.clicked.disconnect()
        self.reject_call_button.clicked.disconnect()
        self.start_contact_pg()

    def start_chat_pg(self):
        self.end_call_button.clicked.connect(lambda: self.init_end_call())
        self.send_msg_button.clicked.connect(lambda: self.init_send_msg())
        self.change_page(4)

    def stop_chat_pg(self):
        self.end_call_button.clicked.disconnect()
        self.send_msg_button.clicked.disconnect()
        self.start_contact_pg()

    def isSignalConnected(self, obj, name):
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False

    def change_page(self, i):
        self.sw_page.setCurrentIndex(i)


    ########################
    #Threading stuff
    ##################
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
    #     self.printLogs(LOADER, ".")s