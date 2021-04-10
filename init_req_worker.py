from PyQt5 import QtCore


import msg_processor
import cryptodriver
import time


class WorkerSignals(QtCore.QObject):
    start_timer = QtCore.pyqtSignal()
    call_accepted = QtCore.pyqtSignal(str, str)
    reject = QtCore.pyqtSignal()
    timeout = QtCore.pyqtSignal()


class InitRequestWorker(QtCore.QThread):
    def __init__(self, client, call_target):
        super(InitRequestWorker, self).__init__()

        self.signals = WorkerSignals()
        self.client = client
        self.call_target = call_target
        self.listen_call = True

    @QtCore.pyqtSlot()
    def run(self):
        print("calling....")

        response = "header: CALL_REQ content: " + self.call_target + " [EOM]"
        response = self.client.encrypt_content(response)
        self.client.send_msg(response)
        self.signals.start_timer.emit()

        while True:

            # logic for stopping init_req worker (this is when the user cancels the call
            if not self.listen_call:
                response = "header: CALL_REQ_STATUS content: canc [EOM]"
                response = self.client.encrypt_content(response)
                self.client.send_msg(response)
                break

            # send call_req_status to server
            response = "header: CALL_REQ_STATUS content: ok [EOM]"
            response = self.client.encrypt_content(response)
            self.client.send_msg(response)

            # get server response
            msg = self.client.recv_msg()
            msg = self.client.decrypt_content(msg)

            if msg and msg_processor.get_header_field(msg) == "CALL_REQ_RES":
                response = msg_processor.get_content_field(msg)

                # if response is ack means recipient has accepted the call
                if response == "ack":

                    # perform ip exchange and ECDH exchange
                    msg = self.client.recv_msg()
                    msg = self.client.decrypt_content(msg)

                    if msg and msg_processor.get_header_field(msg) == "CALLER_IP":
                        caller_ip = msg_processor.get_content_field(msg)

                        key_obj = cryptodriver.make_edhe_key_obj()
                        own_public_key = cryptodriver.make_edhe_keypair(key_obj)
                        msg = self.client.recv_msg()
                        msg = self.client.decrypt_content(msg)
                        print(msg)

                        if msg_processor.get_header_field(msg) == "CALL_PUB_KEY":

                            recipient_public_key = msg_processor.get_content_field(msg)
                            key_obj = cryptodriver.make_edhe_key_obj()
                            own_public_key = cryptodriver.make_edhe_keypair(key_obj)
                            response = "header: CALL_PUB_KEY content: " + own_public_key + " [EOM]"

                            response = self.client.encrypt_content(response)
                            self.client.send_msg(response)
                            shared_key = cryptodriver.make_edhe_sharedkey(key_obj, recipient_public_key)
                            self.signals.call_accepted.emit(shared_key, caller_ip)
                            print("Shared: key is: " + shared_key)
                            break

                # if response is dec means recipient has declined the call
                elif response == "dec":
                    # go back to contacts page
                    print("dec")
                    self.signals.reject.emit()
                    break

                # if waiting means recipient still has not responded
                elif response == "waiting":
                    # do nth
                    print("waiting")

                # if timeout means call has timeout
                elif response == "timeout":
                    # go back to contacts page
                    self.signals.timeout.emit()
                    print("timeout")
                    break

            time.sleep(1)

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
