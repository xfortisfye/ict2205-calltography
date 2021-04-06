from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
import msg_processor
import cryptodriver
import time
import select


class WorkerSignals(QtCore.QObject):
    start_timer = QtCore.pyqtSignal()
    call_accepted = QtCore.pyqtSignal(str, str)
    reject = QtCore.pyqtSignal()
    timeout = QtCore.pyqtSignal()

class InitRequestWorker(QtCore.QThread):
    def __init__(self, client, call_target):
        super(InitRequestWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.signals = WorkerSignals()
        self.client = client
        self.call_target = call_target
        self.listen_call = True

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
            
        print("calling....")

        response = "header: CALL_REQ content: " + self.call_target + " [EOM]"  # msg structure smt like header=purpose of msg
        response = self.client.encrypt_content(response)
        self.client.send_msg(response)
        #self.signals.call_target.emit(self.call_target)  # Return the result of the processing
        self.signals.start_timer.emit()

        while True:


            print(self.listen_call)
            if not self.listen_call:
                response = "header: CALL_REQ_STATUS content: canc [EOM]"  # msg structure smt like header=purpose of msg
                response = self.client.encrypt_content(response)
                self.client.send_msg(response)
                print("SENT!!!")
                time.sleep(1)
                break


            response = "header: CALL_REQ_STATUS content: ok [EOM]"  # msg structure smt like header=purpose of msg
            response = self.client.encrypt_content(response)
            self.client.send_msg(response)


            msg = self.client.recv_msg()
            msg = self.client.decrypt_content(msg)
            if msg and msg_processor.get_header_field(msg) == "CALL_REQ_RES":
                response = msg_processor.get_content_field(msg)
                if response == "ack":
                    print("ack")
                    msg = self.client.recv_msg()
                    msg = self.client.decrypt_content(msg)

                    if msg and msg_processor.get_header_field(msg) == "CALLER_IP":
                        caller_ip = msg_processor.get_content_field(msg)
                        print(caller_ip)

                        key_obj = cryptodriver.make_dhe_key_obj()
                        own_public_key = cryptodriver.make_dhe_keypair(key_obj)

                        msg = self.client.recv_msg()
                        msg = self.client.decrypt_content(msg)
                        print(msg)
                        if msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
                            recipient_public_key = msg_processor.get_content_field(msg)
                            key_obj = cryptodriver.make_dhe_key_obj()
                            own_public_key = cryptodriver.make_dhe_keypair(key_obj)
                            response = "header: CALL_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                            response = self.client.encrypt_content(response)
                            self.client.send_msg(response)
                            shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_public_key)
                            self.signals.call_accepted.emit(shared_key, caller_ip)
                            print("Shared: key is: "+shared_key)
                            break
                if response == "dec":
                    print("dec")
                    self.signals.reject.emit()
                    # HI ANDY DO YOUR MAGIC HERE!!!
                    break
                if response == "waiting":
                    print("waiting")

                if response == "timeout":
                    self.signals.timeout.emit()
                    print("timeout")
                    # HI ANDY DO YOUR MAGIC HERE!!!
                    break


    def init_req_start(self):
        self.listen_call = True

    def init_req_pause(self):
        self.listen_call = False


    # return client object
    def retClient(self):
        return self.client

    # insert client object
    def insertClient(self, client):
        self.client = client

