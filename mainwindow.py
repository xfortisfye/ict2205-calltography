import os
import shutil
import socket
import sys
from config import *
import threading
import queue
from threading import Thread
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PyQt5.QtMultimedia
import PyQt5.QtMultimediaWidgets

from PyQt5 import uic, QtWidgets, QtCore, QtGui
import time
import client_class
from msg_design import *
from server_auth_worker import ServerAuthWorker
from listen_req_worker import ListenRequestWorker
from init_req_worker import InitRequestWorker
from send_ack_worker import SendAckWorker

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

        # set up chat bubbles for messaging
        self.display_msg.setItemDelegate(MessageDelegate())
        self.model = MessageModel()
        self.display_msg.setModel(self.model)

        #socket stuff
        self.client_obj = None
        self.socket = None
        
        # threading stuff
        self.counter = None
        self.server_auth_thread = None
        self.listen_req_thread = None
        self.init_req_thread = None
        self.send_ack_thread = None

        # naming
        self.sender_name = None
        self.receiver_name = None

        # intro video
        intro_file = f"{ABSOLUTE_PATH}/img/intro.mp4"
        self.intro_pl = PyQt5.QtMultimedia.QMediaPlaylist()
        self.intro_mp = PyQt5.QtMultimedia.QMediaPlayer(None, PyQt5.QtMultimedia.QMediaPlayer.VideoSurface)
        self.intro_mp.setVideoOutput(self.intro_vw)
        self.intro_pl.addMedia(PyQt5.QtMultimedia.QMediaContent(PyQt5.QtCore.QUrl.fromLocalFile(intro_file)))
        self.intro_pl.setPlaybackMode(PyQt5.QtMultimedia.QMediaPlaylist.Loop)
        self.intro_mp.setPlaylist(self.intro_pl)
        self.intro_vw.show()
        self.intro_mp.setPosition(0)
        self.intro_mp.play()

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
        
        self.server_auth_thread = ServerAuthWorker(self.startServerAuth)
        self.server_auth_thread.signals.result.connect(self.serverAuthResult)
        self.server_auth_thread.start()
        self.server_auth_thread.wait()
        self.server_auth_thread.exit()

    def set_nickname(self):
        if self.input_nickname.text():
            # set nickname
            self.current_nickname.setText(self.input_nickname.text())
            # update server the nickname
            if self.client_obj.set_username(self.get_nickname()):
                # disconnect unused signals
                self.server_auth_thread.signals.result.disconnect()
                self.timer.timeout.disconnect()

                #start listen for request thread
                self.listen_req_thread = ListenRequestWorker(self.client_obj)
                self.listen_req_thread.signals.caller.connect(self.init_receive_call) #andy
                self.listen_req_thread.start()

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
        self.client_obj = self.listen_req_thread.retClient()
        self.listen_req_thread.listen_call_req_pause()
        self.listen_req_thread.wait()
        self.listen_req_thread.exit()
        self.listen_req_thread.signals.caller.disconnect()

        # disable GUI to refresh contact list
        self.display_contact_list.setEnabled(False)
        self.start_call_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.display_contact_list.clear()

        # retrieve contact list from server
        online_users = self.client_obj.get_online_users()

        #start call_lister again
        self.listen_req_thread.insertClient(self.client_obj)
        self.listen_req_thread.listen_call_req_start()
        self.listen_req_thread = ListenRequestWorker(self.client_obj)
        self.listen_req_thread.signals.caller.connect(self.init_receive_call)
        self.listen_req_thread.start()

        if online_users:
            for users in online_users:
                self.display_contact_list.addItem(users)
            
            # enable GUI upon completion
            self.display_contact_list.setEnabled(True)
            self.start_call_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
        else:
            self.contact_error_msg.setText("Failed to update contact list")
            self.display_contact_list.setEnabled(True)
            self.start_call_button.setEnabled(True)
            self.refresh_button.setEnabled(True)

    def init_send_call(self):
        if self.display_contact_list.currentItem() is None:
            self.contact_error_msg.setText("You have not chose any contact to call.")
        else:
            # store the receiver_name
            self.receiver_name = self.display_contact_list.currentItem().text()

            # stop listening for request
            self.client_obj = self.listen_req_thread.retClient()
            self.listen_req_thread.listen_call_req_pause()
            self.listen_req_thread.wait()
            self.listen_req_thread.exit()

            # if succeeded, change to send call page
            self.stop_contact_pg()
            self.start_send_call_pg()

            # start sending call request
            self.init_req_thread = InitRequestWorker(self.client_obj, self.receiver_name)
            self.init_req_thread.signals.start_timer.connect(self.init_send_timer)
            self.init_req_thread.signals.call_accepted.connect(self.init_call_accepted)
            self.init_req_thread.start()       

    '''
    Page 2/Send Call Page's Functions 
    '''

    def init_send_timer(self):
        self.send_timer = QtCore.QTimer()
        self.send_timer.setInterval(1000)
        self.counter = 1
        self.send_timer.timeout.connect(self.print_send_timer)
        self.send_timer.start()

    def print_send_timer(self):
        dot_string = ""
        for _ in range(self.counter):
            dot_string += "."
        self.send_call_text.setText("Calling \n" + self.receiver_name + dot_string)
        self.counter += 1

        if self.counter > 3:
            self.counter = 1

    def init_call_accepted(self, key, caller_ip):
        self.init_req_thread.wait()
        self.init_req_thread.exit()
        self.send_timer.timeout.disconnect()
        self.init_req_thread.signals.start_timer.disconnect()
        self.init_req_thread.signals.call_accepted.disconnect()
        self.send_timer.stop()
        self.stop_send_call_pg()
        self.start_chat_pg(self.receiver_name, key, caller_ip)

    def stop_send_call(self):
            # perform all the actions to process stop call
        print("rest")

        self.client_obj =  self.init_req_thread.retClient()
        self.init_req_thread.init_req_pause()
        self.init_req_thread.wait()
        self.init_req_thread.exit()
        self.send_timer.timeout.disconnect()
        self.init_req_thread.signals.start_timer.disconnect()
        self.init_req_thread.signals.call_accepted.disconnect()

        self.client_obj.send_call_canc()


        self.stop_send_call_pg()
        self.start_contact_pg()

    '''
    Page 3/Receive Call Page's Functions 
    '''

    def init_receive_call(self, caller_name):
        self.sender_name = caller_name

        #HI ANDY I SHIFTED THIS CHUNK BELOW TO INTI ACCPET CALL
        #cause we want to still keep the listener active even when they recieve the call reqeust
        # we only want to stop it when the user accepts the call
        # self.client_obj = self.listen_req_thread.retClient()
        # self.listen_req_thread.listen_call_req_pause()
        # self.listen_req_thread.wait()
        # self.listen_req_thread.exit()
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        self.stop_contact_pg()
        self.start_recv_call_pg()
        
        self.receive_timer = QtCore.QTimer()
        self.receive_timer.setInterval(1000)
        self.counter = 1
        self.receive_timer.timeout.connect(lambda caller_name=caller_name: self.print_recv_timer(caller_name))
        self.receive_timer.start()

    def init_accept_call(self):

        # HI ANDY I SHIFTED THIS CHUNK BELOW TO INTI ACCPET CALL
        self.client_obj = self.listen_req_thread.retClient()
        self.listen_req_thread.listen_call_req_pause()
        self.listen_req_thread.wait()
        self.listen_req_thread.exit()

        self.send_ack_thread = SendAckWorker(self.client_obj)
        self.send_ack_thread.signals.call_accepted.connect(self.post_accept_call)
        self.send_ack_thread.start()
        self.send_ack_thread.wait()

    def post_accept_call(self, key, caller_ip):
        self.receive_timer.stop()
        self.send_ack_thread.exit()
        self.receive_timer.timeout.disconnect()
        self.send_ack_thread.signals.call_accepted.disconnect()
        self.stop_recv_call_pg()
        self.start_chat_pg(self.sender_name, key, caller_ip)
        
    def init_reject_call(self):
        # perform all the actions to process reject call
        self.client_obj.send_call_dec()
        self.stop_recv_call_pg()
        self.start_contact_pg()

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
        self.intro_mp.pause()
        self.start_contact_pg()

    def start_contact_pg(self):
        self.start_call_button.clicked.connect(lambda: self.init_send_call())
        self.refresh_button.clicked.connect(lambda: self.refresh_contact_list())
        self.refresh_contact_list()
        self.change_page(1)

    def stop_contact_pg(self):
        self.start_call_button.clicked.disconnect()
        self.refresh_button.clicked.disconnect()

    def start_send_call_pg(self):
        self.stop_call_button.clicked.connect(lambda: self.stop_send_call())
        self.change_page(2)
    
    def stop_send_call_pg(self):
        self.stop_call_button.clicked.disconnect()

    def start_recv_call_pg(self):
        self.accept_call_button.clicked.connect(lambda: self.init_accept_call())
        self.reject_call_button.clicked.connect(lambda: self.init_reject_call())
        self.change_page(3)

    def stop_recv_call_pg(self):
        self.accept_call_button.clicked.disconnect()
        self.reject_call_button.clicked.disconnect()
        self.start_contact_pg()

    def start_chat_pg(self, name, key, caller_ip):
        self.display_name.setEnabled(True)
        self.display_name.setText(name + caller_ip)
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
        self.display_name.setText("")
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

    # def init_call_recv_timer(self, caller_name):
        
    
    def print_recv_timer(self, caller_name):
        dot_string = ""
        for _ in range(self.counter):
            dot_string += "."
        self.recv_call_text.setText(caller_name + "\nis calling" + dot_string)
        self.counter += 1

        if self.counter > 3:
            self.counter = 1
