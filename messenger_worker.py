from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
from call_client import Sender
from call_server import Receiver
import msg_processor
import cryptodriver
import time



class MessengerWorker(QtCore.QThread):
    def __init__(self, role, messenger):
        super(MessengerWorker, self).__init__()

        self.role = role
        self.messenger = messenger

    @QtCore.pyqtSlot()
    def run(self):
        if self.role == "sender":
            print("sender host : " + str(self.messenger.host) +  " port: " + str(self.messenger.port) + " key : " + str(self.messenger.key))
            self.messenger.reset_global_variables_listen()
            self.messenger.reset_global_variables_speak()
            self.messenger.call()
            
        if self.role == "receiver":
            print("receiver host : " + str(self.messenger.host) +  " port: " + str(self.messenger.port )+ " key : " + str(self.messenger.key))
            self.messenger.reset_global_variables_listen()
            self.messenger.reset_global_variables_speak()
            self.messenger.wait_for_call()
              
    # return sender/receiver object
    def retMessenger(self):
        return self.messenger