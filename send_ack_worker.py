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
    result = QtCore.pyqtSignal()
    call_accepted = QtCore.pyqtSignal(str, str)


class SendAckWorker(QtCore.QThread):
    def __init__(self, client):
        super(SendAckWorker, self).__init__()

        self.signals = WorkerSignals()
        self.client = client

    @QtCore.pyqtSlot()
    def run(self):
        try:
            response = "header: INC_CALL_REQ_RES content: ack [EOM]"  # msg structure smt like header=purpose of msg
            response = self.client.encrypt_content(response)

            self.client.send_msg(response)

            msg = self.client.recv_msg()
            msg = self.client.decrypt_content(msg)

            print(msg)
            if msg and msg_processor.get_header_field(msg) == "CALLER_IP":
                caller_ip = msg_processor.get_content_field(msg)
                print(caller_ip)
                key_obj = cryptodriver.make_edhe_key_obj()
                own_public_key = cryptodriver.make_edhe_keypair(key_obj)

                response = "header: CALL_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                response = self.client.encrypt_content(response)
                self.client.send_msg(response)

                msg = self.client.recv_msg()
                msg = self.client.decrypt_content(msg)
                
                if msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
                    recipient_public_key = msg_processor.get_content_field(msg)
                    shared_key = cryptodriver.make_edhe_sharedkey(key_obj, recipient_public_key)
                    print("Shared: key is: " + shared_key)
                    self.signals.call_accepted.emit(shared_key, caller_ip)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))

        else:
            self.signals.result.emit()  # Return the result of the processing
        finally:
            self.signals.finished.emit()          

    # return client object
    def retClient(self):
        return self.client

    # insert client object
    def insertClient(self, client):
        self.client = client