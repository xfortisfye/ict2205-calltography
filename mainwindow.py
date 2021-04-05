import os
import shutil
import socket
import sys
from config import *
import threading
import queue
from threading import Thread
from PyQt5.QtCore import QObject, QThread, pyqtSignal



from PyQt5 import uic, QtWidgets, QtCore, QtGui
from worker import Worker
import time
import client_class
from msg_design import *
from listen_call_req_worker import ListenCallReqWorker
from init_call_req_worker import InitCallReqWorker







class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        # call the inherited classes __init__ method
        super(UiMainWindow, self).__init__()

        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/mainwindow.ui", self)

        # set gui window size
        self.setMinimumSize(QtCore.QSize(1280, 820))
        self.setMaximumSize(QtCore.QSize(1280, 820))
        
        # start gui at the intro page
        self.start_intro_pg()

        #self.start_recv_call_pg()

        # set up chat bubbles for messaging
        self.display_msg.setItemDelegate(MessageDelegate())
        self.model = MessageModel()
        self.display_msg.setModel(self.model)
        
        # initialise threading
        self.counter = None
        self.threadpool = QtCore.QThreadPool()

        #socket stuff
        self.client_obj = None
        self.socket = None
        
        self.call_listener_thread = None
        self.listen_call_req_work = None
        self.init_call_req_work = None

        self.receiver_name = None
        
        self.pushButton.clicked.connect(lambda: self.change_page(3)) # andy to be deleted


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

                #start call listener thread
                self.listen_call_req_work = ListenCallReqWorker(self.client_obj)
                self.listen_call_req_work.signals.caller.connect(self.init_call_recv_timer)
                self.listen_call_req_work.start()

                time.sleep(2)
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

        # pause call_lister to refresh contact list
        self.client_obj = self.listen_call_req_work.retClient()
        self.listen_call_req_work.listen_call_req_pause()
        self.listen_call_req_work.wait()

        # disable GUI to refresh contact list
        self.display_contact_list.setEnabled(False)
        self.start_call_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.display_contact_list.clear()

        # retrieve contact list from server
        online_users = self.client_obj.get_online_users()

        #start call_lister again
        self.listen_call_req_work.insertClient(self.client_obj)
        self.listen_call_req_work.listen_call_req_start()
        self.listen_call_req_work = ListenCallReqWorker(self.client_obj)
        self.listen_call_req_work.signals.caller.connect(self.init_call_recv_timer)
        self.listen_call_req_work.start()

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
            # store the receiver_name
            self.receiver_name = self.display_contact_list.currentItem().text()


            self.client_obj = self.listen_call_req_work.retClient()
            self.listen_call_req_work.listen_call_req_pause()
            self.listen_call_req_work.wait()



            #self.client_obj.initiate_call_req(self.receiver_name)

            # if succeeded, change to send call page
            self.stop_contact_pg()
            self.start_send_call_pg()

            # start sending call request
            self.init_call_req_work = InitCallReqWorker(self.client_obj, self.receiver_name)
            self.init_call_send_timer(self.receiver_name)

            self.init_call_req_work.signals.finished.connect(self.init_call_send_timer)
            self.init_call_req_work.start()
            #self.init_call_req_work.wait()


            

            return True
    
    def init_receive_call(self):
        
        # listen for call response

        # send response back

        # if succeeded, change to receive call page
        self.stop_contact_pg()
        self.start_recv_call_pg()

    '''
    Page 2/Send Call Page's Functions 
    '''
    def stop_send_call(self):

            #todo shift (listencall thread should pause when call has been accepting)
            # listen for response
            self.listen_call_req_work.insertClient(self.client_obj)
            self.listen_call_req_work.listen_call_req_start()
            self.listen_call_req_work = ListenCallReqWorker(self.client_obj)
            self.listen_call_req_work.signals.caller.connect(self.init_call_recv_timer)
            self.listen_call_req_work.start()

            # perform all the actions to process stop call
            self.stop_send_call_pg()

    

    '''
    Page 3/Receive Call Page's Functions 
    '''

    def init_accept_call(self):
        # perform all the actions to process accept call
        self.listen_call_req_work.wait()
        #self.client_obj.send_call_ack()
        thread = threading.Thread(target=self.client_obj.send_call_ack)
        thread.start()



        self.start_chat_pg()


    def init_reject_call(self):
        # perform all the actions to process reject call

        self.client_obj.send_call_dec()

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
        self.model.add_message(USER_ME, message)
        self.model.add_message(USER_THEM, message) # andy put for fun can delete

    def display_recv_msg():
        self.model.add_message(USER_THEM, message)

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
        #reminder to andy to use this for send and recv.
        #self.start_call_button.clicked.disconnect()
        #self.refresh_button.clicked.disconnect()
        pass

    def start_send_call_pg(self):
        self.stop_call_button.clicked.connect(lambda: self.stop_send_call())
        self.change_page(2)
    
    def stop_send_call_pg(self):
        self.stop_call_button.clicked.disconnect()
        self.start_contact_pg()

    def start_recv_call_pg(self):
        self.accept_call_button.clicked.connect(lambda: self.init_accept_call())
        self.reject_call_button.clicked.connect(lambda: self.init_reject_call())
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
        #self.mute_button.clicked.connect(lambda: self.init_send_msg()) # andy if time persist then we do
        self.end_call_button.clicked.connect(lambda: self.init_end_call())
        self.change_page(4)

    def stop_chat_pg(self):
        self.display_name.setEnabled(False)
        self.display_msg.setEnabled(False)
        self.input_msg.setEnabled(False)
        self.send_msg_button.setEnabled(False)
        self.mute_button.setEnabled(False)
        self.send_msg_button.clicked.disconnect()
        #self.mute_button.clicked.disconnect() # andy if time persist then we do
        self.end_call_button.clicked.disconnect()
        self.model.clear()
        self.start_contact_pg()

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

    def init_call_send_timer(self, caller):
        self.listen_call_req_timer = QtCore.QTimer()
        self.listen_call_req_timer.setInterval(1000)
        self.counter = 1
        self.listen_call_req_timer.timeout.connect(lambda caller=caller: self.print_call_send(caller))
        self.listen_call_req_timer.start()

    def init_call_recv_timer(self, caller_name):
        self.listen_call_req_timer = QtCore.QTimer()
        self.listen_call_req_timer.setInterval(1000)
        self.counter = 1
        self.listen_call_req_timer.timeout.connect(lambda caller_name=caller_name: self.print_call_recv(caller_name))
        self.listen_call_req_timer.start()

    def print_call_send(self, caller):
        dot_string = ""
        for _ in range(self.counter):
            dot_string += "."
        self.send_call_text.setText("Calling " + self.receiver_name + dot_string)
        self.counter += 1

        if self.counter > 3:
            self.counter = 1
    
    def print_call_recv(self, caller_name):
        self.init_receive_call()
        dot_string = ""
        for _ in range(self.counter):
            dot_string += "."
        self.recv_call_text.setText(caller_name + " is calling" + dot_string)
        self.counter += 1

        if self.counter > 3:
            self.counter = 1

    def display_calling_screen(self):
        self.stop_contact_pg()
        self.start_send_call_pg()