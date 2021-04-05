from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
import msg_processor
import cryptodriver
import time
import select

class WorkerSignals(QtCore.QObject):
    caller = QtCore.pyqtSignal(str)
    init_recv_call = QtCore.pyqtSignal()


class ListenRequestWorker(QtCore.QThread):
    def __init__(self, client):
        super(ListenRequestWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.signals = WorkerSignals()
        self.client = client
        self.listen_call = True

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        while True:
            print("Starting call listener...")

            response = "header: CHECK_INC_CALL_REQ content: ok [EOM]"  # msg structure smt like header=purpose of msg
            response = self.client.encrypt_content(response)

            self.client.send_msg(response)

            msg = self.client.recv_msg()
            msg = self.client.decrypt_content(msg)

            if msg and msg_processor.get_header_field(msg) == "INC_CALL_REQ":
                caller = msg_processor.get_content_field(msg)
                if caller != "none":
                    self.signals.caller.emit(caller)
                    self.signals.init_recv_call.emit()
                    print(caller + " is trying to call you")

                    #shift bottom to another function
                    # do smt
                    print("accepting call")
                    break



            if not self.listen_call:
                break

            time.sleep(2)
            

    def listen_call_req_start(self):
        self.listen_call = True

    def listen_call_req_pause(self):
        self.listen_call = False

    # return client object
    def retClient(self):
        return self.client

    # insert client object
    def insertClient(self, client):
        self.client = client