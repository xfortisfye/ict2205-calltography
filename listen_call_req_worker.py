from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
import msg_processor
import cryptodriver
import time
import select

class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    caller = QtCore.pyqtSignal(str)


class ListenCallReqWorker(QtCore.QThread):
    def __init__(self, client):
        super(ListenCallReqWorker, self).__init__()

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
                    print(caller + " is trying to call you")

                    # do smt
                    print("accepting call")

                    response = "header: INC_CALL_REQ_RES content: ack [EOM]"  # msg structure smt like header=purpose of msg
                    response = self.client.encrypt_content(response)

                    self.client.send_msg(response)

                    msg = self.client.recv_msg()
                    msg = self.client.decrypt_content(msg)


                    print(msg)
                    if msg and msg_processor.get_header_field(msg) == "CALLER_IP":
                        caller_ip = msg_processor.get_content_field(msg)
                        print(caller_ip)


                        key_obj = cryptodriver.make_dhe_key_obj()
                        own_public_key = cryptodriver.make_dhe_keypair(key_obj)


                        response = "header: CALL_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        response = self.client.encrypt_content(response)
                        self.client.send_msg(response)

                        msg = self.client.recv_msg()
                        msg = self.client.decrypt_content(msg)
                        if msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
                            recipient_public_key = msg_processor.get_content_field(msg)
                            shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_public_key)
                            print("Shared: key is: " + shared_key)

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