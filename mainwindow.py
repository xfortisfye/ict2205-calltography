import os
import shutil
import socket
import sys
from config import *
import threading
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from worker import Worker
import time
import client_class

class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        # call the inherited classes __init__ method
        super(UiMainWindow, self).__init__()

        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/mainwindow.ui", self)

        # set gui window size
        # self.setMinimumSize(QtCore.QSize(450, 700))
        # self.setMaximumSize(QtCore.QSize(450, 700))
        self.setMinimumSize(QtCore.QSize(1280, 820))
        self.setMaximumSize(QtCore.QSize(1280, 820))
        
        self.start_intro_pg()
        #self.start_recv_call_pg()
        
        # initialise threading
        self.counter = None
        self.threadpool = QtCore.QThreadPool()

        #socket stuff
        self.client_obj = None
        self.socket = None


    '''
    Page 0/Intro Page's Functions 
    '''

    def init_intro(self):
        self.init_intro_button.clicked.disconnect()
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.counter = 1
        self.timer.timeout.connect(self.init_loading_timer)
        self.timer.start()
        
        worker = Worker(self.startServerAuth)
        worker.signals.result.connect(self.serverAuthResult)
        self.threadpool.start(worker)

    def set_nickname(self):
        if self.input_nickname.text():
            # set nickname
            self.current_nickname.setText(self.input_nickname.text())
            # update server the nickname
            if self.client_obj.set_username(self.get_nickname()):
                # get new contact list from server
                self.refresh_contact_list()
                # start contact page
                self.stop_nick_pg()
            else:
                self.nick_error_msg.setStyleSheet("QLabel {color: red;}")
                self.nick_error_msg.setText("Nickname has been taken, choose another one!")
        else:
            self.nick_error_msg.setStyleSheet("QLabel {color: red;}")
            self.nick_error_msg.setText("No nickname has been set!")

    def get_nickname(self):
        return self.current_nickname.text()            

    '''
    Page 1/Contact Page's Functions 
    '''

    def refresh_contact_list(self):
        # disable GUI to refresh contact list
        self.display_contact_list.setEnabled(False)
        self.start_call_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.display_contact_list.clear()

        # retrieve contact list from server
        online_users = self.client_obj.get_online_users()

        if online_users:
            for users in online_users:
                self.display_contact_list.addItem(users)
            
            # enable GUI upon completion
            self.display_contact_list.setEnabled(True)
            self.start_call_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
        else:
            self.contact_error_msg.setText("Failed to update contact list")
            pass

    def init_send_call(self):
        if self.display_contact_list.currentItem() is None:
            self.contact_error_msg.setText("You have not chose any contact to call.")
            return False
        else:
            self.send_call_text.setText("You are calling...\n" + self.display_contact_list.currentItem().text())
        
            # 1) send _NAME_CALL_ to Bob he is available

            # 3) upon receive _NAME_RECV_, wait for server send Bob's IP
    
            # 4) send _CALL_REQ_

            self.start_send_call_pg()
            return True
    
    def init_receive_call(self):

        # 2) send _NAME_RECV_ back to Alice

        # 2.5) do we we want to receive Alice's IP for double checking <- can dont do

        # 5) wait for _CALL_REQ_

        # 6) if succeeded, change to send call page
        self.start_recv_call_pg()

    '''
    Page 2/Send Call Page's Functions 
    '''
    def stop_send_call(self):
            # Alice to send _CALL_END_ to Bob since she called wrongly

            # perform all the actions to process stop call
            self.stop_send_call_pg()

    #####

    # there needs to be a function of a listener to grab for _CALL_ACC_ by Alice to start gen ECDHE keys
    #####

    '''
    Page 3/Receive Call Page's Functions 
    '''

    def init_accept_call(self):
        # perform all the actions to process accept call

        # Bob to send _CALL_ACC_ to Alice since he okay to talk
        
        # start generating ecdsa keys


        self.start_chat_pg()

    def init_reject_call(self):
        # perform all the actions to process reject call

        # Bob to send _CALL_REJ_ to Alice since he lazy to talk

        self.stop_recv_call_pg()

    '''
    Page 4/Chat Page's Functions 
    '''
    def init_end_call(self):
        # perform all the actions to process end call during chat
        
        # send _CALL_END_ 

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
        self.start_nick_pg()

    def start_nick_pg(self):
        self.set_nick_button.clicked.connect(lambda: self.set_nickname())
        self.bot_sw.setCurrentIndex(5)

    def stop_nick_pg(self):
        self.set_nick_button.clicked.disconnect()
        self.start_contact_pg()

    def start_contact_pg(self):
        self.start_call_button.clicked.connect(lambda: self.init_send_call())
        self.refresh_button.clicked.connect(lambda: self.refresh_contact_list())
        self.change_page(1)

    def stop_contact_pg(self):
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
        self.display_name.setEnabled(True)
        self.display_msg.setEnabled(True)
        self.input_msg.setEnabled(True)
        self.send_msg_button.setEnabled(True)
        self.mute_button.setEnabled(True)
        self.send_msg_button.clicked.connect(lambda: self.init_send_msg())
        #self.mute_button.clicked.connect(lambda: self.init_send_msg())
        self.end_call_button.clicked.connect(lambda: self.init_end_call())
        self.change_page(4)

    def stop_chat_pg(self):
        self.display_name.setEnabled(False)
        self.display_msg.setEnabled(False)
        self.input_msg.setEnabled(False)
        self.send_msg_button.setEnabled(False)
        self.mute_button.setEnabled(False)
        self.send_msg_button.clicked.disconnect()
        #self.mute_button.clicked.disconnect()
        self.end_call_button.clicked.disconnect()
        self.start_contact_pg()
        self.display_msg.clear()

    def isSignalConnected(self, obj, name):
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False

    def change_page(self, i):
        self.top_sw.setCurrentIndex(i)
        self.bot_sw.setCurrentIndex(i)


    ########################
    #Client Socket Stuff
    ##################

    def connect_server(self):
        host = '127.0.0.1'
        port = 8888

        self.socket = socket.socket()
        print('Waiting for connection response')
        try:
            self.socket.connect((host, port))
        except socket.error as e:
            print(str(e))


    ########################
    #Threading stuff
    ##################

    def startServerAuth(self):
        #build socket
        self.connect_server()

        #get server connection msg
        res = self.socket.recv(1024)

        print(res.decode('utf-8'))
        if res:
            proceed = True

            self.client_obj = client_class.Client(self.socket)

            # perform server authentication
            print("\n")
            print("=================================")
            print("Performing server authentication")
            print("=================================")
            if (self.client_obj.auth_server()):
                print("Server authentication successful\n\n")
            else:
                proceed = False
                return "Server authentication failed"

            # perform ecdh exchange
            if proceed:
                print("=================================")
                print("Performing ECDH exchange")
                print("=================================")
                if (self.client_obj.exchange_ecdh()):
                    print("ECDH exchange successful\n\n")
                    return None
                else:
                    return "ECDH exchange failed"
        else:
            return "Failed to connect to server"


    def init_loading_timer(self):
        self.init_error_msg.setStyleSheet("QLabel {color: black;}")

        dot_string = ""
        for _ in range(self.counter):
            dot_string += "."
        self.init_error_msg.setText("Loading " + dot_string)
        self.counter += 1

        if self.counter > 3:
            self.counter = 1

    def serverAuthResult(self, error):
        self.timer.stop()
        if error:
            self.init_intro_button.clicked.connect(lambda: self.init_intro())
            self.init_error_msg.setStyleSheet("QLabel {color: red;}")
            self.init_error_msg.setText(error)
        else:
            self.stop_intro_pg()
            